import ollama
from typing import List, Dict, Any, Optional

class LocalLLM:
    """
    Wrapper for Ollama (Local LLM Inference).
    Mimics the interface of cloud providers for easy swapping.
    """
    def __init__(self, model_name: str = "mistral"):
        self.model_name = model_name
        self.check_availability()

    def check_availability(self):
        """Checks if Ollama is running and the model is pulled."""
        try:
            ollama.list()
        except Exception:
            print(f"Warning: Ollama service not detected. Local LLM {self.model_name} may fail.")

    async def generate_content_async(self, prompt: str, system_instruction: str = "") -> str:
        """
        Generates content using the local model.
        """
        try:
            messages = []
            if system_instruction:
                messages.append({"role": "system", "content": system_instruction})
            
            messages.append({"role": "user", "content": prompt})

            response = ollama.chat(model=self.model_name, messages=messages)
            return response['message']['content']
        except Exception as e:
            return f"Local LLM Error ({self.model_name}): {str(e)}"

    def generate_content(self, prompt: str, system_instruction: str = "") -> str:
        """Sync version."""
        try:
            messages = []
            if system_instruction:
                messages.append({"role": "system", "content": system_instruction})
            
            messages.append({"role": "user", "content": prompt})

            response = ollama.chat(model=self.model_name, messages=messages)
            return response['message']['content']
        except Exception as e:
            return f"Local LLM Error ({self.model_name}): {str(e)}"
