"""
browser_server.py — FocusGuard

Tiny aiohttp HTTP server that receives active tab URL updates from the
FocusGuard browser extension. Runs on http://127.0.0.1:7890

Endpoints:
  POST /tab     — Extension sends { url, title } on every tab change
  GET  /status  — Popup polls this to check connection + current state
"""

import asyncio
import json
import threading
from typing import Callable

from aiohttp import web

PORT = 7890

_CORS = {
    "Access-Control-Allow-Origin":  "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
}


class BrowserTabServer:
    """
    Thread-safe local HTTP server.
    The extension POSTs tab info here; the monitor reads .current_url.
    """

    def __init__(self, port: int = PORT):
        self.port = port
        self._current_url    = ""
        self._current_title  = ""
        self._matched_app    = ""        # set externally by monitor
        self._lock           = threading.Lock()
        self._loop: asyncio.AbstractEventLoop | None = None
        self._thread: threading.Thread | None = None

    # ── Thread-safe properties ──────────────────────────────────────────────

    @property
    def current_url(self) -> str:
        with self._lock:
            return self._current_url

    @property
    def current_title(self) -> str:
        with self._lock:
            return self._current_title

    def set_matched_app(self, app_name: str):
        """Called by monitor to reflect what app is currently matched."""
        with self._lock:
            self._matched_app = app_name

    # ── HTTP handlers ───────────────────────────────────────────────────────

    async def _options(self, req: web.Request) -> web.Response:
        return web.Response(headers=_CORS)

    async def _post_tab(self, req: web.Request) -> web.Response:
        """Extension → server: update active tab URL."""
        try:
            data  = await req.json()
            url   = (data.get("url",   "") or "").strip()
            title = (data.get("title", "") or "").strip()
            with self._lock:
                self._current_url   = url
                self._current_title = title
                if not url:               # browser lost focus
                    self._matched_app = ""
        except Exception as e:
            print(f"[BrowserServer] Parse error: {e}")

        return web.Response(
            text='{"ok":true}',
            content_type="application/json",
            headers=_CORS,
        )

    async def _get_status(self, req: web.Request) -> web.Response:
        """Popup → server: get current state."""
        with self._lock:
            payload = {
                "ok":          True,
                "current_url":   self._current_url,
                "current_title": self._current_title,
                "matched_app":   self._matched_app,
            }
        return web.Response(
            text=json.dumps(payload),
            content_type="application/json",
            headers=_CORS,
        )

    # ── Lifecycle ───────────────────────────────────────────────────────────

    def start(self):
        """Start the server in a background daemon thread."""
        def _run():
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)

            app = web.Application()
            app.router.add_options("/tab",    self._options)
            app.router.add_options("/status", self._options)
            app.router.add_post(   "/tab",    self._post_tab)
            app.router.add_get(    "/status", self._get_status)

            runner = web.AppRunner(app, access_log=None)
            self._loop.run_until_complete(runner.setup())
            site = web.TCPSite(runner, "127.0.0.1", self.port, reuse_address=True)
            self._loop.run_until_complete(site.start())
            print(f"[BrowserServer] Listening on http://127.0.0.1:{self.port}")
            self._loop.run_forever()

        self._thread = threading.Thread(
            target=_run, daemon=True, name="FocusGuard-BrowserServer"
        )
        self._thread.start()

    def stop(self):
        if self._loop and self._loop.is_running():
            self._loop.call_soon_threadsafe(self._loop.stop)
