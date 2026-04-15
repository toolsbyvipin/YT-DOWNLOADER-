# 🎬 YT Playlist Downloader - 🔥

Download complete YouTube playlists in **best quality** for offline viewing.

## 📥 Installation

### 1. Clone the repository

## FOR LINUX 

```bash
git clone https://github.com/toolsbyvipin/YT-DOWNLOADER-.git
cd YT-DOWNLOADER-
pip install -r requirements.txt
sudo apt update
sudo pacman -S ffmpeg
python Ytply.py

```
## FOR WINDOWS 

1) FIRST INSTALL PYTHON FOR WINDOWS

     Download from : https://www.python.org/downloads/

2) 🔧 FFMPEG REQUIRED FOR BEST QUALITY (OPTIONAL)  
Windows:
```
winget install --id Gyan.FFmpeg -e --source winget
```

4) THEN EXECUTE THESE COMMANDS

```bash
python -m pip install yt-dlp rich

Invoke-WebRequest -Uri "https://github.com/toolsbyvipin/YT-DOWNLOADER-/archive/refs/heads/main.zip" -OutFile "$env:USERPROFILE\Downloads\YT-DOWNLOADER.zip"
Expand-Archive -Path "$env:USERPROFILE\Downloads\YT-DOWNLOADER.zip" -DestinationPath "$env:USERPROFILE\Downloads\" -Force
cd Downloads
cd YT-DOWNLOADER--main
python Ytply.py
```

NEXT TIME COMMAND 

``` 
powershell -Command "pip install yt-dlp rich; python Ytply.py" 

```
DEVELOPER 

```
VIPIN
```
