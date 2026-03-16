import google.generativeai as genai
from typing import List, Dict, Optional
import json
import config

class AIRouter:
    """
    Cổng kết nối AI chính sử dụng Google Gemini.
    Đã được chuyển sang model GEMINI 2.0 FLASH cực mạnh.
    """
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        # Sử dụng model từ config.py (gemini-2.0-flash)
        self.model = genai.GenerativeModel(config.DEFAULT_MODEL)

    async def chat(self, messages: List[Dict[str, str]], context: Optional[str] = None) -> str:
        """
        Gửi yêu cầu tới Gemini.
        """
        system_prompt = f"""
        Bạn là kiến trúc sư AI cao cấp. 
        NHIỆM VỤ: Giúp người dùng viết code chất lượng cao, an toàn và chuyên nghiệp.
        BỐI CẢNH DỰ ÁN HIỆN TẠI:
        {context if context else 'Dự án mới'}
        
        QUY TẮC:
        - Luôn phản hồi code sạch, theo chuẩn production.
        - Nếu tạo code cho file cụ thể, hãy bọc trong tag: [FILE: path/to/file]<code>[/FILE]
        """
        
        user_input = messages[-1]['content']
        full_prompt = f"{system_prompt}\n\nUSER REQUEST: {user_input}"
        
        # Gọi Gemini và đợi phản hồi
        response = await self.model.generate_content_async(full_prompt)
        
        if response and response.text:
            return response.text
        return "AI không trả về kết quả."

    async def generate_project(self, prompt: str) -> Dict[str, str]:
        """
        Tạo toàn bộ cấu trúc file cho một project mới.
        """
        system_prompt = f"""
        Người dùng muốn tạo project: "{prompt}"
        Hãy trả về một JSON chứa toàn bộ cấu trúc project cần thiết.
        FORMAT: {{ "file_path": "file_content" }}
        CHỈ TRẢ VỀ JSON, KHÔNG GIẢI THÍCH.
        """
        
        response = await self.model.generate_content_async(system_prompt)
        full_text = response.text
        
        try:
            clean_json = full_text.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_json)
        except:
            return {"error": "AI returned invalid JSON structure"}
