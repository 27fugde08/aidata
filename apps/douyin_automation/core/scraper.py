import os
import asyncio
import json
import re
from typing import Dict, Any, List

class DouyinScraper:
    """
    Bộ giải mã video Douyin thật, lấy link không logo (no watermark) và metadata chất lượng cao.
    """
    def __init__(self, download_path: str = "outputs/douyin"):
        self.download_path = download_path
        os.makedirs(self.download_path, exist_ok=True)

    async def get_video_info(self, url: str) -> Dict[str, Any]:
        """Lấy thông tin video và link không logo bằng yt-dlp."""
        print(f"🔍 [DouyinScraper] Extracting: {url}")
        
        # yt-dlp mặc định hỗ trợ Douyin rất tốt để lấy link không logo
        cmd = [
            "yt-dlp",
            "--dump-json",
            "--no-playlist",
            "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            url
        ]
        
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            
            if proc.returncode != 0:
                error_msg = stderr.decode()
                print(f"❌ [DouyinScraper] yt-dlp error: {error_msg}")
                return {"error": error_msg}
                
            info = json.loads(stdout.decode())
            
            # Phân tích kết quả
            video_data = {
                "id": info.get("id"),
                "title": info.get("title", "Douyin Video"),
                "description": info.get("description", ""),
                "author": info.get("uploader", "Unknown"),
                "author_id": info.get("uploader_id"),
                "thumbnail": info.get("thumbnail"),
                "original_url": url,
                "video_url": info.get("url"), # Đây thường là link không logo
                "duration": info.get("duration", 0),
                "timestamp": info.get("timestamp"),
                "like_count": info.get("like_count", 0),
                "comment_count": info.get("comment_count", 0),
                "tags": info.get("tags", [])
            }
            
            # Ghi log kết quả (cho mục đích rà soát logic)
            with open(os.path.join(self.download_path, f"{info.get('id')}_meta.json"), "w", encoding="utf-8") as f:
                json.dump(video_data, f, ensure_ascii=False, indent=4)
                
            return video_data
            
        except Exception as e:
            print(f"❌ [DouyinScraper] Exception: {str(e)}")
            return {"error": str(e)}

    async def download_video(self, url: str, filename: str = None) -> str:
        """Tải video thật (không logo) về máy."""
        if not filename:
            filename = "douyin_video"
            
        output_template = os.path.join(self.download_path, f"{filename}.%(ext)s")
        print(f"⬇️ [DouyinScraper] Downloading to: {output_template}")
        
        cmd = [
            "yt-dlp",
            "-f", "bestvideo+bestaudio/best",
            "-o", output_template,
            "--no-playlist",
            url
        ]
        
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            
            if proc.returncode != 0:
                print(f"❌ [DouyinScraper] Download error: {stderr.decode()}")
                return None
            
            # Tìm file thực tế được tải xuống (với phần mở rộng .mp4, .webm...)
            for file in os.listdir(self.download_path):
                if file.startswith(filename) and not file.endswith("_meta.json"):
                    return os.path.abspath(os.path.join(self.download_path, file))
                    
            return None
        except Exception as e:
            print(f"❌ [DouyinScraper] Download Exception: {str(e)}")
            return None
