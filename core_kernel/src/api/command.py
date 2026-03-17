from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, List
from core.command_parser import CommandParser
from core.task_queue.queue import TaskQueue

router = APIRouter(prefix="/api/command", tags=["AIOS Command System"])
task_queue = TaskQueue()

class CommandRequest(BaseModel):
    command: str

class CommandResponse(BaseModel):
    status: str
    message: str
    task_id: str = None
    parsed_data: Dict[str, Any] = None

@router.post("/execute", response_model=CommandResponse)
async def execute_command(request: CommandRequest):
    """
    Nhận lệnh (VD: "/aios run update_os_health_ui") và đưa vào hàng đợi xử lý.
    """
    # 1. Parse lệnh
    parsed = CommandParser.parse(request.command)
    if not parsed:
        raise HTTPException(status_code=400, detail="Invalid command format. Use: /aios run <task_name>")
    
    # 2. Đưa vào hàng đợi
    task_id = await task_queue.add_task(parsed["task"], parsed["params"])
    
    return CommandResponse(
        status="success",
        message=f"Command '{parsed['task']}' accepted and queued.",
        task_id=task_id,
        parsed_data=parsed
    )

@router.get("/tasks")
async def list_tasks():
    """Liệt kê trạng thái tất cả các task trong hệ thống."""
    tasks = task_queue.get_all_tasks()
    return [{"id": t.id, "task": t.task, "status": t.status, "result": t.result, "created_at": t.created_at} for t in tasks]
