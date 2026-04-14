# 🎬 YT Playlist Downloader - 🔥

Download complete YouTube playlists in **best quality** for offline viewing.

## 📥 Installation

### 1. Clone the repository

FOR LINUX 

```bash
git clone https://github.com/toolsbyvipin/YT-DOWNLOADER-.git
cd YT-DOWNLOADER-
pip install -r requirements.txt
sudo apt update
sudo pacman -S ffmpeg
python Ytply.py

```
FOR WINDOWS 

```bash
powershell -Command "Set-ExecutionPolicy Bypass -Scope Process -Force; $ffmpegPath='C:\ffmpeg'; if (!(Test-Path $ffmpegPath)) { Write-Host '📥 Downloading FFmpeg...' -ForegroundColor Yellow; Invoke-WebRequest -Uri 'https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip' -OutFile '$env:TEMP\ffmpeg.zip'; Expand-Archive -Path '$env:TEMP\ffmpeg.zip' -DestinationPath 'C:\' -Force; Move-Item 'C:\ffmpeg-*' 'C:\ffmpeg' -Force; Remove-Item '$env:TEMP\ffmpeg.zip' }; $env:Path += ';C:\ffmpeg\bin'; [Environment]::SetEnvironmentVariable('Path', $env:Path, 'User'); pip install yt-dlp rich; python Ytply.py"
git clone https://github.com/toolsbyvipin/YT-DOWNLOADER-.git
cd YT-DOWNLOADER-
cd YT-DOWNLOADER-
 && pip install -r requirements.txt && python Ytply.py
 
 ```
NEXT TIME COMMAND 

``` 
powershell -Command "pip install yt-dlp rich; python Ytply.py" 

```
DEVELOPER 

```
VIPIN
```
