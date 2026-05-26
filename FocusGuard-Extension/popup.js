/**
 * FocusGuard Extension — popup.js
 * Shows connection status and current active tab info.
 */

const SERVER_URL   = 'http://127.0.0.1:7890';
const connDot      = document.getElementById('conn-dot');
const connText     = document.getElementById('conn-text');
const urlBox       = document.getElementById('url-box');
const matchBadge   = document.getElementById('match-badge');

// ── Helpers ──────────────────────────────────────────────────────────────────

function setConnected(ok) {
  if (ok) {
    connDot.className   = 'dot green';
    connText.className  = 'status-text green';
    connText.textContent = '✅  Connected to FocusGuard';
  } else {
    connDot.className   = 'dot red';
    connText.className  = 'status-text red';
    connText.textContent = '❌  Desktop app not running';
  }
}

function showUrl(url, title) {
  if (!url) {
    urlBox.textContent  = 'Browser not in focus';
    urlBox.className    = 'url-box empty';
    matchBadge.textContent = '–';
    matchBadge.className   = 'match-badge no-focus';
    return;
  }

  urlBox.textContent = url;
  urlBox.className   = 'url-box';
  matchBadge.textContent = '🟢  Safe — not a blocked site';
  matchBadge.className   = 'match-badge safe';
}

function showBlocked(url, appName) {
  urlBox.textContent = url;
  urlBox.className   = 'url-box blocked';
  matchBadge.textContent = `🔴  Blocked: ${appName}`;
  matchBadge.className   = 'match-badge blocked';
}

// ── Check connection by pinging the server ────────────────────────────────────

async function checkConnection() {
  try {
    const resp = await fetch(SERVER_URL + '/status', { method: 'GET' });
    if (resp.ok) {
      const data = await resp.json();
      setConnected(true);
      if (data.current_url) {
        if (data.matched_app) {
          showBlocked(data.current_url, data.matched_app);
        } else {
          showUrl(data.current_url, data.current_title);
        }
      } else {
        showUrl('', '');
      }
    } else {
      setConnected(false);
    }
  } catch {
    setConnected(false);
    showUrl('', '');
  }
}

// ── Get current active tab URL and show it ────────────────────────────────────

async function showActiveTab() {
  // Only use this as a fallback if the server didn't already give us the info
  if (urlBox.textContent && urlBox.textContent !== 'Browser not in focus' && urlBox.textContent !== 'Checking...') {
      return;
  }
  try {
    const [tab] = await chrome.tabs.query({ active: true, lastFocusedWindow: true });
    if (tab) {
      showUrl(tab.url, tab.title);
    }
  } catch (err) {
    console.warn('[FocusGuard popup]', err);
  }
}

// ── Init ──────────────────────────────────────────────────────────────────────

(async () => {
  // First update UI with local tab info, then override with server status
  try {
    const [tab] = await chrome.tabs.query({ active: true, lastFocusedWindow: true });
    if (tab) {
      showUrl(tab.url, tab.title);
    }
  } catch(e) {}
  
  await checkConnection();
})();
