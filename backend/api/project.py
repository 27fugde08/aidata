from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os
import sys

# Thêm đường dẫn để import core
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.file_manager import FileManager

router = APIRouter()
WORKSPACE_ROOT = "spaceofduy"
fm = FileManager(WORKSPACE_ROOT)

class ProjectCreate(BaseModel):
    name: str
    template: str
    description: str

@router.post("/create")
async def create_project(req: ProjectCreate):
    proj_path = req.name.strip().replace(" ", "_")
    try:
        fm.write(f"{proj_path}/README.md", f"# Project: {req.name}\n\n{req.description}")
        return {"status": "success", "project_path": proj_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list")
def list_projects():
    if not os.path.exists(WORKSPACE_ROOT):
        os.makedirs(WORKSPACE_ROOT)
    return {"projects": [d for d in os.listdir(WORKSPACE_ROOT) if os.path.isdir(os.path.join(WORKSPACE_ROOT, d))]}
