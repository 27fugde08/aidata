import os
import asyncio
import google.generativeai as genai
from google.api_core import exceptions
from typing import List, Dict, Any, Optional
import sys
import tenacity

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from .resource_manager import ResourceManager
from .models.local_llm import LocalLLM
from .auth.key_manager import KeyManager
import config

class ModelOrchestrator:
    """
    Hệ thống điều phối đa mô hình (Multi-LLM) - Enhanced for AI Automation OS.
    Supports: Gemini, OpenAI, Claude, Local LLM (Ollama).
    Features: Routing, Fallback, Cost Optimization, Key Rotation.
    """
    def __init__(self, api_keys: Dict[str, str] = None, workspace_root: str = config.WORKSPACE_ROOT):
        # We now prioritize KeyManager over static api_keys dict
        self.key_manager = KeyManager()
        self.resources = ResourceManager(workspace_root)
        self.local_llm = LocalLLM(model_name=config.LOCAL_MODEL)
        
    async def chat(self, prompt: str, model: str = "gemini", system_instruction: str = "") -> str:
        """
        Gửi yêu cầu tới mô hình được chọn với cơ chế Fallback.
        Priority: Selected Model -> Local LLM (if cloud fails).
        """
        try:
            if model.startswith("gemini"):
                return await self._call_gemini_with_retry(prompt, model, system_instruction)
            elif model.startswith("gpt"):
                return await self._call_openai(prompt, model, system_instruction)
            elif model.startswith("claude"):
                return await self._call_claude(prompt, model, system_instruction)
            elif model == "local" or model.startswith("ollama"):
                 return await self.local_llm.generate_content_async(prompt, system_instruction)
            else:
                return f"Model {model} is not supported yet."
        except Exception as e:
            print(f"Error with model {model}: {e}. Falling back to Local LLM.")
            return await self.local_llm.generate_content_async(prompt, system_instruction)

    async def _call_gemini_with_retry(self, prompt: str, model_name: str, system_instruction: str) -> str:
        """Call Gemini with manual key rotation on 429."""
        retries = 3
        last_error = None
        
        for _ in range(retries):
            key = self.key_manager.get_key("gemini")
            if not key:
                raise Exception("No available Gemini API keys.")
                
            genai.configure(api_key=key)
            
            try:
                return await self._call_gemini_raw(prompt, model_name, system_instruction)
            except exceptions.ResourceExhausted:
                print(f"Gemini Key {key[:4]}... exhausted. Rotating...")
                self.key_manager.report_failure("gemini", key)
                continue # Retry with next key
            except Exception as e:
                last_error = e
                # For other errors, maybe don't rotate immediately, or do?
                # For now, just re-raise non-auth errors
                print(f"Gemini Error: {e}")
                raise e
        
        raise last_error or Exception("All retries failed")

    async def _call_gemini_raw(self, prompt: str, model_name: str, system_instruction: str) -> str:
        """Direct call to Gemini."""
        real_model_name = config.DEFAULT_MODEL if model_name == "gemini" else model_name
        model = genai.GenerativeModel(
            model_name=real_model_name,
            system_instruction=system_instruction
        )
        response = await model.generate_content_async(prompt)
        return response.text

    async def _call_openai(self, prompt: str, model_name: str, system_instruction: str) -> str:
        """Gọi OpenAI GPT API."""
        try:
            # Placeholder: Implement similar rotation logic for OpenAI if needed
            return f"OpenAI ({model_name}) integration pending."
        except Exception as e:
            raise e

    async def _call_claude(self, prompt: str, model_name: str, system_instruction: str) -> str:
        """Gọi Anthropic Claude API."""
        return f"Claude ({model_name}) integration in progress."

    def route_task(self, task_description: str) -> str:
        """
        Tự động chọn mô hình tốt nhất cho tác vụ cụ thể.
        Rules:
        - Privacy/Internal Data -> Local
        - Complex Logic -> Cloud (Gemini/GPT)
        - Simple/Fast -> Local
        """
        task_lower = task_description.lower()
        
        # Privacy & Simple tasks
        if any(keyword in task_lower for keyword in ["private", "local", "secret", "internal", "summarize", "simple"]):
            return "local"
            
        # Complex tasks
        if "complex logic" in task_lower or "architecture" in task_lower or "reasoning" in task_lower:
            return "gemini-2.0-flash" 
            
        return "gemini-1.5-flash"
