from fastapi import APIRouter
from pydantic import BaseModel
import sys
import os

# Import Celery App
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from worker import run_agent_task, celery_app

router = APIRouter()

class TaskRequest(BaseModel):
    type: str  # video_render, ai_research
    payload: dict = {}

@router.get("/")
async def get_queue_health():
    """Kiểm tra sức khỏe của Task Queue."""
    return {"status": "success", "worker_pool": "celery", "active": True}

@router.post("/submit")
async def submit_task(req: TaskRequest):
    """
    Gửi một tác vụ vào hàng đợi phân tán (Redis).
    Worker Swarm sẽ tự động nhận và xử lý.
    """
    task = run_agent_task.delay(req.type, req.payload)
    return {
        "status": "queued",
        "task_id": task.id,
        "message": "Task submitted to AIOS Worker Swarm."
    }

@router.get("/status/{task_id}")
async def get_task_status(task_id: str):
    """Kiểm tra trạng thái tác vụ."""
    res = celery_app.AsyncResult(task_id)
    return {
        "task_id": task_id,
        "status": res.status,
        "result": res.result if res.ready() else None
    }
