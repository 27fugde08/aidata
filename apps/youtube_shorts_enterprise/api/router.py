from fastapi import APIRouter, Body
from typing import Dict, Any
from apps.youtube_shorts_enterprise.core.video_engine import YouTubeShortEngine

router = APIRouter(tags=["YouTube Enterprise"])
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
