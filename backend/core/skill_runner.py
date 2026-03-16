import subprocess
import sys
import os
import asyncio
from typing import Dict, Any

class SkillRunner:
    """
    Thực thi code Python và lệnh hệ thống.
    Hỗ trợ chạy async để không làm treo Backend.
    """
    def __init__(self, workspace_root: str):
        self.workspace_root = os.path.abspath(workspace_root)

    async def run_python_script(self, rel_path: str) -> Dict[str, Any]:
        """Chạy một file Python và trả về kết quả."""
        full_path = os.path.abspath(os.path.join(self.workspace_root, rel_path))
        
        # Bảo mật: Không cho phép chạy file ngoài workspace
        if not full_path.startswith(self.workspace_root):
            return {"status": "error", "output": "Access denied: Path outside workspace"}

        if not os.path.exists(full_path):
            return {"status": "error", "output": f"File not found: {rel_path}"}

        try:
            # Thực thi file bằng Python hiện tại
            process = await asyncio.create_subprocess_exec(
                sys.executable, full_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=os.path.dirname(full_path)
            )

            stdout, stderr = await process.communicate()
            
            return {
                "status": "success" if process.returncode == 0 else "failed",
                "exit_code": process.returncode,
                "stdout": stdout.decode().strip(),
                "stderr": stderr.decode().strip()
            }
        except Exception as e:
            return {"status": "error", "output": str(e)}

    async def run_shell_command(self, command: str, cwd: str = None) -> Dict[str, Any]:
        """Chạy lệnh shell (pip install, git, vv)."""
        # Đảm bảo cwd luôn nằm trong workspace_root
        if cwd:
            target_cwd = os.path.abspath(os.path.join(self.workspace_root, cwd))
            if not target_cwd.startswith(self.workspace_root):
                return {"status": "error", "output": "Access denied: Target directory is outside workspace"}
        else:
            target_cwd = self.workspace_root
        
        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=target_cwd
            )

            stdout, stderr = await process.communicate()
            
            return {
                "status": "success" if process.returncode == 0 else "failed",
                "stdout": stdout.decode().strip(),
                "stderr": stderr.decode().strip()
            }
        except Exception as e:
            return {"status": "error", "output": str(e)}
