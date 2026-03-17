import os
from fastapi import APIRouter, Body
from typing import Dict
from tiktok_uploader.upload import upload_video

router = APIRouter()

@router.post("/tiktok")
async def publish_to_tiktok(data: Dict = Body(...)):
    video_path = data.get("video_path") # Đường dẫn file mp4
    description = data.get("description", "Automated AI Shorts #ai #shorts")
    
    # Đường dẫn file cookies (người dùng cần chuẩn bị cookies.txt)
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
    cookies_path = os.path.join(root, "cookies.txt")
    
    if not os.path.exists(video_path):
        return {"status": "error", "message": "Video file not found."}
        
    if not os.path.exists(cookies_path):
        return {"status": "error", "message": "cookies.txt not found. Please follow documentation to export cookies."}

    try:
        # Thực hiện upload
        # Lưu ý: Quá trình này có thể tốn thời gian, nên chạy trong background task
        upload_video(
            video_path,
            description=description,
            cookies=cookies_path,
            browser='chrome'
        )
        return {"status": "success", "message": "Video uploaded successfully to TikTok!"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
