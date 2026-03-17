from fastapi import APIRouter, Body, HTTPException
from typing import Dict, Any
from spaceofduy.projects.youtube_shorts_automation.backend.core.video_service import YouTubeShortsService

router = APIRouter(prefix="/v1/shorts", tags=["YouTube Shorts"])
service = YouTubeShortsService()

@router.post("/process-viral")
async def process_viral_video(data: dict = Body(...)):
    """
    Kích hoạt quy trình tạo video Shorts từ URL nguồn.
    """
    url = data.get("url")
    title = data.get("title", "Viral Short")
    
    if not url:
        raise HTTPException(status_code=400, detail="Source URL is required.")
        
    result = await service.process_video_mission(url, {"title": title, "task_id": "yt-" + os.urandom(4).hex()})
    return result

@router.get("/health")
def get_service_status():
    """Kiểm tra sức khỏe của YouTube Automation Service."""
    return service.get_stats()

import os # Cần cho os.urandom
