import asyncio
import json
import httpx
from typing import AsyncGenerator, List, Dict, Any, Optional
from core.logger import logger

class LLMService:
    """
    Dịch vụ kết nối LLM tập trung, hỗ trợ Async Streaming và Error Handling.
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        # Mặc định sử dụng cấu trúc tương thích với Gemini/OpenAI
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"

    async def stream_chat(self, prompt: str, system_instruction: str = "You are a helpful AIOS assistant.") -> AsyncGenerator[str, None]:
        """
        Stream phản hồi từ LLM dưới dạng từng token.
        """
        if not self.api_key:
            yield "❌ Lỗi: Chưa cấu hình API Key trong Settings."
            return

        payload = {
            "model": "gpt-4o", # Map to gemini-1.5-pro in your proxy if needed
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt}
            ],
            "stream": True
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                async with client.stream("POST", self.base_url, json=payload, headers=headers) as response:
                    if response.status_code != 200:
                        error_detail = await response.aread()
                        yield f"❌ LLM API Error ({response.status_code}): {error_detail.decode()}"
                        return

                    async for line in response.aiter_lines():
                        if not line or not line.startswith("data: "):
                            continue
                        
                        data_str = line[6:]
                        if data_str == "[DONE]":
                            break
                            
                        try:
                            data = json.loads(data_str)
                            token = data['choices'][0]['delta'].get('content', '')
                            if token:
                                yield token
                        except:
                            continue
        except Exception as e:
            logger.error(f"LLM Stream Error: {e}")
            yield f"❌ Connection Error: {str(e)}"

    async def get_json_response(self, prompt: str, schema_name: str) -> Dict[str, Any]:
        """
        Lấy phản hồi có cấu trúc JSON (Dùng cho Manager/Evaluator).
        """
        # Logic giả lập hoặc gọi LLM với JSON mode
        # Ở phiên bản này, ta sẽ dùng prompt engineering để lấy JSON
        full_prompt = f"{prompt}\n\nReturn ONLY a valid JSON following the schema of {schema_name}. No preamble."
        
        response_text = ""
        async for chunk in self.stream_chat(full_prompt, "You are a structured data generator."):
            if not chunk.startswith("❌"):
                response_text += chunk
        
        try:
            # Tìm JSON trong block ```json ... ``` nếu có
            import re
            json_match = re.search(r'(\{.*\})', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            return json.loads(response_text)
        except Exception as e:
            logger.error(f"JSON Parse Error: {e} | Raw: {response_text}")
            return {"error": "Failed to parse LLM response as JSON", "raw": response_text}
