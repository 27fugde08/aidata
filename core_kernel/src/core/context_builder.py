import os
import sys
from typing import List, Dict, Any, Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from .memory_manager import MemoryManager
from .vector_memory import VectorMemory
import config

class ContextBuilder:
    """
    Hệ thống xây dựng ngữ cảnh thông minh cho AI.
    Kết hợp:
    1. Bộ nhớ JSON (Cấu trúc dự án, mục tiêu)
    2. Vector Memory (Truy xuất nội dung liên quan)
    3. File Content (Nội dung file đang mở)
    """
    def __init__(self, workspace_root: str = config.WORKSPACE_ROOT):
        self.workspace_root = workspace_root
        self.memory = MemoryManager(workspace_root)
        self.vector = VectorMemory()

    async def build_context(self, prompt: str, current_file: str = None) -> str:
        """Xây dựng chuỗi Context tối ưu cho LLM."""
        
        # 1. Lấy thông tin dự án cơ bản
        project_info = self.memory.get_context()
        
        # 2. Truy xuất tri thức liên quan từ Vector DB
        vector_res = await self.vector.search(prompt, top_k=2)
        vector_context = "\n".join([f"- {res['text']}" for res in vector_res])
        
        # 3. Thông tin file hiện tại (nếu có)
        file_context = ""
        if current_file:
            try:
                path = os.path.join(self.workspace_root, current_file)
                if os.path.exists(path):
                    with open(path, "r", encoding="utf-8") as f:
                        file_context = f"CURRENT FILE ({current_file}):\n{f.read()}\n"
            except:
                pass

        # Kết hợp tất cả
        context = f"""
{project_info}

RELEVANT KNOWLEDGE (Vector Search):
{vector_context if vector_context else 'No relevant background found.'}

{file_context}

USER REQUEST: {prompt}
"""
        return context

if __name__ == "__main__":
    # Test
    import asyncio
    async def test():
        cb = ContextBuilder()
        ctx = await cb.build_context("Làm thế nào để thêm API mới?")
        print(ctx)
    
    # asyncio.run(test())
