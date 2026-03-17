from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
import sys

# Đảm bảo đường dẫn gốc được nhận diện
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.skill_runner import SkillRunner

router = APIRouter()
WORKSPACE_ROOT = "spaceofduy"
runner = SkillRunner(WORKSPACE_ROOT)

class RunRequest(BaseModel):
    file_path: str

class ShellRequest(BaseModel):
    command: str
    cwd: str = ""

@router.post("/run-script")
async def run_script(req: RunRequest):
    result = await runner.run_python_script(req.file_path)
    return result

@router.post("/run-shell")
async def run_shell(req: ShellRequest):
    result = await runner.run_shell_command(req.command, req.cwd)
    return result
