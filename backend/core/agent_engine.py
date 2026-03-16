import os
import asyncio
import json
import google.generativeai as genai
from typing import List, Dict, Any, Optional
import sys

# Thêm đường dẫn gốc để import core và config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from .file_manager import FileManager
from .sandbox_manager import SandboxManager
from .memory_manager import MemoryManager
from .context_builder import ContextBuilder
from .vector_memory import VectorMemory
from .knowledge_graph import KnowledgeGraph
from .model_orchestrator import ModelOrchestrator

class AgentEngine:
    def __init__(self, workspace_root: str, api_key: Optional[str] = None):
        self.fm = FileManager(workspace_root)
        self.sandbox = SandboxManager(workspace_root)
        self.memory = MemoryManager(workspace_root)
        self.context_builder = ContextBuilder(workspace_root)
        self.vector = VectorMemory()
        self.graph = KnowledgeGraph(workspace_root)
        self.orchestrator = ModelOrchestrator() # Hệ thống Multi-LLM
        
        self.api_key = api_key or config.GEMINI_API_KEY
        
        # Thêm công cụ query graph
        self.tools = [
            self.list_files,
            self.read_file,
            self.write_file,
            self.run_command,
            self.debug_code,
            self.update_project_memory,
            self.query_knowledge_graph
        ]
        
        self.reload_model()

    def query_knowledge_graph(self, file_path: str = ""):
        """AI truy vấn bản đồ tri thức để tìm quan hệ giữa các file/class."""
        if not file_path:
            return json.dumps(self.graph.build_graph(), indent=2)
        return json.dumps(self.graph.query_relations(file_path), indent=2)

    def reload_model(self):
        """Khởi tạo lại model với tools thông qua Google Generative AI."""
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(
            model_name=config.DEFAULT_MODEL,
            tools=self.tools
        )

    # --- Tool Definitions ---

    def update_project_memory(self, description: str):
        """AI tự cập nhật mô tả dự án và mục tiêu vào bộ nhớ."""
        self.memory.update_description(description)
        # Đồng thời lưu vào Vector Memory
        asyncio.create_task(self.vector.add_text(f"Project Goal Update: {description}", {"type": "goal"}))
        return "Project memory updated successfully."

    def list_files(self, path: str = "") -> str:
        """Liệt kê danh sách file trong thư mục."""
        try:
            tree = self.fm.list_tree(path)
            return json.dumps(tree, indent=2)
        except Exception as e:
            return f"Error listing files: {str(e)}"

    def read_file(self, path: str) -> str:
        """Đọc nội dung của một file."""
        try:
            content = self.fm.read(path)
            # Tự động index nội dung file quan trọng vào Vector Memory
            if len(content) < 5000:
                asyncio.create_task(self.vector.add_text(f"File Content ({path}):\n{content}", {"path": path, "type": "code"}))
            return content
        except Exception as e:
            return f"Error reading file {path}: {str(e)}"

    def write_file(self, path: str, content: str, reason: str = "Updating project files") -> str:
        """Ghi nội dung vào một file. Yêu cầu giải thích lý do (reason)."""
        try:
            self.fm.write(path, content)
            self.memory.add_action(f"AI ghi file: {path}. Lý do: {reason}")
            # Index thay đổi vào Vector Memory
            asyncio.create_task(self.vector.add_text(f"File Updated ({path}): {reason}", {"path": path, "type": "update"}))
            return f"Successfully wrote to {path}"
        except Exception as e:
            return f"Error writing to {path}: {str(e)}"

    async def run_command(self, command: str, reason: str = "Executing system task") -> str:
        """Chạy lệnh terminal qua Sandbox (Docker hoặc Local)."""
        result = await self.sandbox.run_shell_command(command)
        
        if result.get("stderr") or result.get("status") == "failed":
             return f"COMMAND FAILED (Exit Code {result.get('exit_code')}): \nSTDOUT: {result.get('stdout')}\nSTDERR: {result.get('stderr')}\n\nHÃY PHÂN TÍCH VÀ SỬA LỖI."
        
        self.memory.add_action(f"AI chạy lệnh: {command}. Lý do: {reason}")
        output = f"SUCCESS:\n{result.get('stdout', '')}"
        return output

    async def debug_code(self, file_path: str, error_message: str) -> str:
        """Tự động phân tích lỗi và đề xuất cách sửa cho file cụ thể."""
        content = self.read_file(file_path)
        prompt = f"FILE: {file_path}\nCONTENT:\n{content}\n\nERROR:\n{error_message}\n\nHãy phân tích lỗi và trả về mã nguồn đã sửa. Nếu cần sửa, hãy dùng tool write_file."
        return prompt 

    async def _retry_llm_call(self, chat_session, prompt: str, retries: int = 3, delay: int = 2):
        """Thực hiện retry cho LLM call nếu gặp lỗi mạng hoặc quá tải."""
        last_exception = None
        for attempt in range(retries):
            try:
                return await chat_session.send_message_async(prompt)
            except Exception as e:
                last_exception = e
                # Log warning (could use EventEngine here but keeping it simple for now)
                print(f"LLM Call failed (Attempt {attempt+1}/{retries}): {e}")
                await asyncio.sleep(delay * (attempt + 1))
        raise last_exception

    # --- Execution Loop ---

    async def work_stream(self, prompt: str):
        """Phiên bản stream tích hợp Context Builder và Vector Memory."""
        chat = self.model.start_chat(enable_automatic_function_calling=True)
        
        # 1. Xây dựng ngữ cảnh thông minh (Smart Context Retrieval)
        yield f"⏳ Đang truy xuất tri thức từ Vector Memory cho: '{prompt[:30]}...' \n"
        smart_context = await self.context_builder.build_context(prompt)

        system_instruction = f"""
        BẠN LÀ AGENT AI CAO CẤP (ENTERPRISE EDITION).
        
        NGỮ CẢNH HỆ THỐNG (SMART CONTEXT):
        {smart_context}
        
        NHIỆM VỤ: Thực hiện yêu cầu người dùng dựa trên tri thức đã truy xuất.
        
        QUY TẮC SANDBOX:
        - Mọi lệnh terminal được thực thi qua Sandbox (Docker={config.ENABLE_DOCKER_SANDBOX}).
        - Nếu chạy Docker, bạn có môi trường '{config.DOCKER_IMAGE}' an toàn.
        
        QUY TRÌNH:
        1. 📋 Plan: Trả về kế hoạch thực hiện.
        2. ⏳ Execute: Gọi các công cụ cần thiết.
        3. 🔍 Verify: Kiểm tra kết quả qua log terminal.
        """
        
        full_prompt = f"{system_instruction}\n\nUSER REQUEST: {prompt}"
        
        try:
            # Sử dụng retry mechanism
            response = await self._retry_llm_call(chat, full_prompt)
            yield response.text
            
            # Lưu lịch sử hội thoại vào Vector Memory để "nhớ" lâu dài
            asyncio.create_task(self.vector.add_text(f"Chat History: User asked '{prompt}'. AI replied.", {"type": "history"}))
            
            yield "\n🏁 Done: Yêu cầu đã được thực hiện xong."
        except Exception as e:
            yield f"\n❌ Agent Error: {str(e)}"
