from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import sys
import os

# Thêm đường dẫn gốc để import core và config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.ai_router import AIRouter
from core.file_manager import FileManager
from core.code_reviewer import CodeReviewer
import config # Import cấu hình mới

router = APIRouter()

# Lấy cài đặt từ file config.py
fm = FileManager(config.WORKSPACE_ROOT)
ai = AIRouter(config.GEMINI_API_KEY)
reviewer = CodeReviewer(ai, fm)

class ReviewRequest(BaseModel):
    file_path: str

@router.post("/file")
async def review_file(req: ReviewRequest):
    """API sử dụng AI để kiểm tra file code."""
    result = await reviewer.review_file(req.file_path)
    return result
