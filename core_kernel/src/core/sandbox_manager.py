import os
import subprocess
import sys
import asyncio
from typing import Dict, Any, Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

class SandboxManager:
    """
    Quản lý việc thực thi mã an toàn trong Docker Sandbox.
    Hỗ trợ mount workspace, giới hạn tài nguyên và tự động dọn dẹp.
    """
    def __init__(self, workspace_root: str = config.WORKSPACE_ROOT):
        self.workspace_root = os.path.abspath(workspace_root)

    async def run_in_sandbox(self, command: str, image: str = config.DOCKER_IMAGE) -> Dict[str, Any]:
        """Thực thi lệnh trong Docker container và trả về kết quả."""
        if not config.ENABLE_DOCKER_SANDBOX:
            return await self._run_local(command)

        # Container name duy nhất
        import uuid
        container_name = f"aios-sandbox-{uuid.uuid4().hex[:8]}"
        
        # Lệnh docker run với mount volume
        docker_cmd = [
            "docker", "run", "--name", container_name,
            "-v", f"{self.workspace_root}:/workspace",
            "-w", "/workspace",
            "--network", "none", # Chặn internet cho an toàn (tùy chọn)
            "--memory", "512m",  # Giới hạn RAM
            image, "sh", "-c", command
        ]

        try:
            process = await asyncio.create_subprocess_exec(
                *docker_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            # Tự động xóa container sau khi chạy xong
            await asyncio.create_subprocess_exec("docker", "rm", "-f", container_name)
            
            return {
                "status": "success" if process.returncode == 0 else "failed",
                "stdout": stdout.decode(errors='replace').strip(),
                "stderr": stderr.decode(errors='replace').strip(),
                "exit_code": process.returncode
            }
        except Exception as e:
            return {"status": "error", "output": f"Sandbox Error: {str(e)}"}

    async def _run_local(self, command: str, cwd: str = None) -> Dict[str, Any]:
        """Dự phòng thực thi cục bộ nếu Docker bị tắt."""
        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.workspace_root
            )
            stdout, stderr = await process.communicate()
            return {
                "status": "success" if process.returncode == 0 else "failed",
                "stdout": stdout.decode(errors='replace').strip(),
                "stderr": stderr.decode(errors='replace').strip(),
                "exit_code": process.returncode
            }
        except Exception as e:
            return {"status": "error", "output": str(e)}

if __name__ == "__main__":
    # Test
    import asyncio
    async def test():
        sm = SandboxManager()
        res = await sm.run_shell_command("ls -la")
        print(res)
    
    # asyncio.run(test())
