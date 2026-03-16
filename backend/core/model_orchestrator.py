import os
import asyncio
import google.generativeai as genai
from typing import List, Dict, Any, Optional
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from .resource_manager import ResourceManager
import config

class ModelOrchestrator:
    """
    Hệ thống điều phối đa mô hình (Multi-LLM).
    Cho phép chuyển đổi linh hoạt giữa Gemini, OpenAI, Claude và Local models.
    Tích hợp theo dõi token.
    """
    def __init__(self, api_keys: Dict[str, str] = None, workspace_root: str = config.WORKSPACE_ROOT):
        self.api_keys = api_keys or {
            "gemini": config.GEMINI_API_KEY,
            "openai": os.getenv("OPENAI_API_KEY", ""),
            "anthropic": os.getenv("ANTHROPIC_API_KEY", "")
        }
        self.resources = ResourceManager(workspace_root)
        self._setup_providers()

    def _setup_providers(self):
        """Cấu hình các SDK của các nhà cung cấp."""
        if self.api_keys.get("gemini"):
            genai.configure(api_key=self.api_keys["gemini"])

    async def chat(self, prompt: str, model: str = "gemini", system_instruction: str = "") -> str:
        """Gửi yêu cầu tới mô hình được chọn."""
        if model.startswith("gemini"):
            return await self._call_gemini(prompt, model, system_instruction)
        elif model.startswith("gpt"):
            return await self._call_openai(prompt, model, system_instruction)
        elif model.startswith("claude"):
            return await self._call_claude(prompt, model, system_instruction)
        else:
            return f"Model {model} is not supported yet."

    async def _call_gemini(self, prompt: str, model_name: str, system_instruction: str) -> str:
        """Gọi Google Gemini API."""
        try:
            model = genai.GenerativeModel(
                model_name=model_name if model_name != "gemini" else config.DEFAULT_MODEL,
                system_instruction=system_instruction
            )
            response = await model.generate_content_async(prompt)
            return response.text
        except Exception as e:
            return f"Gemini Error: {str(e)}"

    async def _call_openai(self, prompt: str, model_name: str, system_instruction: str) -> str:
        """Gọi OpenAI GPT API."""
        # Placeholder cho OpenAI SDK (Yêu cầu thư viện 'openai')
        try:
            # import openai
            # client = openai.AsyncOpenAI(api_key=self.api_keys["openai"])
            # response = await client.chat.completions.create(...)
            return f"OpenAI ({model_name}) is being integrated. API Key found: {bool(self.api_keys['openai'])}"
        except Exception as e:
            return f"OpenAI Error: {str(e)}"

    async def _call_claude(self, prompt: str, model_name: str, system_instruction: str) -> str:
        """Gọi Anthropic Claude API."""
        # Placeholder cho Anthropic SDK
        return f"Claude ({model_name}) integration in progress."

    def route_task(self, task_description: str) -> str:
        """Tự động chọn mô hình tốt nhất cho tác vụ cụ thể."""
        if "complex logic" in task_description or "architecture" in task_description:
            return "gpt-4o"
        if "coding" in task_description or "debug" in task_description:
            return "claude-3-5-sonnet"
        return "gemini-2.0-flash"
