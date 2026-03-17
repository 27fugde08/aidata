import os
import asyncio
from core.sdk.plugin_base import AIOSPlugin
from typing import Dict, Any
import sys

# Đảm bảo có thể import các services của backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from services.video_engine import VideoEngine

class VideoGeneratorPlugin(AIOSPlugin):
    """
    Plugin xử lý video độc lập.
    Được thiết kế theo kiến trúc Plugin-First cho SaaS.
    """
    
    async def setup(self) -> bool:
        self.log("INFO", "Setting up Video Generator Plugin...")
        # Khởi tạo VideoEngine với workspace root
        self.video_engine = VideoEngine(self.workspace_root)
        return True

    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Nhận payload từ Agent hoặc API và thực thi tác vụ video.
        Payload: {"url": "...", "action": "viral_shorts" | "download" | "clip"}
        """
        action = payload.get("action", "viral_shorts")
        url = payload.get("url")
        
        if not self.video_engine:
            await self.setup()

        if action == "viral_shorts":
            if not url: return {"status": "error", "message": "URL is required"}
            self.log("INFO", f"Generating viral shorts for: {url}")
            
            # Tạo một ID duy nhất cho video (ví dụ từ URL hoặc random)
            video_id = url.split("v=")[-1].split("&")[0] if "v=" in url else "video_" + os.urandom(4).hex()
            
            try:
                shorts = await self.video_engine.process_viral_shorts(url, video_id)
                return {
                    "status": "success",
                    "plugin": self.plugin_id,
                    "shorts": shorts,
                    "video_id": video_id
                }
            except Exception as e:
                self.log("ERROR", f"Viral shorts generation failed: {str(e)}")
                return {"status": "error", "message": str(e)}

        elif action == "download":
            if not url: return {"status": "error", "message": "URL is required"}
            video_id = url.split("v=")[-1].split("&")[0] if "v=" in url else "video_" + os.urandom(4).hex()
            path = await self.video_engine.download_video(url, video_id)
            return {"status": "success", "path": path}

        return {"status": "error", "message": f"Unknown action: {action}"}

    async def shutdown(self) -> bool:
        self.log("INFO", "Shutting down Video Generator Plugin.")
        return True
