from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import psutil
import os
import sys

# Thêm đường dẫn để import core
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.state_manager import state_manager

router = APIRouter()

@router.get("/stream")
async def stream_events():
    """SSE Endpoint để stream sự kiện hệ thống, log và trạng thái theo thời gian thực."""
    return StreamingResponse(state_manager.get_events(), media_type="text/event-stream")

@router.get("/health")
async def get_health():
    """Lấy thông số sức khỏe hệ thống thực tế."""
    cpu_percent = psutil.cpu_percent()
    memory = psutil.virtual_memory()
    
    return {
        "status": "success",
        "data": {
            "cpu": cpu_percent,
            "ram": {
                "total": round(memory.total / (1024**3), 2),
                "used": round(memory.used / (1024**3), 2),
                "percent": memory.percent
            },
            "projects_count": len(state_manager.projects),
            "tasks_count": len(state_manager.tasks)
        }
    }
