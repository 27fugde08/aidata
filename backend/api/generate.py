from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import os
import sys

# Thêm đường dẫn gốc để import core và config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.ai_router import AIRouter
from core.file_manager import FileManager
from core.code_generator import CodeGenerator
import config # Import cấu hình mới

router = APIRouter()

# Lấy cài đặt từ file config.py
fm = FileManager(config.WORKSPACE_ROOT)
ai = AIRouter(config.GEMINI_API_KEY)
generator = CodeGenerator(ai, fm)

class GenerateRequest(BaseModel):
    prompt: str
    current_file: Optional[str] = None

@router.post("/prompt")
async def generate_code(req: GenerateRequest):
    try:
        result = await generator.apply_ai_request(req.prompt, req.current_file)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
