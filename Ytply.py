#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════╗
║  YT PLAYLIST DOWNLOADER 🔥                                                ║
║  Download complete YouTube playlists in best quality for offline viewing  ║
║  Saves to: D:\YT_Playlists\Playlist_Name\                                ║
╚═══════════════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import json
import time
import re
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any

# ===== DEPENDENCY CHECK =====
def check_dependencies():
    missing = []
    try:
        import yt_dlp
    except ImportError:
        missing.append("yt-dlp")
    
    try:
        from rich.console import Console
        from rich.table import Table
        from rich.panel import Panel
        from rich.prompt import Prompt, Confirm
        from rich import print as rprint
    except ImportError:
        missing.append("rich")
    
    if missing:
        print(f"Installing missing dependencies: {', '.join(missing)}")
        os.system(f"pip install {' '.join(missing)}")
        print("Restart the script after installation.")
        sys.exit(0)

check_dependencies()

import yt_dlp
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich import print as rprint

console = Console()

# ===== COLOR THEME =====
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'

# ===== QUALITY PRESETS =====
QUALITY_PRESETS = {
    "1": {
        "name": "🎬 BEST QUALITY (4K/1080p)",
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "description": "Highest available video + audio (4K/1080p where available)"
    },
    "2": {
        "name": "📱 1080p HIGH QUALITY",
        "format": "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]/best",
        "description": "1080p maximum, good balance of quality and size"
    },
    "3": {
        "name": "📱 720p MEDIUM QUALITY",
        "format": "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best",
        "description": "720p, smaller file size"
    },
    "4": {
        "name": "🎵 AUDIO ONLY (MP3)",
        "format": "bestaudio/best",
        "description": "Extract audio as MP3",
        "postprocessors": [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320',
        }]
    },
    "5": {
        "name": "📦 CUSTOM QUALITY",
        "format": None,
        "description": "Manually specify format code"
    }
}

