#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════╗
║  YT PLAYLIST DOWNLOADER 🔥                                                ║
║  Download complete YouTube playlists in best quality for offline viewing  ║
║  Supports: 4K/1080p/720p, Audio extraction, Metadata preservation         ║
╚═══════════════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import json
import time
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# ===== DEPENDENCY CHECK =====
def check_dependencies():
    missing = []
    try:
        import yt_dlp
    except ImportError:
        missing.append("yt-dlp")
    
    try:
        from rich.console import Console
        from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
        from rich.table import Table
        from rich.panel import Panel
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
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
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
        self.download_dir = Path.home() / "Downloads" / "YT_Playlists"
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.history_file = self.download_dir / "download_history.json"
        self.download_history = self.load_history()
        self.cancelled = False
    
    def load_history(self) -> Dict:
        """Load download history"""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_history(self):
        """Save download history"""
        with open(self.history_file, 'w') as f:
            json.dump(self.download_history, f, indent=2)
    
    def print_banner(self):
        banner = f"""
{Colors.RED}{Colors.BOLD}╔═══════════════════════════════════════════════════════════════════════════╗
║                    YT PLAYLIST DOWNLOADER 🔥                                                      ║
║                    Download playlists in best quality for offline viewing                         ║
╚═══════════════════════════════════════════════════════════════════════════╝{Colors.RESET}
"""
        console.print(Panel(banner, border_style="red"))
    
    def get_playlist_info(self, url: str) -> Optional[Dict]:
        """Fetch playlist information without downloading"""
        console.print(f"\n[cyan]📊 Fetching playlist information...[/cyan]")
        
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
            'force_generic_extractor': False,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return info
        except Exception as e:
            console.print(f"[red]❌ Error fetching playlist: {e}[/red]")
            return None
    
    def display_playlist_info(self, info: Dict):
        """Display playlist information in a nice table"""
        table = Table(title="📋 PLAYLIST INFORMATION", style="cyan")
        table.add_column("Property", style="bold yellow")
        table.add_column("Value", style="white")
        
        table.add_row("Title", info.get('title', 'Unknown')[:60])
        table.add_row("Channel", info.get('uploader', 'Unknown'))
        table.add_row("Total Videos", str(info.get('playlist_count', 0)))
        table.add_row("Duration", self.format_duration(info.get('duration', 0)))
        
        if info.get('description'):
            desc = info.get('description', '')[:100] + ('...' if len(info.get('description', '')) > 100 else '')
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
                duration = self.format_duration(entry.get('duration', 0))
                title = entry.get('title', 'Unknown')[:50]
                video_table.add_row(str(i), title, duration)
            
            console.print(video_table)
            
            if len(entries) > 10:
                console.print(f"[dim]... and {len(entries) - 10} more videos[/dim]")
    
    def format_duration(self, seconds: int) -> str:
        """Format duration in HH:MM:SS"""
        if not seconds:
            return "Unknown"
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        return f"{minutes:02d}:{seconds:02d}"
    
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
    
    def create_progress_hook(self):
        """Create progress hook for yt-dlp"""
        progress = Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
            console=console,
            transient=False
        )
        task_id = None
        
        def progress_hook(d):
            nonlocal task_id
            if d['status'] == 'downloading':
                if task_id is None:
                    task_id = progress.add_task(f"[cyan]Downloading...[/cyan]", total=100)
                if d.get('_percent_str'):
                    try:
                        percent = float(d['_percent_str'].replace('%', '').strip())
                        progress.update(task_id, completed=percent)
                    except:
                        pass
            elif d['status'] == 'finished':
                if task_id:
                    progress.update(task_id, completed=100)
        
        return progress, progress_hook
    
    def download_playlist(self, url: str, output_dir: Path, preset: Dict, max_downloads: int = None):
        """Download the entire playlist"""
        self.cancelled = False
        
        # Prepare output template
        output_template = str(output_dir / '%(playlist_title)s' / '%(title)s.%(ext)s')
        
        # Base options
        ydl_opts = {
            'outtmpl': output_template,
            'ignoreerrors': True,
            'no_warnings': False,
            'quiet': False,
            'progress_hooks': [self.progress_hook],
            'merge_output_format': 'mp4',
            'postprocessors': preset.get('postprocessors', []),
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
        
        start_time = time.time()
        downloaded_count = 0
        failed_count = 0
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Update progress display
                info = ydl.extract_info(url, download=True)
                
                # Count downloaded videos
                if 'entries' in info:
                    for entry in info['entries']:
                        if entry is not None:
                            downloaded_count += 1
                        else:
                            failed_count += 1
                else:
                    downloaded_count = 1
                
        except KeyboardInterrupt:
            console.print("\n[yellow]⚠️ Download interrupted by user[/yellow]")
            self.cancelled = True
        except Exception as e:
            console.print(f"\n[red]❌ Download error: {e}[/red]")
        
        elapsed = time.time() - start_time
        
        # Summary
        console.print("\n" + "=" * 60)
        if not self.cancelled:
            console.print(f"[bold green]✅ DOWNLOAD COMPLETE![/bold green]")
            console.print(f"   Videos downloaded: [green]{downloaded_count}[/green]")
            if failed_count > 0:
                console.print(f"   Failed: [red]{failed_count}[/red]")
            console.print(f"   Time taken: [cyan]{self.format_duration(int(elapsed))}[/cyan]")
            console.print(f"   Location: [cyan]{output_dir}[/cyan]")
            
            # Save to history
            playlist_title = info.get('title', 'Unknown') if 'info' in locals() else 'Unknown'
            self.download_history[datetime.now().isoformat()] = {
                'url': url,
                'title': playlist_title,
                'quality': preset['name'],
                'downloaded': downloaded_count,
                'failed': failed_count,
                'location': str(output_dir)
            }
            self.save_history()
        else:
            console.print(f"[bold red]❌ DOWNLOAD CANCELLED[/bold red]")
        
        console.print("=" * 60)
    
    def progress_hook(self, d):
        """Progress hook for yt-dlp"""
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', '0%').replace('%', '').strip()
            speed = d.get('_speed_str', 'N/A')
            eta = d.get('_eta_str', 'N/A')
            console.print(f"\r   [dim]Downloading: {percent}% | Speed: {speed} | ETA: {eta}[/dim]", end='')
        elif d['status'] == 'finished':
            console.print(f"\r   [green]✓ Downloaded: {d.get('filename', 'Unknown')}[/green]")
    
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
        
        for timestamp, record in sorted(self.download_history.items(), reverse=True)[:20]:
            date = timestamp[:19].replace('T', ' ')
            table.add_row(
                date,
                record.get('title', 'Unknown')[:40],
                record.get('quality', 'Unknown')[:30],
                str(record.get('downloaded', 0))
            )
        
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

[cyan]macOS:[/cyan]
  brew install ffmpeg

[cyan]Linux (Ubuntu/Debian):[/cyan]
  sudo apt install ffmpeg

[cyan]Linux (Arch):[/cyan]
  sudo pacman -S ffmpeg

After installing, restart this script.
""")
    
    def run(self):
        """Main execution loop"""
        self.print_banner()
        
        # Check ffmpeg
        import shutil
        if not shutil.which('ffmpeg'):
            console.print("[red]⚠️ FFmpeg not found![/red]")
            if Confirm.ask("Do you want to see installation instructions?"):
                self.show_ffmpeg_help()
                return
        
        while True:
            console.print("\n[bold cyan]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/bold cyan]")
            console.print("[bold yellow]📋 MAIN MENU[/bold yellow]")
            console.print("  1. 📥 Download Playlist")
            console.print("  2. 🔍 Get Playlist Info Only")
            console.print("  3. 📜 View Download History")
            console.print("  4. 📁 Open Downloads Folder")
            console.print("  5. ❌ Exit")
            
            choice = Prompt.ask("\n[green]Select option[/green]", choices=["1", "2", "3", "4", "5"])
            
            if choice == "1":
                url = Prompt.ask("[cyan]Enter YouTube playlist URL[/cyan]")
                
                # Get playlist info first
                info = self.get_playlist_info(url)
                if not info:
                    continue
                
                self.display_playlist_info(info)
                
                # Confirm download
                if not Confirm.ask("\n[bold red]Start download?[/bold red]"):
                    continue
                
                # Get quality preset
                preset_choice, preset = self.get_quality_preset()
                
                # Max downloads
                max_downloads = None
                if info.get('playlist_count', 0) > 20:
                    if Confirm.ask(f"Playlist has {info.get('playlist_count')} videos. Download all?"):
                        max_downloads = None
                    else:
                        try:
                            max_downloads = int(Prompt.ask("[cyan]Enter number of videos to download[/cyan]", default="10"))
                        except:
                            max_downloads = 10
                
                # Output directory
                custom_dir = Confirm.ask("Use custom output directory?")
                if custom_dir:
                    custom_path = Prompt.ask("[cyan]Enter directory path[/cyan]")
                    output_dir = Path(custom_path).expanduser()
                else:
                    playlist_name = info.get('title', 'playlist').replace(' ', '_').replace('/', '_')
                    output_dir = self.download_dir / playlist_name
                
                output_dir.mkdir(parents=True, exist_ok=True)
                
                # Download
                self.download_playlist(url, output_dir, preset, max_downloads)
                
            elif choice == "2":
                url = Prompt.ask("[cyan]Enter YouTube playlist URL[/cyan]")
                info = self.get_playlist_info(url)
                if info:
                    self.display_playlist_info(info)
            
            elif choice == "3":
                self.show_history()
            
            elif choice == "4":
                console.print(f"[green]Opening: {self.download_dir}[/green]")
                os.system(f'open "{self.download_dir}"' if sys.platform == 'darwin' else 
                         f'start "" "{self.download_dir}"' if sys.platform == 'win32' else
                         f'xdg-open "{self.download_dir}"')
            
            elif choice == "5":
                console.print("[bold green]👋 Goodbye![/bold green]")
                break

def main():
    try:
        downloader = YTPlaylistDownloader()
        downloader.run()
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"[red]Fatal error: {e}[/red]")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
