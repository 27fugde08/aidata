from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import sys
import os

# Thêm đường dẫn gốc để import core
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.file_manager import FileManager
from core.deployer import DeploymentEngine

router = APIRouter()
WORKSPACE_ROOT = "spaceofduy"
fm = FileManager(WORKSPACE_ROOT)
deployer = DeploymentEngine(WORKSPACE_ROOT)

class DeployRequest(BaseModel):
    project_path: str # e.g. "my_bot"
    project_type: str = "python"
    image_name: str = "my_app_image"

@router.post("/build-docker")
async def build_docker(req: DeployRequest):
    """API tự động tạo Dockerfile và build image."""
    # 1. Tạo Dockerfile trước
    msg = deployer.generate_dockerfile(req.project_path, req.project_type)
    
    # 2. Xây dựng Docker Image (Không chạy nếu Duy chưa cài Docker)
    result = await deployer.build_docker_image(req.project_path, req.image_name)
    
    return {
        "status": result["status"],
        "dockerfile_status": msg,
        "build_output": result["output"]
    }
