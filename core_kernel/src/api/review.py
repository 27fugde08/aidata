from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import sys
import os

# Thêm đường dẫn gốc để import core và config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.model_orchestrator import ModelOrchestrator
from core.file_manager import FileManager
from core.code_reviewer import CodeReviewer
import config

router = APIRouter()

# Unified AI Automation OS Core
orchestrator = ModelOrchestrator(workspace_root=config.WORKSPACE_ROOT)
reviewer = CodeReviewer(config.WORKSPACE_ROOT)

class ReviewRequest(BaseModel):
    file_path: str

@router.post("/file")
async def review_file(req: ReviewRequest):
    try:
        res = await reviewer.review_file(req.file_path)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    """API sử dụng AI để kiểm tra file code."""
    result = await reviewer.review_file(req.file_path)
    return result
