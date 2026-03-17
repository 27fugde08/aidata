from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, List
from spaceofduy.projects.douyin_automation.backend.models.douyin_models import DouyinVideoRequest, DouyinVideoResponse, DownloadRequest
from spaceofduy.projects.douyin_automation.backend.services.douyin_service import DouyinService

router = APIRouter(prefix="/douyin", tags=["Douyin"])
douyin_service = DouyinService()

@router.post("/info", response_model=DouyinVideoResponse)
async def get_video_info(request: DouyinVideoRequest):
    """Lấy thông tin video Douyin thực tế (bao gồm link không logo)."""
    info = await douyin_service.get_video_details(request.url)
    if not info or "error" in info:
        raise HTTPException(status_code=400, detail=info.get("error", "Could not extract video info"))
    return info

@router.post("/download")
async def download_video(request: DownloadRequest):
    """Tải video Douyin thực tế về server."""
    file_path = await douyin_service.download_real_video(request.url, request.video_id, request.filename)
    if not file_path:
        raise HTTPException(status_code=500, detail="Download failed")
    return {"status": "success", "file_path": file_path}

@router.get("/status/{video_id}")
async def get_download_status(video_id: str):
    """Kiểm tra trạng thái tải video (Mockup)."""
    # Logic thực tế có thể kiểm tra trong file hệ thống hoặc database
    return {"status": "completed", "id": video_id}
