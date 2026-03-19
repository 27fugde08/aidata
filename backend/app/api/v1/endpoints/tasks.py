from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import List
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate
from app.services.task_service import TaskService
from app.api import deps

router = APIRouter()

@router.post("/", response_model=TaskResponse)
async def create_task(
    task_in: TaskCreate,
    service: TaskService = Depends(deps.get_task_service)
):
    return await service.create_task(task_in)

@router.get("/", response_model=List[TaskResponse])
async def list_tasks(
    skip: int = 0,
    limit: int = 100,
    service: TaskService = Depends(deps.get_task_service)
):
    return await service.list_tasks(skip, limit)

@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    service: TaskService = Depends(deps.get_task_service)
):
    task = await service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
