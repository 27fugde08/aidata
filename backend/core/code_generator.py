from .model_orchestrator import ModelOrchestrator
from .file_manager import FileManager
import re
from typing import Dict

class CodeGenerator:
    """
    Phối hợp AI và File System.
    Nhận prompt -> AI tạo code -> Ghi vào workspace.
    """
    def __init__(self, workspace_root: str):
        self.orchestrator = ModelOrchestrator(workspace_root=workspace_root)
        self.fm = FileManager(workspace_root)

    async def apply_ai_request(self, prompt: str, current_file: str = None):
        """Xử lý yêu cầu tạo hoặc chỉnh sửa code."""
        context = ""
        if current_file:
            try:
                content = self.fm.read(current_file)
                context = f"FILE HIỆN TẠI ({current_file}):\n{content}"
            except:
                pass
        
        # Determine if we should use local or cloud model
        model = self.orchestrator.route_task(f"coding task: {prompt}")
        response = await self.orchestrator.chat(prompt, model=model, system_instruction=context)
        
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
