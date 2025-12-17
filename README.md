# 🎬 Video Downloader Chrome Extension

A powerful Chrome extension that allows you to download videos from YouTube, Instagram, and other supported platforms directly to your computer. Features real-time download progress tracking via WebSocket connection.

![Chrome Extension](https://img.shields.io/badge/Chrome-Extension-green?logo=googlechrome)
![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python)
![License](https://img.shields.io/badge/License-MIT-yellow)

## ✨ Features

- 🔗 **One-click downloads** - Auto-detects video URL from current tab
- 📊 **Real-time progress** - Live download progress with speed and ETA
- 🌐 **Multi-platform support** - YouTube, Instagram, Twitter, and 1000+ sites via yt-dlp
- 📁 **Smart saving** - Downloads directly to your ~/Downloads folder
- ⚡ **WebSocket-powered** - Fast, responsive progress updates
- 🎯 **In-page buttons** - Download buttons appear directly on video elements

## 🏗️ Architecture

```
┌─────────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Chrome Extension   │────▶│  FastAPI Backend │────▶│     yt-dlp      │
│  (popup.js)         │ WS  │  (Python)        │     │  (downloader)   │
└─────────────────────┘     └──────────────────┘     └─────────────────┘
```

## 📋 Prerequisites

- **Python 3.8+**
- **Google Chrome** browser
- **FFmpeg** (for video merging) - `brew install ffmpeg` on macOS

## 🚀 Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/p1-patidar/VideoDownloaderExtension.git
cd VideoDownloaderExtension
```

### 2. Set up Python environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

### 3. Start the backend server

```bash
# Option 1: Direct command
python backend/main.py

# Option 2: Using the convenience script
./start_server.command
```

The server will start at `http://127.0.0.1:8000`

### 4. Install the Chrome extension

1. Open Chrome and navigate to `chrome://extensions/`
2. Enable **Developer mode** (toggle in top-right)
3. Click **Load unpacked**
4. Select the `VideoDownloaderExtension` folder

## 📖 Usage

1. **Start the server** - Run the backend server first
2. **Open any video page** - Navigate to YouTube, Instagram, etc.
3. **Click the extension icon** - The popup shows the current page URL
4. **Hit Download** - Watch the real-time progress!

The extension will:
- Auto-fill the current page URL
- Connect via WebSocket for live progress
- Download the best quality video
- Save to your `~/Downloads` folder

## 📁 Project Structure

```
VideoDownloaderExtension/
├── manifest.json          # Chrome extension manifest (v3)
├── popup.html             # Extension popup UI
├── popup.js               # Popup logic & WebSocket handling
├── style.css              # Popup styling
├── content.js             # In-page video detection & download buttons
├── background.js          # Service worker for messaging
├── backend/
│   ├── main.py            # FastAPI server with WebSocket
│   ├── requirements.txt   # Python dependencies
│   ├── native_host.py     # Chrome native messaging host
│   └── install_host.py    # Native host installer
└── start_server.command   # macOS convenience script
```

## ⚙️ API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Check server status |
| `/download` | POST | Start video download (REST) |
| `/ws` | WebSocket | Real-time download with progress |
| `/open-folder` | GET | Open downloads folder in Finder |

## 🔧 Technologies

- **Frontend**: Chrome Extension APIs (Manifest V3)
- **Backend**: FastAPI + Uvicorn
- **Downloader**: yt-dlp (supports 1000+ sites)
- **Communication**: WebSocket for real-time updates

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## ⚠️ Disclaimer

This tool is for personal use only. Please respect copyright laws and the terms of service of the platforms you download from. Only download content you have the right to download.

---

**Made with ❤️ by [p1-patidar](https://github.com/p1-patidar)**
