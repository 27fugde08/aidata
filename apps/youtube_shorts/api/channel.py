from fastapi import APIRouter, Body
from typing import Dict, List
from spaceofduy.projects.youtube_shorts_automation.backend.services.video_service import VideoService

router = APIRouter()
video_service = VideoService()

@router.post("/scan")
async def scan_channel(data: Dict = Body(...)):
    url = data.get("url")
    videos = await video_service.scan_channel(url)
    return {"status": "success", "videos": videos}
