/**
 * FocusGuard Extension — background.js (Service Worker)
 * 
 * Watches for tab changes and sends the active tab's URL + title
 * to the FocusGuard desktop app via a local HTTP server on port 7890.
 */

const SERVER_URL = 'http://127.0.0.1:7890/tab';

// ── Send tab info to the desktop app ────────────────────────────────────────

async function reportTab(url, title) {
  try {
    await fetch(SERVER_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: url || '', title: title || '' })
    });
  } catch {
    // FocusGuard desktop app is not running — fail silently.
  }
}

async function reportActiveTabInWindow(windowId) {
  try {
    const win = await chrome.windows.get(windowId);
    if (win.type !== 'normal') return; // Ignore popup windows, devtools, etc.

    const tabs = await chrome.tabs.query({ active: true, windowId });
    if (tabs.length > 0) {
      await reportTab(tabs[0].url, tabs[0].title);
    }
  } catch (err) {
    console.warn('[FocusGuard] Could not query tabs:', err);
  }
}

// ── Event listeners ──────────────────────────────────────────────────────────

// User switched tabs within a window
chrome.tabs.onActivated.addListener(async (activeInfo) => {
  try {
    const tab = await chrome.tabs.get(activeInfo.tabId);
    await reportTab(tab.url, tab.title);
  } catch (err) {
    console.warn('[FocusGuard] onActivated error:', err);
  }
});

// A tab's URL or load status changed (page navigation)
chrome.tabs.onUpdated.addListener(async (tabId, changeInfo, tab) => {
  // Only care about URL changes or full page loads on the ACTIVE tab
  if (!changeInfo.url && changeInfo.status !== 'complete') return;

  try {
    const [activeTab] = await chrome.tabs.query({ active: true, lastFocusedWindow: true });
    if (activeTab && activeTab.id === tabId) {
      await reportTab(tab.url, tab.title);
    }
  } catch (err) {
    console.warn('[FocusGuard] onUpdated error:', err);
  }
});

// Browser window focus changed (user alt-tabbed to/from browser)
chrome.windows.onFocusChanged.addListener(async (windowId) => {
  if (windowId === chrome.windows.WINDOW_ID_NONE) {
    // Browser lost focus entirely — clear the active tab URL
    await reportTab('', '');
  } else {
    // Browser regained focus — report which tab is active
    await reportActiveTabInWindow(windowId);
  }
});

// A tab was removed (closed) — re-report the new active tab
chrome.tabs.onRemoved.addListener(async (tabId, removeInfo) => {
  if (!removeInfo.isWindowClosing) {
    await reportActiveTabInWindow(removeInfo.windowId);
  }
});

console.log('[FocusGuard] Extension background worker started.');
