from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import os
import sys

# Thêm đường dẫn gốc để import core và config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.instance import orchestrator
from core.file_manager import FileManager
from core.code_generator import CodeGenerator
import config

router = APIRouter()

# Use shared generator or its components
generator = CodeGenerator(config.WORKSPACE_ROOT)
# Override generator's orchestrator to use the shared one
generator.orchestrator = orchestrator.model_router

class GenerateRequest(BaseModel):
    prompt: str
    current_file: Optional[str] = None

@router.post("/")
async def generate_code(req: GenerateRequest):
    try:
        res = await generator.apply_ai_request(req.prompt, req.current_file)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/prompt")
async def generate_code(req: GenerateRequest):
    try:
        result = await generator.apply_ai_request(req.prompt, req.current_file)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
