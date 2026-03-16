import os
import sys
import asyncio
from fastapi import APIRouter, Body, BackgroundTasks, HTTPException
from typing import Dict, List
import config

# Thêm path để import core và services
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.video_engine import VideoEngine

router = APIRouter()
video_engine = VideoEngine(config.WORKSPACE_ROOT)

# Progress tracking
processing_results = {}

@router.get("/projects")
async def list_projects():
    """Liệt kê các project video (dựa trên folder data)."""
    data_dir = video_engine.data_dir
    if not os.path.exists(data_dir):
        return {"projects": []}
    
    projects = []
    for f in os.listdir(data_dir):
        if f.endswith(".mp4"):
            video_id = f.replace(".mp4", "")
            projects.append({
                "id": video_id,
                "title": f"Project {video_id}",
                "status": "completed" if video_id not in processing_results else "processing"
            })
    return {"projects": projects}

@router.get("/project/{video_id}")
async def get_project_details(video_id: str):
    """Lấy danh sách shorts thuộc về video_id."""
    shorts_dir = video_engine.output_dir
    shorts = []
    if os.path.exists(shorts_dir):
        import json
        for f in os.listdir(shorts_dir):
            if f.startswith(f"viral_{video_id}_") and f.endswith(".json"):
                try:
                    with open(os.path.join(shorts_dir, f), "r", encoding="utf-8") as jf:
                        shorts.append(json.load(jf))
                except: pass
    return {"project": {"id": video_id, "title": f"Project {video_id}"}, "shorts": shorts}

@router.get("/last-result/{video_id}")
async def get_last_result(video_id: str):
    return processing_results.get(video_id, {"status": "idle"})

@router.post("/process")
async def process_video(background_tasks: BackgroundTasks, data: Dict = Body(...)):
    url = data.get("url")
    video_id = data.get("id")
    
    if not url or not video_id:
        raise HTTPException(status_code=400, detail="Missing url or id")

    async def update_callback(step: str, progress: int):
        processing_results[video_id] = {
            "status": "processing",
            "step": step,
            "progress": progress
        }

    async def run_pipeline():
        try:
            shorts = await video_engine.process_viral_shorts(url, video_id, callback=update_callback)
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

@router.get("/shorts/list")
def list_all_shorts():
    """Liệt kê toàn bộ shorts có trong hệ thống."""
    shorts_dir = video_engine.output_dir
    if not os.path.exists(shorts_dir):
        return {"shorts": []}
    
    import json
    shorts = []
    for f in os.listdir(shorts_dir):
        if f.endswith(".json"):
            try:
                with open(os.path.join(shorts_dir, f), "r", encoding="utf-8") as jf:
                    shorts.append(json.load(jf))
            except: pass
    return {"shorts": shorts}
