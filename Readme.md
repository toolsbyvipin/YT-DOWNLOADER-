🎬 YT-DL PRO - HACKER EDITION
<p align="center"> <img src="https://img.shields.io/badge/Version-3.0-red?style=for-the-badge&logo=github" alt="Version"/> <img src="https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python" alt="Python"/> <img src="https://img.shields.io/badge/Platform-All%20OS-green?style=for-the-badge" alt="Platform"/> <img src="https://img.shields.io/badge/Developer-VIP_IN-brightgreen?style=for-the-badge" alt="Developer"/> </p><p align="center"> <img src="https://readme-typing-svg.herokuapp.com?font=Fira+Code&weight=700&size=24&pause=1000&color=00FF00&center=true&vCenter=true&random=false&width=600&height=60&lines=🎬+YT-DL+PRO+💀;⚡+Download+Anything;🔓+Break+the+Limits" alt="Typing SVG"/> </p>
📸 User Interface
<p align="center"> <img src="https://github.com/toolsbyvipin/YT-DOWNLOADER-/blob/6a0182e1c1b7e9bbadf70a6dbb90c718deba0464/Screenshot%20(540).png" alt="YT-DL PRO UI" width="800"/> </p><p align="center"> <i>💀 Cyberpunk-style terminal with real-time download matrix</i> </p>

---

## 🔥 What Makes This Different?

- 🎬 8K/4K Downloads - Download any resolution including 8K
- 📦 Batch Processing - Multiple URLs at once
- 🔊 Audio Extraction - High-quality audio (FLAC, MP3, M4A)
- 📝 Subtitle Download - Auto-subtitles in any language
- 🎯 Playlist Master - Full playlist download with metadata
- 🔐 Age-Restricted - Bypass age restrictions
- 📁 Smart Organize - Auto-sort by channel, date, or playlist
- ⚡ Speed Boost - Multi-threaded downloading

---

## 🚀 One-Line Installation

### Windows
powershell -Command "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/toolsbyvipin/YT-DOWNLOADER-/main/install.bat' -OutFile install.bat" && install.bat

### Linux
bash <(curl -s https://raw.githubusercontent.com/toolsbyvipin/YT-DOWNLOADER-/main/install.sh)

### Termux (Android)
pkg update && pkg upgrade -y && pkg install python git ffmpeg -y && git clone https://github.com/toolsbyvipin/YT-DOWNLOADER-.git && cd YT-DOWNLOADER- && pip install -r requirements.txt && python ytdl_pro.py

---

## 📦 Manual Installation

### 1. Clone Repository
git clone https://github.com/toolsbyvipin/YT-DOWNLOADER-.git
cd YT-DOWNLOADER-

### 2. Install Dependencies
pip install -r requirements.txt

### 3. Install FFmpeg (Required for merging)

#### Windows
winget install ffmpeg

#### Linux (Ubuntu/Debian)
sudo apt update && sudo apt install ffmpeg -y

#### Linux (Arch)
sudo pacman -S ffmpeg

#### Termux
pkg install ffmpeg -y

### 4. Run
python ytdl_pro.py

---

## 🎯 Quick Start

git clone https://github.com/toolsbyvipin/YT-DOWNLOADER-.git
cd YT-DOWNLOADER-
pip install -r requirements.txt
python ytdl_pro.py

---

## 🎬 Quality Options

1. 8K/4K - MP4/WebM - Maximum quality
2. 1080p - MP4 - High quality
3. 720p - MP4 - Balanced
4. 480p - MP4 - Small size
5. Audio MP3 - MP3 - Music
6. Audio FLAC - FLAC - Lossless
7. Custom - User defined - Advanced

---

## 📁 Folder Structure

D:/YT_Downloads/
├── Videos/
│   ├── Channel_Name/
│   ├── Playlist_Name/
│   └── Single_Videos/
├── Audio/
└── Subtitles/

---

## 💀 Cyberpunk UI Elements

🎬 Video Mode
💀 Hacker Mode
⚡ Speed Mode
🔓 Unlocked
🛸 Matrix Mode
🔥 Downloading

---

## ⚠️ Warnings

🔴 DO NOT GO OFFLINE DURING DOWNLOAD
🔴 DO NOT CLOSE LAPTOP LID
🔴 DO NOT PUT COMPUTER TO SLEEP
🔴 STAY IN THE MATRIX

---

## 🛠️ Requirements

### Python Packages
yt-dlp>=2023.10.13
rich>=13.7.0
requests>=2.28.0

### System Requirements
- Python 3.8 or higher
- FFmpeg (for video/audio merging)
- 5GB+ free space (for 4K/8K)
- D: Drive or custom directory

---

## 📱 Termux Setup

pkg update && pkg upgrade -y
pkg install python ffmpeg git -y
git clone https://github.com/toolsbyvipin/YT-DOWNLOADER-.git
cd YT-DOWNLOADER-
pip install -r requirements.txt
python ytdl_pro.py

---

## 🔥 Advanced Features

- Resume Support: Continue interrupted downloads
- Cookie Support: Access restricted content
- Proxy Support: Use with VPN/proxy
- Metadata: Preserve all video metadata
- Thumbnails: Download video thumbnails
- Subtitles: Auto-generate or download
- Playlist: Full playlist with index

---

## 📜 License

MIT License - see LICENSE file.

---

## 🤝 Contributing

1. Fork: git checkout -b feature/Amazing
2. Commit: git commit -m 'Add feature'
3. Push: git push origin feature/Amazing
4. PR: Open Pull Request

---

## 📞 Contact

Developer: VIP_IN
GitHub: @toolsbyvipin
Version: 3.0

---

## ⭐ Support

⭐ this repo if you find it useful!

---

## 🔄 Version History

Version 3.0 | 2026 | Cyberpunk UI, 8K support, Batch processing
Version 2.0 | 2025 | Added playlist support, Subtitles
Version 1.0 | 2025 | Initial release

---

## 📄 Additional Files

### requirements.txt
yt-dlp>=2023.10.13
rich>=13.7.0
requests>=2.28.0

### install.sh (Linux)
#!/bin/bash
echo "🎬 Installing YT-DL PRO..."

if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found!"
    exit 1
fi

if [ -d "YT-DOWNLOADER-" ]; then
    cd YT-DOWNLOADER-
    git pull
else
    git clone https://github.com/toolsbyvipin/YT-DOWNLOADER-.git
    cd YT-DOWNLOADER-
fi

if command -v apt &> /dev/null; then
    sudo apt update && sudo apt install ffmpeg -y
elif command -v pacman &> /dev/null; then
    sudo pacman -S ffmpeg
fi

pip3 install -r requirements.txt
echo "✅ Installation complete!"

### install.bat (Windows)
@echo off
echo 🎬 Installing YT-DL PRO...

python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found!
    exit /b 1
)

if exist "YT-DOWNLOADER-" (
    cd YT-DOWNLOADER-
    git pull
) else (
    git clone https://github.com/toolsbyvipin/YT-DOWNLOADER-.git
    cd YT-DOWNLOADER-
)

winget install ffmpeg
pip install -r requirements.txt
echo ✅ Installation complete!
pause

---

🎬 Hack the Video!
Made with 🔥 by VIP_IN
