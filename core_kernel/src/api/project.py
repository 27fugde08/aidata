from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
import uuid
import sys
import os

# Thêm đường dẫn để import core
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.state_manager import state_manager, Project

router = APIRouter()

class ProjectCreate(BaseModel):
    name: str
    description: str

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None

@router.get("/")
async def list_projects():
    """Lấy danh sách tất cả các dự án."""
    return {
        "status": "success",
        "data": list(state_manager.projects.values())
    }

@router.post("/")
async def create_project(req: ProjectCreate, background_tasks: BackgroundTasks):
    """Tạo dự án mới."""
    new_id = f"p_{uuid.uuid4().hex[:8]}"
    project = Project(id=new_id, name=req.name, description=req.description)
    state_manager.projects[new_id] = project
    state_manager.save_state()
    
    # Gửi sự kiện hệ thống để frontend cập nhật qua SSE
    background_tasks.add_task(state_manager.add_event, "project_created", project.dict())
    
    return {
        "status": "success",
        "message": f"Project '{req.name}' created successfully.",
        "data": project
    }

@router.patch("/{project_id}")
async def update_project(project_id: str, req: ProjectUpdate, background_tasks: BackgroundTasks):
    """Cập nhật thông tin dự án."""
    if project_id not in state_manager.projects:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = state_manager.projects[project_id]
    update_data = req.dict(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(project, key, value)
    
    state_manager.save_state()
    background_tasks.add_task(state_manager.add_event, "project_updated", project.dict())
    return {"status": "success", "data": project}

@router.delete("/{project_id}")
async def delete_project(project_id: str, background_tasks: BackgroundTasks):
    """Xóa một dự án."""
    if project_id not in state_manager.projects:
        raise HTTPException(status_code=404, detail="Project not found")
    
    deleted_project = state_manager.projects.pop(project_id)
    state_manager.save_state()
    background_tasks.add_task(state_manager.add_event, "project_deleted", {"id": project_id})
    return {"status": "success", "message": f"Project {project_id} deleted."}
