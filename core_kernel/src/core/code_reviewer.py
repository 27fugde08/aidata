from .model_orchestrator import ModelOrchestrator
from .file_manager import FileManager
from typing import Dict, List
import json

class CodeReviewer:
    """
    Sử dụng AI để kiểm tra chất lượng code và bảo mật.
    Uses ModelOrchestrator for advanced reasoning.
    """
    def __init__(self, workspace_root: str):
        self.model_orchestrator = ModelOrchestrator(workspace_root=workspace_root)
        self.fm = FileManager(workspace_root)

    async def review_file(self, file_path: str) -> Dict:
        """Kiểm tra một file cụ thể."""
        try:
            content = self.fm.read(file_path)
            
            prompt = f"""
            Hãy đóng vai một chuyên gia bảo mật và kiến trúc sư phần mềm (Senior Security Engineer).
            PHÂN TÍCH FILE: {file_path}
            NỘI DUNG CODE:
            {content}
            
            NHIỆM VỤ:
            1. Tìm các lỗ hổng bảo mật (API Keys, SQL Injection, Hardcoded secrets).
            2. Tìm lỗi logic hoặc code chưa tối ưu.
            3. Đề xuất cách sửa cụ thể.
            
            TRẢ VỀ KẾT QUẢ DƯỚI DẠNG JSON:
            {{
                "score": 0-100,
                "issues": [
                    {{"type": "security|logic|style", "severity": "high|medium|low", "description": "...", "fix": "..."}}
                ],
                "summary": "..."
            }}
            CHỈ TRẢ VỀ JSON.
            """
            
            # Use high-performance model for review
            model = self.model_orchestrator.route_task("security review and code analysis")
            response_text = await self.model_orchestrator.chat(prompt, model=model)
            
            # Làm sạch chuỗi JSON từ AI
            clean_json = response_text.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_json)
        except Exception as e:
            return {"error": str(e), "summary": "Không thể phân tích file này."}
