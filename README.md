# Freesound.org Downloader

A modern Freesound.org downloader and API client with native browser-based authentication. No API token required — just log in once securely via your browser and gain programmatic access to Freesound.org audio samples responsibly.

## Overview

This open-source Python framework simplifies interaction with the Freesound.org API for educational and personal research. It uses secure browser integration for authentication, keeping credentials private. No OAuth token or API key needed—authentication happens via your browser session.

You are free to modify this code or integrate it into your own automation workflows for Freesound.org.

**Note:** For personal, non-commercial use only, respecting Freesound's terms and licenses.

## Key Features

- ✅ Secure auth via Chromium-based browser (Chrome, Edge, Brave, Opera) - no API token required
- ✅ Automatic browser detection - uses Chrome if available, falls back to Edge/Brave/Opera
- ✅ No extra drivers or Selenium needed
- ✅ Session saving for reuse
- ✅ API support with delays for fair use
- ✅ Cross-platform
- ✅ Interactive console with command history
- ✅ Bulk download and audio sample access (planned)

## Installation

### Option 1: Quick Install (Recommended)

1. Clone the repository:
   ```bash
   git clone https://github.com/nordost8/freesoundorg-downloader-python.git
   cd freesoundorg-downloader-python
   ```

2. Run the install script:
   ```bash
   ./install.sh
   ```

### Option 2: Manual Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/nordost8/freesoundorg-downloader-python.git
   cd freesoundorg-downloader-python
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Option 3: Install as Package (Advanced)

```bash
pip install -e .
```

This allows you to run `freesound-downloader` from anywhere.

**Required packages:**
- `nodriver` - Browser automation
- `prompt-toolkit` - Interactive console
- `rich` - Beautiful terminal output

## Usage

### Quick Start

1. **Run the interactive console:**
   ```bash
   python freesound_downloader.py
   ```

2. **First-time authentication:**
   - Chromium-based browser will open automatically (Chrome, Edge, Brave, or Opera)
   - Script automatically detects and uses the first available Chromium-based browser
   - Priority order: Chrome → Edge → Brave → Opera → Chromium
   - Log in to Freesound.org in the browser window
   - Script detects successful login and closes browser
   - Session is saved for future use
   
   **Note:** Requires a Chromium-based browser (Chrome, Edge, Brave, Opera, or Chromium). Firefox is not supported.

3. **Find a sound on Freesound.org:**
   - Open [freesound.org](https://freesound.org) in your browser
   - Browse or search for sounds
   - Click on a sound you want to download
   - Copy the URL from your browser's address bar

4. **Download the sound:**
   - In the interactive console, paste the URL or enter the sound ID
   - Example URL: `https://freesound.org/people/troyane/sounds/233770/`
   - Example ID: `233770`
   - Press Enter to download

### Interactive Console Commands

- **URL or Sound ID** - Download a sound
  - Example: `https://freesound.org/people/user/sounds/12345/`
  - Example: `12345`
- **`help`** - Show help message
- **`exit`** or **`quit`** - Exit the console
- **`clear`** - Clear the screen

### Custom Output Directory

```bash
python freesound_downloader.py --output ./my_sounds
```

## How It Works

1. Checks for saved session cookies
2. If invalid or missing, opens browser for login
3. Captures cookies securely from browser session
4. Saves session for future use
5. Uses cookies for API calls with appropriate delays
6. Downloads sounds to specified directory

## Important Disclaimer

This is an independent tool, not affiliated with Freesound.org. For education/research purposes only. Please comply with Freesound's terms of service and respect content licenses. No warranty provided. Use responsibly.

## Future Plans

- 🔄 **Bulk download** - Download multiple sounds at once (not yet implemented)
- 📦 **Sound pack support** - Download entire sound packs
- 🔍 **Search integration** - Search and download directly from console
- 📊 **Download queue** - Manage multiple downloads with progress tracking

## Tested Systems

This tool has been officially tested on the following systems:

- ✅ **Ubuntu 24.04.3 LTS (Noble)** - Python 3.12.3, Linux kernel 6.17.0-14-generic
- ✅ Cross-platform support (Windows, macOS, Linux) - should work on any system with Python 3.8+

## AI Agent Friendly (Claude Code, Cursor...)

This repository is optimized for AI coding assistants with clean code structure and comprehensive documentation.

**Example prompt for your AI agent:**

```
Привіт Агенте, склонуй і запусти для мене це рішення:
https://github.com/nordost8/freesoundorg-downloader-python
```

## License

MIT License - see LICENSE file.

## Search Keywords

To help with discovery: freesound org login bypass python, freesound org userbot, freesound bulk downloader, freesound automatic download, freesound high quality downloader, python freesound open-source api client, freesound script, freesound.org downloader without api key, freesound automate, freesound org scraper without api key, freesound python client, freesound opensource client, freesound download no api key

---

[![Telegram](https://img.icons8.com/color/48/000000/telegram-app.png)](https://t.me/nordost8)
