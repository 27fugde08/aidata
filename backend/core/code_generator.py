from .ai_router import AIRouter
from .file_manager import FileManager
import re
from typing import Dict

class CodeGenerator:
    """
    Phối hợp AI và File System.
    Nhận prompt -> AI tạo code -> Ghi vào workspace.
    """
    def __init__(self, ai_router: AIRouter, file_manager: FileManager):
        self.ai = ai_router
        self.fm = file_manager

    async def apply_ai_request(self, prompt: str, current_file: str = None):
        """Xử lý yêu cầu tạo hoặc chỉnh sửa code."""
        context = ""
        if current_file:
            try:
                content = self.fm.read(current_file)
                context = f"FILE HIỆN TẠI ({current_file}):\n{content}"
            except:
                pass
        
        response = await self.ai.chat([{"role": "user", "content": prompt}], context)
        
        # Parse output for [FILE: path]<code>[/FILE] pattern
        files_created = []
        pattern = r"\[FILE:\s*(.*?)\](.*?)\[/FILE\]"
        matches = re.findall(pattern, response, re.DOTALL)
        
        if matches:
            for path, code in matches:
                self.fm.write(path.strip(), code.strip())
                files_created.append(path.strip())
        
        return {
            "response": response,
            "files_modified": files_created
        }

    async def create_new_project(self, prompt: str, project_name: str):
        """Tạo dự án mới dựa trên mô tả AI."""
        files = await self.ai.generate_project(prompt)
        
        for path, content in files.items():
            if path == "error": continue
            # Đảm bảo lưu trong thư mục dự án
            full_path = f"{project_name}/{path}"
            self.fm.write(full_path, content)
            
        return {"project": project_name, "files": list(files.keys())}
