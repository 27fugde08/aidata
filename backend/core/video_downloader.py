import yt_dlp
import os
import uuid

class DownloaderService:
    def __init__(self, download_dir="videos"):
        self.download_dir = download_dir
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)

    def get_info(self, url):
        """Extract metadata without downloading."""
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
                # Platform detection
                platform = "unknown"
                if "youtube.com" in url or "youtu.be" in url: platform = "youtube"
                elif "facebook.com" in url or "fb.watch" in url: platform = "facebook"
                elif "instagram.com" in url: platform = "instagram"
                
                return {
                    "url": url,
                    "platform": platform,
                    "title": info.get("title", "Unknown Title"),
                    "duration": info.get("duration", 0),
                    "thumbnail": info.get("thumbnail", ""),
                    "ext": info.get("ext", "mp4")
                }
            except Exception as e:
                return {"error": str(e)}

    def download(self, url):
        """Download video and return file path."""
        # Use a unique name to avoid conflicts and special character issues
        unique_id = str(uuid.uuid4())[:8]
        
        ydl_opts = {
            'outtmpl': os.path.join(self.download_dir, f'%(title)s_{unique_id}.%(ext)s'),
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'merge_output_format': 'mp4',
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                
                # yt-dlp might change extension after merge
                if not os.path.exists(filename) and os.path.exists(filename + ".mp4"):
                    filename += ".mp4"
                elif not filename.endswith(".mp4"):
                    # Check if merged file exists with .mp4
                    base = os.path.splitext(filename)[0]
                    if os.path.exists(base + ".mp4"):
                        filename = base + ".mp4"

                return {
                    "status": "success",
                    "file_path": filename,
                    "title": info.get("title"),
                    "duration": info.get("duration"),
                    "thumbnail": info.get("thumbnail"),
                    "platform": self._detect_platform(url)
                }
            except Exception as e:
                return {"status": "error", "error": str(e)}

    def _detect_platform(self, url):
        if "youtube.com" in url or "youtu.be" in url: return "youtube"
        if "facebook.com" in url or "fb.watch" in url: return "facebook"
        if "instagram.com" in url: return "instagram"
        return "other"
