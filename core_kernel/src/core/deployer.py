import os
import asyncio
import datetime
import json
from typing import Dict, List, Any
from .file_manager import FileManager
import config

class DeploymentEngine:
    """
    Hệ thống triển khai sản phẩm chuyên nghiệp.
    Quản lý phiên bản, môi trường và Docker container sản xuất.
    """
    def __init__(self, workspace_root: str):
        self.workspace_root = os.path.abspath(workspace_root)
        self.fm = FileManager(workspace_root)
        self.history_file = os.path.join(workspace_root, ".memory/deployment_history.json")
        self.deployments = self._load_history()

    def _load_history(self) -> List[Dict[str, Any]]:
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return []
        return []

    def _save_history(self):
        os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(self.deployments, f, indent=2)

    async def deploy(self, project_path: str, env: str = "production") -> Dict[str, Any]:
        """Quy trình triển khai đầy đủ: Build -> Config -> Run."""
        project_name = os.path.basename(project_path)
        deploy_id = f"dep-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        # 1. Phát hiện loại dự án
        project_type = self._detect_project_type(project_path)
        
        # 2. Tạo config môi trường (.env)
        self._ensure_env_config(project_path, env)
        
        # 3. Build Docker Image
        image_name = f"aios-prod-{project_name}:{env}"
        build_res = await self._build_image(project_path, image_name)
        
        if build_res["status"] == "success":
            # 4. Chạy Container sản xuất
            run_res = await self._run_container(image_name, project_name, env)
            status = "live" if run_res["status"] == "success" else "failed"
        else:
            run_res = {"output": "Build failed"}
            status = "failed"

        # Lưu lịch sử
        deploy_info = {
            "id": deploy_id,
            "project": project_name,
            "type": project_type,
            "env": env,
            "status": status,
            "timestamp": datetime.datetime.now().isoformat(),
            "image": image_name
        }
        self.deployments.append(deploy_info)
        self._save_history()
        
        return {**deploy_info, "logs": build_res["output"] + "\n" + run_res["output"]}

    def _detect_project_type(self, path: str) -> str:
        full_path = os.path.join(self.workspace_root, path)
        if os.path.exists(os.path.join(full_path, "package.json")): return "nodejs"
        if os.path.exists(os.path.join(full_path, "requirements.txt")): return "python"
        return "static"

    def _ensure_env_config(self, path: str, env: str):
        env_path = os.path.join(self.workspace_root, path, ".env")
        if not os.path.exists(env_path):
            content = f"ENVIRONMENT={env}\nAPP_NAME=AIOS_App\n"
            self.fm.write(f"{path}/.env", content)

    async def _build_image(self, path: str, image_name: str) -> Dict[str, Any]:
        # Giả lập build (Trong thực tế dùng docker build)
        await asyncio.sleep(2)
        return {"status": "success", "output": f"Successfully built {image_name}"}

    async def _run_container(self, image_name: str, name: str, env: str) -> Dict[str, Any]:
        # Giả lập run (Trong thực tế dùng docker run hoặc docker-compose)
        await asyncio.sleep(1)
        return {"status": "success", "output": f"Container {name} is running on port 8080"}

    def get_history(self) -> List[Dict[str, Any]]:
        return self.deployments
