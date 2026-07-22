#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════╗
║  YT PLAYLIST DOWNLOADER 🔥                                                ║
║  Download complete YouTube playlists in best quality for offline viewing  ║
║  Saves to: D:\YT_Playlists\Playlist_Name\                                ║
║  ⚠️ WARNING: DO NOT GO OFFLINE OR CLOSE LAPTOP DURING DOWNLOAD!         ║
╚═══════════════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import json
import time
import re
import shutil
import signal
import subprocess
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
        from rich.text import Text
        from rich.box import ROUNDED
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
from rich.text import Text
from rich.box import ROUNDED
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn

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
    BG_RED = '\033[41m'
    BG_YELLOW = '\033[43m'

# ===== QUALITY PRESETS =====
QUALITY_PRESETS = {
    "1": {
        "name": "🎬 BEST QUALITY (1080p/4K) - Merged",
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "description": "1080p maximum, best quality with merge",
        "needs_merge": True
    },
    "2": {
        "name": "📱 1080p HIGH QUALITY - Pre-merged",
        "format": "best[height<=1080][ext=mp4]/best",
        "description": "1080p, pre-merged format, NO merge needed",
        "needs_merge": False
    },
    "3": {
        "name": "📱 720p MEDIUM QUALITY - Pre-merged",
        "format": "best[height<=720][ext=mp4]/best",
        "description": "720p, smaller file size, NO merge needed",
        "needs_merge": False
    },
    "4": {
        "name": "📱 480p LOW QUALITY - Pre-merged",
        "format": "best[height<=480][ext=mp4]/best",
        "description": "480p, smallest file size",
        "needs_merge": False
    },
    "5": {
        "name": "🎵 AUDIO ONLY (MP3 320kbps)",
        "format": "bestaudio/best",
        "description": "Extract audio as MP3 320kbps",
        "needs_merge": False,
        "postprocessors": [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320',
        }]
    },
    "6": {
        "name": "🎵 AUDIO ONLY (M4A High Quality)",
        "format": "bestaudio[ext=m4a]/bestaudio",
        "description": "Extract audio as M4A (high quality)",
        "needs_merge": False
    },
    "7": {
        "name": "📦 CUSTOM QUALITY",
        "format": None,
        "description": "Manually specify format code",
        "needs_merge": True
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
        self.paused = False
        self.current_video = ""
        self.downloaded_count = 0
        self.failed_count = 0
        self.total_videos = 0
        self.retry_count = 0
        self.max_retries = 3
        self.current_ydl = None  # Store downloader instance for pause/resume
    
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
        """Display the banner with warning"""
        banner = f"""
{Colors.RED}{Colors.BOLD}╔═══════════════════════════════════════════════════════════════════════════╗
║                    YT PLAYLIST DOWNLOADER - SHΔDØW WORM-AI💀🔥                    ║
║              Downloading to: D:\\YT_Playlists\\[Playlist_Name]\\                    ║
╚═══════════════════════════════════════════════════════════════════════════╝{Colors.RESET}
"""
        console.print(Panel(banner, border_style="red"))
        
        # BIG WARNING BOX
        warning_text = f"""
{Colors.BG_RED}{Colors.WHITE}{Colors.BOLD}⚠️  IMPORTANT WARNING ⚠️{Colors.RESET}

{Colors.RED}{Colors.BOLD}🔴 DO NOT GO OFFLINE DURING DOWNLOAD!{Colors.RESET}
{Colors.RED}🔴 DO NOT CLOSE LAPTOP LID!{Colors.RESET}
{Colors.RED}🔴 DO NOT PUT COMPUTER TO SLEEP!{Colors.RESET}
{Colors.RED}🔴 DO NOT UNPLUG POWER CABLE!{Colors.RESET}

{Colors.YELLOW}⚠️ If download is interrupted, videos may become CORRUPTED!{Colors.RESET}
{Colors.GREEN}✅ Keep your internet connection stable and laptop awake.{Colors.RESET}
"""
        console.print(Panel(warning_text, border_style="red", box=ROUNDED))
        
        console.print(f"[cyan]📁 Download directory: {self.download_dir}[/cyan]")
        
        # Check D: drive
        if not Path("D:/").exists():
            console.print("[red]❌ WARNING: D: drive not found![/red]")
            if not Confirm.ask("[yellow]Continue anyway?[/yellow]"):
                sys.exit(0)
    
    def sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for Windows/Unix compatibility"""
        # Remove invalid characters
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Remove trailing dots and spaces
        filename = filename.strip('. ')
        # Limit length to avoid Windows path issues
        if len(filename) > 150:
            filename = filename[:150]
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
    
    def format_file_size(self, size_bytes: float) -> str:
        """Format file size in MB or GB"""
        if not size_bytes:
            return "Unknown"
        if size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"
    
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
        
        if choice == "7":  # Custom format
            preset['format'] = Prompt.ask("[cyan]Enter format code[/cyan]\n[dim](e.g., bestvideo[height<=1080]+bestaudio, 137+140, etc.)[/dim]")
            preset['needs_merge'] = Confirm.ask("Does this format require merging video + audio?")
        
        return choice, preset
    
    def progress_hook(self, d: Dict):
        """Progress hook for yt-dlp with pause support"""
        if self.paused:
            return
        
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', '0%').replace('%', '').strip()
            speed = d.get('_speed_str', 'N/A')
            eta = d.get('_eta_str', 'N/A')
            downloaded = d.get('_downloaded_bytes_str', '0')
            total = d.get('_total_bytes_str', 'Unknown')
            filename = d.get('filename', '')
            
            if filename:
                filename = Path(filename).name[:40]
            
            console.print(f"\r   [dim]⬇️  {filename} | {percent}% | {downloaded}/{total} | Speed: {speed} | ETA: {eta}[/dim]", end='')
            
        elif d['status'] == 'finished':
            filename = Path(d.get('filename', 'Unknown')).name
            console.print(f"\r   [green]✅ Downloaded: {filename}[/green]")
            self.downloaded_count += 1
            
        elif d['status'] == 'error':
            console.print(f"\r   [red]❌ Error downloading video[/red]")
            self.failed_count += 1
    
    def merge_video_audio(self, output_dir: Path) -> bool:
        """Manually merge video and audio files that are separate"""
        console.print("\n[bold yellow]🔄 Starting manual merge process...[/bold yellow]")
        
        # Find all video files without audio (f140 files)
        video_files = []
        audio_files = []
        
        for file in output_dir.glob("*.*"):
            if "f" in file.stem and "m4a" in file.suffix.lower():
                # This is an audio file
                audio_files.append(file)
            elif "f" in file.stem and file.suffix.lower() in ['.mp4', '.webm']:
                # Check if it's a video file
                video_files.append(file)
        
        if not video_files:
            console.print("[yellow]No separate video files found to merge.[/yellow]")
            return True
        
        merged_count = 0
        failed_count = 0
        
        for video_file in video_files:
            # Try to find matching audio file
            video_name = video_file.stem
            matching_audio = None
            
            for audio_file in audio_files:
                audio_name = audio_file.stem
                # Check if they share the same base name (before the format code)
                if video_name.split('f')[0] == audio_name.split('f')[0]:
                    matching_audio = audio_file
                    break
            
            if not matching_audio:
                console.print(f"[yellow]⚠️ No matching audio found for: {video_file.name}[/yellow]")
                continue
            
            # Output merged file
            output_file = output_dir / f"{video_name.split('f')[0]}.mp4"
            
            console.print(f"\n[cyan]🔄 Merging: {video_file.name} + {matching_audio.name}[/cyan]")
            console.print(f"   → [green]{output_file.name}[/green]")
            
            try:
                cmd = [
                    'ffmpeg',
                    '-i', str(video_file),
                    '-i', str(matching_audio),
                    '-c:v', 'copy',
                    '-c:a', 'aac',
                    '-map', '0:v:0',
                    '-map', '1:a:0',
                    '-shortest',
                    '-y',
                    str(output_file)
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
                
                if result.returncode == 0:
                    # Delete the separate files
                    try:
                        video_file.unlink()
                        matching_audio.unlink()
                    except:
                        pass
                    merged_count += 1
                    console.print(f"[green]✅ Merged successfully![/green]")
                else:
                    console.print(f"[red]❌ Merge failed: {result.stderr[:100]}[/red]")
                    failed_count += 1
                    
            except subprocess.TimeoutExpired:
                console.print("[red]❌ Merge timed out (video may be too large)[/red]")
                failed_count += 1
            except Exception as e:
                console.print(f"[red]❌ Merge error: {e}[/red]")
                failed_count += 1
        
        console.print(f"\n[bold cyan]📊 Merge Summary:[/bold cyan]")
        console.print(f"   Merged successfully: [green]{merged_count}[/green]")
        if failed_count > 0:
            console.print(f"   Failed: [red]{failed_count}[/red]")
        
        return failed_count == 0
    
    def download_playlist(self, url: str, preset: Dict, max_downloads: Optional[int] = None, needs_merge: bool = False):
        """Download the entire playlist to D: drive"""
        self.cancelled = False
        self.paused = False
        self.downloaded_count = 0
        self.failed_count = 0
        self.retry_count = 0
        
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
        
        # Prepare output template with improved naming
        output_template = str(output_dir / '%(title)s.f%(format_id)s.%(ext)s')
        
        # Base options
        ydl_opts = {
            'outtmpl': output_template,
            'ignoreerrors': True,
            'no_warnings': False,
            'quiet': False,
            'progress_hooks': [self.progress_hook],
            'overwrites': True,
            'restrictfilenames': True,
            'windowsfilenames': True,
            'writesubtitles': False,
            'writeautomaticsub': False,
            'writethumbnail': False,
            'merge_output_format': 'mp4',
            'keepvideo': True,  # Keep separate files if we want to merge manually
            'fixup': 'never',
        }
        
        # If needs_merge is True, download video and audio separately
        if needs_merge:
            console.print("[yellow]🔀 Merge mode enabled: Downloading video + audio separately[/yellow]")
            console.print("[dim]Files will be merged after download[/dim]")
            ydl_opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best'
        else:
            # Use pre-merged format
            if preset.get('format'):
                ydl_opts['format'] = preset['format']
        
        # Add audio postprocessor if needed
        if preset.get('postprocessors'):
            ydl_opts['postprocessors'] = preset.get('postprocessors')
        
        # Set max downloads
        if max_downloads:
            ydl_opts['playlistend'] = max_downloads
        
        console.print(f"\n[green]📥 Starting download...[/green]")
        console.print(f"   Output directory: [cyan]{output_dir}[/cyan]")
        console.print(f"   Quality: [cyan]{preset['name']}[/cyan]")
        if max_downloads:
            console.print(f"   Max videos: [cyan]{max_downloads}[/cyan]")
        if needs_merge:
            console.print(f"   [yellow]🔀 Merge mode: ON (will merge after download)[/yellow]")
        else:
            console.print(f"   [green]📦 Pre-merged format: NO merge needed[/green]")
        
        # Show pause/resume instructions
        console.print("\n[dim]💡 Press Ctrl+C to pause/resume[/dim]")
        console.print("[dim]⚠️ Closing terminal will cancel the download[/dim]")
        console.print("")
        
        start_time = time.time()
        
        # Retry loop
        while self.retry_count < self.max_retries:
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    self.current_ydl = ydl
                    ydl.download([url])
                    break  # Success
                    
            except KeyboardInterrupt:
                console.print("\n[yellow]⏸️ Download paused by user[/yellow]")
                self.paused = not self.paused
                if self.paused:
                    console.print("[yellow]⏸️ Download paused. Press Ctrl+C again to resume.[/yellow]")
                    try:
                        while self.paused:
                            time.sleep(1)
                    except KeyboardInterrupt:
                        self.paused = False
                        console.print("[green]▶️ Download resumed![/green]")
                        continue
                else:
                    console.print("[green]▶️ Download resumed![/green]")
                    continue
                    
            except Exception as e:
                self.retry_count += 1
                console.print(f"\n[red]❌ Download error: {e}[/red]")
                
                if self.retry_count < self.max_retries:
                    console.print(f"[yellow]Retry {self.retry_count}/{self.max_retries} in 5 seconds...[/yellow]")
                    time.sleep(5)
                else:
                    console.print(f"[red]❌ Failed after {self.max_retries} retries[/red]")
                    break
        
        elapsed = time.time() - start_time
        
        # ===== MANUAL MERGE =====
        if needs_merge and self.downloaded_count > 0:
            console.print("\n" + "=" * 60)
            console.print("[bold yellow]🔀 MERGING VIDEO AND AUDIO FILES[/bold yellow]")
            console.print("[dim]This may take a few minutes...[/dim]")
            
            # Ask user if they want to merge now
            if Confirm.ask("Merge video and audio files now?"):
                merge_success = self.merge_video_audio(output_dir)
                if merge_success:
                    console.print("[green]✅ All files merged successfully![/green]")
                else:
                    console.print("[yellow]⚠️ Some files failed to merge. You can try manually later.[/yellow]")
            else:
                console.print("[yellow]⚠️ Merge skipped. Files saved separately.[/yellow]")
                console.print("[dim]You can merge them later using the merge option in main menu.[/dim]")
        
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
                'location': str(output_dir),
                'merged': needs_merge
            }
            self.save_history()
        else:
            console.print(f"[bold red]❌ DOWNLOAD CANCELLED[/bold red]")
        
        console.print("=" * 60)
        
        # Open folder option
        if self.downloaded_count > 0:
            if Confirm.ask("Open downloads folder?"):
                self.open_downloads_folder()
    
    def manual_merge_folder(self):
        """Manually merge files in a folder"""
        console.print("\n[bold yellow]🔀 MANUAL MERGE UTILITY[/bold yellow]")
        console.print("[dim]This will merge separate video and audio files in a folder[/dim]")
        
        folder_path = Prompt.ask("[cyan]Enter folder path containing video/audio files[/cyan]", default=str(self.download_dir))
        
        try:
            folder = Path(folder_path).expanduser().resolve()
            if not folder.exists():
                console.print("[red]❌ Folder not found![/red]")
                return
            
            self.merge_video_audio(folder)
            
        except Exception as e:
            console.print(f"[red]❌ Error: {e}[/red]")
    
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
        table.add_column("Merged", style="magenta")
        table.add_column("Location", style="dim")
        
        for timestamp, record in sorted(self.download_history.items(), reverse=True)[:20]:
            try:
                date = timestamp[:19].replace('T', ' ')
                merged_status = "✅" if record.get('merged', False) else "❌"
                table.add_row(
                    date,
                    record.get('title', 'Unknown')[:25],
                    record.get('quality', 'Unknown')[:20],
                    str(record.get('downloaded', 0)),
                    merged_status,
                    Path(record.get('location', '')).name[:15]
                )
            except:
                continue
        
        console.print(table)
    
    def show_ffmpeg_help(self):
        """Show help for ffmpeg installation"""
        console.print("""
[bold yellow]🔧 FFMPEG REQUIRED FOR MERGING[/bold yellow]

To merge video and audio files, you need ffmpeg installed.

[cyan]Windows:[/cyan]
  1. Download from https://www.gyan.dev/ffmpeg/builds/
  2. Download "ffmpeg-release-full.7z"
  3. Extract to C:\\ffmpeg
  4. Add C:\\ffmpeg\\bin to System PATH:
     - Press Win + R, type "sysdm.cpl"
     - Advanced → Environment Variables
     - Under System Variables, find "Path"
     - Add: C:\\ffmpeg\\bin
     - Click OK and restart terminal

[cyan]OR use winget:[/cyan]
  winget install ffmpeg

After installing, restart this script.
""")
        input("\nPress Enter to continue...")
    
    def check_ffmpeg(self) -> bool:
        """Check if ffmpeg is installed"""
        if shutil.which('ffmpeg'):
            version = os.popen('ffmpeg -version').read().split('\n')[0]
            console.print(f"[green]✅ FFmpeg found: {version[:50]}...[/green]")
            return True
        
        console.print("[red]⚠️ FFmpeg not found![/red]")
        console.print("[yellow]Without FFmpeg, you cannot merge video and audio files.[/yellow]")
        
        if Confirm.ask("Do you want to see installation instructions?"):
            self.show_ffmpeg_help()
        
        if Confirm.ask("Continue without FFmpeg? (merge will not work)"):
            return False
        
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
    
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if sys.platform == 'win32' else 'clear')
    
    def run(self):
        """Main execution loop"""
        self.clear_screen()
        self.print_banner()
        
        # Check ffmpeg
        has_ffmpeg = self.check_ffmpeg()
        
        while True:
            console.print("\n[bold cyan]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/bold cyan]")
            console.print("[bold yellow]📋 MAIN MENU[/bold yellow]")
            console.print("  [cyan]1.[/cyan] 📥 Download Playlist")
            console.print("  [cyan]2.[/cyan] 🔍 Get Playlist Info Only")
            console.print("  [cyan]3.[/cyan] 📜 View Download History")
            console.print("  [cyan]4.[/cyan] 📁 Open Downloads Folder")
            console.print("  [cyan]5.[/cyan] 🔧 Check FFmpeg Status")
            console.print("  [cyan]6.[/cyan] 🔀 Merge Video & Audio Files (Manual)")
            console.print("  [cyan]7.[/cyan] ❌ Exit")
            
            choice = Prompt.ask("\n[green]Select option[/green]", choices=["1", "2", "3", "4", "5", "6", "7"])
            
            if choice == "1":
                # Show warning again before download
                console.print("\n[bold red]⚠️ REMEMBER: DO NOT GO OFFLINE OR CLOSE LAPTOP![/bold red]")
                if not Confirm.ask("[yellow]Proceed with download?[/yellow]"):
                    continue
                
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
                
                # Check if merge is needed
                needs_merge = preset.get('needs_merge', False)
                
                if needs_merge and not has_ffmpeg:
                    console.print("[red]❌ This preset requires ffmpeg for merging![/red]")
                    console.print("[yellow]Please install ffmpeg or choose a pre-merged format.[/yellow]")
                    if not Confirm.ask("Continue anyway? (files will be separate)"):
                        continue
                    needs_merge = False
                
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
                
                if needs_merge:
                    console.print("[yellow]🔀 Merge mode: ON[/yellow]")
                    console.print("[dim]Video and audio will be downloaded separately then merged[/dim]")
                
                if not Confirm.ask("\n[bold red]Proceed with download?[/bold red]"):
                    continue
                
                # Final warning
                console.print("\n[bold red]🔴 FINAL WARNING:[/bold red]")
                console.print("[red]✓ DO NOT GO OFFLINE[/red]")
                console.print("[red]✓ DO NOT CLOSE LAPTOP LID[/red]")
                console.print("[red]✓ DO NOT PUT SYSTEM TO SLEEP[/red]")
                console.print("[red]✓ KEEP POWER CONNECTED[/red]")
                console.print("[dim]Press Enter to start...[/dim]")
                input()
                
                # Download
                self.download_playlist(url, preset, max_downloads, needs_merge)
                
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
                    console.print("[green]✅ FFmpeg is installed and working![/green]")
                    has_ffmpeg = True
                else:
                    console.print("[red]❌ FFmpeg not found[/red]")
                    has_ffmpeg = False
                    if Confirm.ask("Install FFmpeg now?"):
                        self.show_ffmpeg_help()
            
            elif choice == "6":
                self.manual_merge_folder()
            
            elif choice == "7":
                console.print("[bold green]👋 Goodbye![/bold green]")
                break

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    console.print("\n[yellow]⚠️ Download interrupted by user[/yellow]")
    console.print("[dim]You can resume by restarting the download (use same folder)[/dim]")
    sys.exit(0)

def main():
    """Main entry point"""
    # Set up signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
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
