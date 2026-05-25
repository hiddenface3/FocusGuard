# FocusGuard
**A Premium Desktop Distraction Blocker & Focus Tracker**

FocusGuard is a Python-based desktop application (built with PyQt6) designed to monitor user activity, track time spent on productive vs. distracting applications, and provide randomized spoken audio reminders using advanced Text-to-Speech (TTS). It includes a dedicated browser extension to accurately track website URLs.

---

## 🎯 Core Features & Architecture

### 1. Advanced Activity Monitoring (`monitor.py`)
- **Foreground Detection**: Uses Windows APIs (`win32gui`, `psutil`) to poll the user's active window every second.
- **Process & Title Matching**: Detects desktop apps by their `.exe` process name or window title.
- **Good vs. Bad Categorization**: Users can define specific keywords for "Good Apps" (Productivity) and "Bad Apps" (Distractions). 
- **Timer Countdown**: When a monitored app is in focus, a background countdown timer begins. If the user stays on the app past the configured interval (e.g., 2 minutes), a TTS reminder is triggered.

### 2. Browser Extension Integration (`browser_server.py`)
- **Local HTTP Server**: Runs a lightweight `aiohttp` server in a background thread on `http://127.0.0.1:7890`.
- **Extension Sync**: A custom Microsoft Edge extension tracks the active browser tab and sends a `POST /tab` request with the exact URL and page title to the local server.
- **Granular Blocking**: This allows FocusGuard to differentiate between `youtube.com` (Distraction) and `github.com` (Productive) even though both run under the same `msedge.exe` process.

### 3. Dynamic Text-to-Speech Engine (`tts_engine.py`)
- **Edge-TTS Integration**: Uses Microsoft's high-quality neural voices.
- **Intelligent Caching**: Audio files are generated once, hashed, and cached locally as `.mp3` files. This ensures instant playback without network delays.
- **Randomized Phrases**: Users can input multiple phrases for both Good and Bad categories. The app randomly selects a phrase to speak when the reminder triggers (e.g., a harsh scolding for YouTube, or encouraging words for VS Code).

### 4. Real-time Analytics (`analytics.py`)
- **Time Tracking**: Logs every second spent on tracked Good/Bad apps into a persistent local `analytics.json` file, organized by date.
- **Data Visualization**: The data is aggregated to show exactly how many minutes/hours the user spent on specific apps today.

---

## 🎨 UI/UX Structure (For Design Reference)

The user interface is built using PyQt6, currently utilizing a dark theme with purple/blue gradients and glassmorphic card elements. 

### Main Window
The main window is constrained to a fixed width (~580px) and operates as a sleek dashboard with a Top Tab Navigation.

#### Tab 1: ⚙️ Settings
- **Header**: App title, brief description, and a gradient logo.
- **Status Card**:
  - Live status text (e.g., `✅ Active - No distractions` or `🔴 Watching - YouTube`).
  - Animated Toggle Switch to Pause/Resume protection.
  - Live countdown showing time remaining until the next spoken reminder.
- **Live Detection Feed**:
  - A real-time debugging panel that updates every second to show the user exactly what process, window title, and matched rule the app currently sees.
- **Good Apps & Bad Apps Lists**:
  - Two distinct sections containing a list of configured keywords.
  - Each list item shows an icon (Globe for browser, Desktop for local app), the display name, the matched keywords, and a prominent `✖` Delete button.
  - **Phrase Input**: Below each list is a multi-line text area where users can type various phrases (one per line) for the TTS engine to randomly choose from.
- **Reminder & Voice Settings**:
  - A numeric spin-box to set the interval (in minutes).
  - A dropdown menu to select the Neural Voice (e.g., Aria, Guy, Jenny).
  - A "Test Voice" button and a primary "Save Settings" gradient button.

#### Tab 2: 📊 Analytics
- **Today's Stats Card**:
  - A custom-drawn PyQt chart (`AnalyticsChart`) that visualizes today's tracked time.
  - Lists the App Name on the left, the total time formatted (e.g., `1h 20m`) on the right.
  - Displays a horizontal progress bar. Green bars represent Productive time, Red bars represent Distraction time.

### Modals & System Tray
- **Add App Dialog**: A popup modal with inputs for Display Name, Detection Type (Browser Tab vs. Process), and Keywords.
- **System Tray Icon**: FocusGuard runs silently in the system tray. The tray icon shows tooltips of the current active distraction and allows the user to quickly pause protection or open the settings dashboard via a right-click context menu.

---

## 🚀 Design Goals for "Stitch AI"
When redesigning this app, focus on:
1. **Premium Aesthetics**: High-end modern design, vibrant tailored colors, smooth gradients, and glassmorphism. Avoid flat, generic looks.
2. **Clear Hierarchy**: The distinction between "Good" (Productive/Green) and "Bad" (Distracting/Red) elements should be visually obvious but harmonious.
3. **Data Visualization**: The Analytics chart needs to look stunning and readable.
4. **Interactivity**: Buttons, toggles, and list items should have clear hover and active states.