# ===== YT PLAYLIST DOWNLOADER =====
class YTPlaylistDownloader:
    def __init__(self):
        # Force save to D: drive
        self.download_dir = Path("D:/YT_Playlists")
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.history_file = self.download_dir / "download_history.json"
        self.download_history = self.load_history()
        self.cancelled = False
        self.current_video = ""
        self.downloaded_count = 0
        self.failed_count = 0
        self.total_videos = 0
    
    def load_history(self) -> Dict:
        """Load download history"""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_history(self):
        """Save download history"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.download_history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            console.print(f"[red]⚠️ Could not save history: {e}[/red]")
    
    def print_banner(self):
        """Display the banner"""
        banner = f"""
{Colors.RED}{Colors.BOLD}╔═══════════════════════════════════════════════════════════════════════════╗
║                    YT PLAYLIST DOWNLOADER - SHΔDØW WORM-AI💀🔥                    ║
║              Downloading to: D:\\YT_Playlists\\[Playlist_Name]\\                    ║
╚═══════════════════════════════════════════════════════════════════════════╝{Colors.RESET}
"""
        console.print(Panel(banner, border_style="red"))
        console.print(f"[cyan]📁 Download directory: {self.download_dir}[/cyan]")
    
    def sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for Windows/Unix compatibility"""
        # Remove invalid characters
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Remove trailing dots and spaces
        filename = filename.strip('. ')
        # Limit length
        if len(filename) > 200:
            filename = filename[:200]
        return filename
    
    def get_playlist_info(self, url: str) -> Optional[Dict]:
        """Fetch playlist information without downloading"""
        console.print(f"\n[cyan]📊 Fetching playlist information...[/cyan]")
        
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
            'force_generic_extractor': False,
            'ignoreerrors': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return info
        except Exception as e:
            console.print(f"[red]❌ Error fetching playlist: {e}[/red]")
            return None
    
    def format_duration(self, seconds: Any) -> str:
        """Format duration in HH:MM:SS - handles int, float, and None"""
        if not seconds:
            return "Unknown"
        
        # Handle both int and float safely
        try:
            seconds = int(float(seconds))
        except (ValueError, TypeError):
            return "Unknown"
        
        if seconds < 0:
            return "Unknown"
        
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        return f"{minutes:02d}:{secs:02d}"
    
    def display_playlist_info(self, info: Dict):
        """Display playlist information in a nice table"""
        table = Table(title="📋 PLAYLIST INFORMATION", style="cyan")
        table.add_column("Property", style="bold yellow")
        table.add_column("Value", style="white")
        
        title = info.get('title', 'Unknown')
        table.add_row("Title", title[:60] if title else "Unknown")
        table.add_row("Channel", info.get('uploader', 'Unknown'))
        table.add_row("Total Videos", str(info.get('playlist_count', 0)))
        table.add_row("Duration", self.format_duration(info.get('duration', 0)))
        
        if info.get('description'):
            desc = info.get('description', '')[:100]
            if len(info.get('description', '')) > 100:
                desc += '...'
            table.add_row("Description", desc)
        
        console.print(table)
        
        # Show first few videos
        entries = info.get('entries', [])
        if entries:
            video_table = Table(title="📹 FIRST 10 VIDEOS IN PLAYLIST", style="green")
            video_table.add_column("#", style="bold yellow")
            video_table.add_column("Title", style="white")
            video_table.add_column("Duration", style="cyan")
            
            for i, entry in enumerate(entries[:10], 1):
                if entry is None:
                    continue
                duration = self.format_duration(entry.get('duration', 0))
                title = entry.get('title', 'Unknown')[:50]
                video_table.add_row(str(i), title, duration)
            
            console.print(video_table)
            
            total_entries = len([e for e in entries if e is not None])
            if total_entries > 10:
                console.print(f"[dim]... and {total_entries - 10} more videos[/dim]")
    
    def get_quality_preset(self) -> Tuple[str, Dict]:
        """Get quality preset from user"""
        console.print("\n[bold yellow]🎯 SELECT QUALITY PRESET[/bold yellow]")
        
        for key, preset in QUALITY_PRESETS.items():
            console.print(f"  {key}. {preset['name']}")
            console.print(f"     [dim]{preset['description']}[/dim]")
        
        choice = Prompt.ask("\n[green]Enter choice[/green]", choices=list(QUALITY_PRESETS.keys()), default="1")
        
        preset = QUALITY_PRESETS[choice].copy()
        
        if choice == "5":  # Custom format
            preset['format'] = Prompt.ask("[cyan]Enter format code[/cyan]\n[dim](e.g., bestvideo[height<=1080]+bestaudio, 137+140, etc.)[/dim]")
        
        return choice, preset
    
    def progress_hook(self, d: Dict):
        """Progress hook for yt-dlp"""
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', '0%').replace('%', '').strip()
            speed = d.get('_speed_str', 'N/A')
            eta = d.get('_eta_str', 'N/A')
            filename = d.get('filename', '')
            if filename:
                # Show just the filename, not the full path
                filename = Path(filename).name[:40]
            console.print(f"\r   [dim]⬇️  {filename} | {percent}% | Speed: {speed} | ETA: {eta}[/dim]", end='')
        elif d['status'] == 'finished':
            filename = Path(d.get('filename', 'Unknown')).name
            console.print(f"\r   [green]✅ Downloaded: {filename}[/green]")
            self.downloaded_count += 1
        elif d['status'] == 'error':
            console.print(f"\r   [red]❌ Error downloading video[/red]")
            self.failed_count += 1
    
    def download_playlist(self, url: str, preset: Dict, max_downloads: Optional[int] = None):
        """Download the entire playlist to D: drive"""
        self.cancelled = False
        self.downloaded_count = 0
        self.failed_count = 0
        
        # Get playlist title for folder name
        playlist_title = "Playlist"
        try:
            ydl_opts = {'quiet': True, 'extract_flat': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if info and info.get('title'):
                    playlist_title = self.sanitize_filename(info.get('title', 'Playlist'))
        except:
            pass
        
        # Create folder: D:\YT_Playlists\Playlist_Name\
        output_dir = self.download_dir / playlist_title
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Prepare output template - saves as D:\YT_Playlists\Playlist_Name\video_title.mp4
        output_template = str(output_dir / '%(title)s.%(ext)s')
        
        # Base options - NO THUMBNAILS
        ydl_opts = {
            'outtmpl': output_template,
            'ignoreerrors': True,
            'no_warnings': False,
            'quiet': False,
            'progress_hooks': [self.progress_hook],
            'merge_output_format': 'mp4',
            'postprocessors': preset.get('postprocessors', []),
            # Thumbnail options removed
            'writesubtitles': False,
            'writeautomaticsub': False,
        }
        
        # Set format
        if preset.get('format'):
            ydl_opts['format'] = preset['format']
        
        # Set max downloads
        if max_downloads:
            ydl_opts['playlistend'] = max_downloads
        
        console.print(f"\n[green]📥 Starting download...[/green]")
        console.print(f"   Output directory: [cyan]{output_dir}[/cyan]")
        console.print(f"   Quality: [cyan]{preset['name']}[/cyan]")
        if max_downloads:
            console.print(f"   Max videos: [cyan]{max_downloads}[/cyan]")
        console.print("")
        
        start_time = time.time()
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
                
        except KeyboardInterrupt:
            console.print("\n[yellow]⚠️ Download interrupted by user[/yellow]")
            self.cancelled = True
        except Exception as e:
            console.print(f"\n[red]❌ Download error: {e}[/red]")
            import traceback
            traceback.print_exc()
        
        elapsed = time.time() - start_time
        
        # Summary
        console.print("\n" + "=" * 60)
        if not self.cancelled:
            console.print(f"[bold green]✅ DOWNLOAD COMPLETE![/bold green]")
            console.print(f"   Videos downloaded: [green]{self.downloaded_count}[/green]")
            if self.failed_count > 0:
                console.print(f"   Failed: [red]{self.failed_count}[/red]")
            console.print(f"   Time taken: [cyan]{self.format_duration(int(elapsed))}[/cyan]")
            console.print(f"   Location: [cyan]{output_dir}[/cyan]")
            
            # Save to history
            try:
                with yt_dlp.YoutubeDL({'quiet': True, 'extract_flat': True}) as ydl:
                    info = ydl.extract_info(url, download=False)
                    playlist_title_save = info.get('title', 'Unknown') if info else 'Unknown'
            except:
                playlist_title_save = 'Unknown'
            
            self.download_history[datetime.now().isoformat()] = {
                'url': url,
                'title': playlist_title_save,
                'quality': preset['name'],
                'downloaded': self.downloaded_count,
                'failed': self.failed_count,
                'location': str(output_dir)
            }
            self.save_history()
        else:
            console.print(f"[bold red]❌ DOWNLOAD CANCELLED[/bold red]")
        
        console.print("=" * 60)
    
    def show_history(self):
        """Show download history"""
        if not self.download_history:
            console.print("[yellow]No download history found.[/yellow]")
            return
        
        table = Table(title="📜 DOWNLOAD HISTORY", style="cyan")
        table.add_column("Date", style="yellow")
        table.add_column("Playlist", style="white")
        table.add_column("Quality", style="green")
        table.add_column("Videos", style="cyan")
        table.add_column("Location", style="dim")
        
        for timestamp, record in sorted(self.download_history.items(), reverse=True)[:20]:
            try:
                date = timestamp[:19].replace('T', ' ')
                table.add_row(
                    date,
                    record.get('title', 'Unknown')[:30],
                    record.get('quality', 'Unknown')[:25],
                    str(record.get('downloaded', 0)),
                    Path(record.get('location', '')).name[:20]
                )
            except:
                continue
        
        console.print(table)
    
    def show_ffmpeg_help(self):
        """Show help for ffmpeg installation"""
        console.print("""
[bold yellow]🔧 FFMPEG REQUIRED FOR BEST QUALITY[/bold yellow]

To download videos in best quality (merging video + audio), you need ffmpeg installed.

[cyan]Windows:[/cyan]
  1. Download from https://ffmpeg.org/download.html
  2. Extract to C:\\ffmpeg
  3. Add C:\\ffmpeg\\bin to System PATH
  4. Restart command prompt

[cyan]macOS:[/cyan]
  brew install ffmpeg

[cyan]Linux (Ubuntu/Debian):[/cyan]
  sudo apt install ffmpeg

[cyan]Linux (Arch):[/cyan]
  sudo pacman -S ffmpeg

After installing, restart this script.
""")
        input("\nPress Enter to continue...")
    
    def check_ffmpeg(self) -> bool:
        """Check if ffmpeg is installed"""
        if shutil.which('ffmpeg'):
            return True
        
        console.print("[red]⚠️ FFmpeg not found![/red]")
        console.print("[yellow]Without FFmpeg, you can only download lower quality videos or audio only.[/yellow]")
        
        if Confirm.ask("Do you want to see installation instructions?"):
            self.show_ffmpeg_help()
            return False
        
        if Confirm.ask("Continue without FFmpeg? (lower quality only)"):
            return True
        
        return False
    
    def open_downloads_folder(self):
        """Open the downloads folder in file explorer"""
        try:
            if sys.platform == 'darwin':  # macOS
                os.system(f'open "{self.download_dir}"')
            elif sys.platform == 'win32':  # Windows
                os.system(f'start "" "{self.download_dir}"')
            else:  # Linux
                os.system(f'xdg-open "{self.download_dir}"')
            console.print(f"[green]📁 Opening: {self.download_dir}[/green]")
        except Exception as e:
            console.print(f"[red]Could not open folder: {e}[/red]")
    
    def run(self):
        """Main execution loop"""
        self.print_banner()
        
        # Check if D: drive exists
        if not Path("D:/").exists():
            console.print("[red]❌ WARNING: D: drive not found![/red]")
            console.print("[yellow]The script will try to create folders anyway...[/yellow]")
        
        # Check ffmpeg
        if not self.check_ffmpeg():
            console.print("[yellow]⚠️ Continuing without ffmpeg...[/yellow]")
        
        while True:
            console.print("\n[bold cyan]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/bold cyan]")
            console.print("[bold yellow]📋 MAIN MENU[/bold yellow]")
            console.print("  [cyan]1.[/cyan] 📥 Download Playlist")
            console.print("  [cyan]2.[/cyan] 🔍 Get Playlist Info Only")
            console.print("  [cyan]3.[/cyan] 📜 View Download History")
            console.print("  [cyan]4.[/cyan] 📁 Open Downloads Folder")
            console.print("  [cyan]5.[/cyan] 🔧 Check FFmpeg Status")
            console.print("  [cyan]6.[/cyan] ❌ Exit")
            
            choice = Prompt.ask("\n[green]Select option[/green]", choices=["1", "2", "3", "4", "5", "6"])
            
            if choice == "1":
                url = Prompt.ask("[cyan]Enter YouTube playlist URL[/cyan]")
                
                if not url or "youtube.com" not in url and "youtu.be" not in url:
                    console.print("[red]❌ Invalid YouTube URL![/red]")
                    continue
                
                # Get playlist info first
                info = self.get_playlist_info(url)
                if not info:
                    console.print("[red]❌ Could not fetch playlist information. Please check the URL.[/red]")
                    continue
                
                self.display_playlist_info(info)
                
                # Confirm download
                if not Confirm.ask("\n[bold red]Start download?[/bold red]"):
                    continue
                
                # Get quality preset
                preset_choice, preset = self.get_quality_preset()
                
                # Max downloads
                total_videos = info.get('playlist_count', 0)
                max_downloads = None
                
                if total_videos > 20:
                    if not Confirm.ask(f"Playlist has {total_videos} videos. Download all?"):
                        try:
                            max_input = Prompt.ask("[cyan]Enter number of videos to download[/cyan]", default="10")
                            max_downloads = int(max_input)
                            if max_downloads <= 0:
                                max_downloads = None
                        except:
                            max_downloads = 10
                
                # Show where files will be saved
                playlist_title = "Playlist"
                try:
                    with yt_dlp.YoutubeDL({'quiet': True, 'extract_flat': True}) as ydl:
                        temp_info = ydl.extract_info(url, download=False)
                        if temp_info and temp_info.get('title'):
                            playlist_title = self.sanitize_filename(temp_info.get('title', 'Playlist'))
                except:
                    pass
                
                console.print(f"\n[bold green]📁 Files will be saved to:[/bold green]")
                console.print(f"[cyan]D:\\YT_Playlists\\{playlist_title}\\[/cyan]")
                
                if not Confirm.ask("\n[bold red]Proceed with download?[/bold red]"):
                    continue
                
                # Download
                self.download_playlist(url, preset, max_downloads)
                
            elif choice == "2":
                url = Prompt.ask("[cyan]Enter YouTube playlist URL[/cyan]")
                info = self.get_playlist_info(url)
                if info:
                    self.display_playlist_info(info)
                else:
                    console.print("[red]❌ Could not fetch playlist information.[/red]")
            
            elif choice == "3":
                self.show_history()
            
            elif choice == "4":
                self.open_downloads_folder()
            
            elif choice == "5":
                if self.check_ffmpeg():
                    console.print("[green]✅ FFmpeg is installed![/green]")
                else:
                    console.print("[red]❌ FFmpeg not found[/red]")
            
            elif choice == "6":
                console.print("[bold green]👋 Goodbye![/bold green]")
                break

def main():
    """Main entry point"""
    try:
        downloader = YTPlaylistDownloader()
        downloader.run()
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️ Interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"[red]❌ Fatal error: {e}[/red]")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
