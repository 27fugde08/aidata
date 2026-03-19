import os
from fastapi import APIRouter, Body, BackgroundTasks
from typing import Dict, List
from apps.youtube_shorts.core.project_service import ProjectService

router = APIRouter()
project_service = ProjectService()

# Biến tạm để lưu progress cho UI tương thích ngược
processing_results = {}

@router.get("/projects")
async def list_projects():
    return {"projects": project_service.get_all_projects()}

@router.get("/project/{video_id}")
async def get_project(video_id: str):
    return project_service.get_project_details(video_id)

@router.get("/last-result/{video_id}")
async def get_last_result(video_id: str):
    return processing_results.get(video_id, {"status": "idle"})

@router.post("/process")
async def process_video(background_tasks: BackgroundTasks, data: Dict = Body(...)):
    url = data.get("url")
    video_id = data.get("id")
    
    # Hàm callback để cập nhật tiến trình
    async def update_progress(step: str, progress: int):
        processing_results[video_id] = {
            "status": "processing",
            "step": step,
            "progress": progress
        }
    
    async def run_pipeline():
        try:
            shorts = await project_service.start_full_pipeline(url, video_id, callback=update_progress)
            processing_results[video_id] = {
                "status": "completed",
                "step": "Hoàn tất",
                "progress": 100,
                "details": shorts
            }
        except Exception as e:
            processing_results[video_id] = {
                "status": "error",
                "message": str(e)
            }

    background_tasks.add_task(run_pipeline)
    return {"status": "started", "video_id": video_id}

@router.post("/merge")
async def merge_clips(data: Dict = Body(...)):
    clip_names = data.get("clips", []) # Danh sách tên file (không có .mp4)
    output_name = data.get("output_name", "merged_compilation")
    
    # Xây dựng đường dẫn file thực tế
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
    clip_paths = [os.path.join(root, f"outputs/shorts/{name}.mp4") for name in clip_names]
    
    # Kiểm tra tồn tại
    valid_paths = [p for p in clip_paths if os.path.exists(p)]
    if not valid_paths:
        return {"status": "error", "message": "Không tìm thấy clip nào hợp lệ để gộp."}
        
    try:
        from apps.youtube_shorts.services.video_service import VideoService
        vs = VideoService()
        merged_path = await vs.concatenate_clips(valid_paths, output_name)
        return {"status": "success", "video_url": f"/outputs/{output_name}.mp4"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
