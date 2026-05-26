"""
TTS Engine — uses Microsoft Edge TTS (edge-tts) with local MP3 caching.
Only re-generates audio when the phrase or voice changes (hash-based cache).
"""

import asyncio
import hashlib
import os
import threading

import pygame

CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tts_cache")
os.makedirs(CACHE_DIR, exist_ok=True)


def _get_cache_path(phrase: str, voice: str) -> str:
    key = hashlib.md5(f"{phrase}|||{voice}".encode("utf-8")).hexdigest()
    return os.path.join(CACHE_DIR, f"{key}.mp3")


def _generate_tts_sync(phrase: str, voice: str, output_path: str):
    """Blocking TTS generation — runs edge-tts in a fresh event loop."""
    import edge_tts

    async def _gen():
        communicate = edge_tts.Communicate(phrase, voice)
        await communicate.save(output_path)

    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(_gen())
    finally:
        loop.close()


class TTSEngine:
    """Thread-safe TTS engine with caching and pygame audio playback."""

    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.mixer.init()
        self._lock = threading.Lock()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def prepare(self, phrase: str, voice: str = "en-US-AriaNeural",
                on_done=None):
        """
        Pre-generate (and cache) TTS for a phrase.
        Non-blocking when on_done callback is provided.
        """
        def _work():
            path = _get_cache_path(phrase, voice)
            if not os.path.exists(path):
                try:
                    _generate_tts_sync(phrase, voice, path)
                except Exception as e:
                    print(f"[TTS] Generation error: {e}")
                    if on_done:
                        on_done(False)
                    return
            if on_done:
                on_done(True)

        t = threading.Thread(target=_work, daemon=True)
        t.start()
        if on_done is None:
            t.join()

    def prepare_many(self, phrases: list[str], voice: str = "en-US-AriaNeural"):
        """Pre-generates multiple phrases asynchronously."""
        def _work():
            for p in phrases:
                if not p.strip(): continue
                path = _get_cache_path(p, voice)
                if not os.path.exists(path):
                    try:
                        _generate_tts_sync(p, voice, path)
                    except:
                        pass
        threading.Thread(target=_work, daemon=True).start()

    def speak(self, phrase: str, voice: str = "en-US-AriaNeural"):
        """Speak phrase. Generates if not cached. Always non-blocking."""
        def _work():
            path = _get_cache_path(phrase, voice)
            if not os.path.exists(path):
                try:
                    _generate_tts_sync(phrase, voice, path)
                except Exception as e:
                    print(f"[TTS] Generation error: {e}")
                    return
            with self._lock:
                try:
                    if pygame.mixer.music.get_busy():
                        pygame.mixer.music.stop()
                    pygame.mixer.music.load(path)
                    pygame.mixer.music.play()
                except Exception as e:
                    print(f"[TTS] Playback error: {e}")

        threading.Thread(target=_work, daemon=True).start()

    def is_speaking(self) -> bool:
        try:
            return pygame.mixer.music.get_busy()
        except Exception:
            return False

    def stop(self):
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass

    def cleanup(self):
        try:
            pygame.mixer.quit()
        except Exception:
            pass
