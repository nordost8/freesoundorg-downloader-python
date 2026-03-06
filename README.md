# Freesound.org Downloader

A modern Freesound.org downloader and API client with native browser-based authentication. No API token required — just log in once securely via your browser and gain programmatic access to Freesound.org audio samples responsibly.

## Overview

This open-source Python framework simplifies interaction with the Freesound.org API for educational and personal research. It uses secure browser integration for authentication, keeping credentials private. No OAuth token or API key needed—authentication happens via your browser session.

You are free to modify this code or integrate it into your own automation workflows for Freesound.org.

**Note:** For personal, non-commercial use only, respecting Freesound's terms and licenses.

## Key Features

- ✅ Secure auth via default browser (no API token required)
- ✅ No extra drivers or Selenium needed
- ✅ Session saving for reuse
- ✅ API support with delays for fair use
- ✅ Cross-platform
- ✅ Interactive console with command history
- ✅ Bulk download and audio sample access (planned)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/nordost8/freesoundorg-downloader-python.git
   cd freesoundorg-downloader-python
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

   Required packages:
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
   - Browser will open automatically
   - Log in to Freesound.org in the browser window
   - Script detects successful login and closes browser
   - Session is saved for future use

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

## License

MIT License - see LICENSE file.

## Search Keywords

To help with discovery: freesound downloader, python freesound client, freesound api python, bulk audio downloader, freesound samples scraper, nodriver authentication, cookie-based freesound access, no token freesound tool.
