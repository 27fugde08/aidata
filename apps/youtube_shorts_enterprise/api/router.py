from fastapi import APIRouter, Body
from typing import Dict, Any
from spaceofduy.projects.youtube_shorts_automation_enterprise.backend.core.video_engine import YouTubeShortEngine

router = APIRouter(prefix="/yt-enterprise", tags=["YouTube Enterprise"])
engine = YouTubeShortEngine()

@router.post("/create")
async def create_yt_short(data: dict = Body(...)):
    """
    Endpoint tạo video Short tự động.
    """
    url = data.get("url")
    title = data.get("title", "AI Generated Short")
    
    result = await engine.create_short(url, title)
    return result

@router.get("/status")
def check_engine_status():
    return {"status": "operational", "engine": "YouTubeShortEngine v2.0"}
