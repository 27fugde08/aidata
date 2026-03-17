import os
import json
import datetime
from typing import Dict, Any, List

class MemoryManager:
    """
    Quản lý bộ nhớ của AI về dự án.
    Lưu trữ cấu trúc, mục tiêu và lịch sử thay đổi.
    """
    def __init__(self, workspace_root: str):
        self.workspace_root = workspace_root
        self.memory_file = os.path.join(workspace_root, ".ai_memory.json")
        self.load_memory()

    def load_memory(self):
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, "r", encoding="utf-8") as f:
                    self.memory = json.load(f)
            except:
                self.memory = self._get_default_memory()
        else:
            self.memory = self._get_default_memory()

    def _get_default_memory(self) -> Dict[str, Any]:
        return {
            "project_name": os.path.basename(self.workspace_root),
            "description": "Dự án mới khởi tạo",
            "key_features": [],
            "recent_actions": [],
            "last_indexed": ""
        }

    def save_memory(self):
        self.memory["last_indexed"] = datetime.datetime.now().isoformat()
        with open(self.memory_file, "w", encoding="utf-8") as f:
            json.dump(self.memory, f, indent=4, ensure_ascii=False)

    def add_action(self, action: str):
        """Lưu lại hành động quan trọng của AI."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.memory["recent_actions"].append(f"[{timestamp}] {action}")
        # Chỉ giữ lại 20 hành động gần nhất
        self.memory["recent_actions"] = self.memory["recent_actions"][-20:]
        self.save_memory()

    def update_description(self, description: str):
        self.memory["description"] = description
        self.save_memory()

    def get_project_context(self) -> str:
        """Tạo chuỗi context để gửi cho AI."""
        actions = "\n".join(self.memory["recent_actions"])
        return f"""
PROJECT CONTEXT:
- Name: {self.memory['project_name']}
- Description: {self.memory['description']}
- Recent History:
{actions if actions else 'Chưa có hành động nào.'}
"""
