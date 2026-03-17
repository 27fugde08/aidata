import os
import sys
import asyncio
from fastapi import APIRouter, Body, BackgroundTasks, HTTPException
from typing import Dict, List, Optional
from pydantic import BaseModel
import config

# Thêm path để import core và services
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.instance import orchestrator
from services.video_engine import VideoEngine

router = APIRouter()
video_engine = VideoEngine(config.WORKSPACE_ROOT)

class VideoProcessRequest(BaseModel):
    url: str

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
async def process_video(req: VideoProcessRequest):
    """
    Hệ thống hóa lại quy trình xử lý video thông qua Orchestrator.
    Input: { "url": "youtube_link" }
    Return: { "task_id": "tid" }
    """
    try:
        payload = {"url": req.url, "action": "viral_shorts"}
        task_id = await orchestrator.enqueue_task("video_process", payload)
        return {"task_id": task_id, "status": "enqueued"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{task_id}")
async def get_task_status(task_id: str):
    """
    Lấy trạng thái xử lý video từ TaskQueue của Orchestrator.
    """
    from core.task_queue.queue import TaskStatus
    status = orchestrator.task_queue.get_task_status(task_id)
    if not status:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = orchestrator.task_queue.tasks.get(task_id)
    return {
        "task_id": task_id,
        "status": status.value,
        "created_at": task.created_at,
        "completed_at": task.completed_at,
        "error": task.error
    }

@router.get("/result/{task_id}")
async def get_task_result(task_id: str):
    """
    Lấy kết quả video đã xử lý từ spaceofduy dựa trên task_id.
    """
    from core.task_queue.queue import TaskStatus
    status = orchestrator.task_queue.get_task_status(task_id)
    if not status:
        raise HTTPException(status_code=404, detail="Task not found")
        
    if status != TaskStatus.COMPLETED:
        return {"status": status.value, "message": "Result not ready or task failed"}
    
    task = orchestrator.task_queue.tasks.get(task_id)
    return {
        "task_id": task_id,
        "result": task.output_data or {}
    }

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
