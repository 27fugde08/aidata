from .ai_router import AIRouter
from .file_manager import FileManager
from typing import Dict, List

class CodeReviewer:
    """
    Sử dụng AI để kiểm tra chất lượng code và bảo mật.
    """
    def __init__(self, ai_router: AIRouter, file_manager: FileManager):
        self.ai = ai_router
        self.fm = file_manager

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
            
            response_text = await self.ai.chat([{"role": "user", "content": prompt}])
            
            import json
            # Làm sạch chuỗi JSON từ AI
            clean_json = response_text.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_json)
        except Exception as e:
            return {"error": str(e), "summary": "Không thể phân tích file này."}
