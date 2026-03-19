import os
import asyncio
import json
import config
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from datetime import datetime

class Project(BaseModel):
    id: str
    name: str
    description: str
    status: str = "active"
    created_at: str = datetime.now().isoformat()

class Task(BaseModel):
    id: str
    project_id: str
    name: str
    status: str = "pending"  # pending, working, completed, failed
    progress: int = 0
    logs: List[str] = []

class StateManager:
    """
    Centralized State Manager for AIOS Kernel (2025 Architecture).
    Manages state of projects, tasks, and system events with JSON persistence.
    """
    def __init__(self):
        self.projects: Dict[str, Project] = {}
        self.tasks: Dict[str, Task] = {}
        self.event_queue = asyncio.Queue()
        
        # Đường dẫn lưu trữ
        self.state_file = os.path.join(config.WORKSPACE_ROOT, "db", "kernel_state.json")
        self._ensure_storage()
        self._load_state()

    def _ensure_storage(self):
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)

    def _load_state(self):
        """Tải dữ liệu từ file JSON nếu tồn tại."""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for p_id, p_data in data.get("projects", {}).items():
                        self.projects[p_id] = Project(**p_data)
                    for t_id, t_data in data.get("tasks", {}).items():
                        self.tasks[t_id] = Task(**t_data)
                print(f"📦 [State] Loaded {len(self.projects)} projects and {len(self.tasks)} tasks.")
            except Exception as e:
                print(f"❌ [State] Load failed: {e}")
        else:
            self._load_mock_data()
            self.save_state()

    def save_state(self):
        """Lưu trạng thái hiện tại vào file JSON."""
        try:
            data = {
                "projects": {k: v.dict() for k, v in self.projects.items()},
                "tasks": {k: v.dict() for k, v in self.tasks.items()},
                "last_updated": datetime.now().isoformat()
            }
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"❌ [State] Save failed: {e}")

    def _load_mock_data(self):
        if not self.projects:
            p1 = Project(id="p_001", name="AIOS Default", description="Dự án mặc định của hệ thống")
            self.projects[p1.id] = p1

    async def add_event(self, event_type: str, data: Any):
        """Adds a system event (log, trace, etc.) to the broadcast queue."""
        event = {
            "type": event_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        await self.event_queue.put(event)

    async def get_events(self):
        """Generator for SSE broadcasting."""
        while True:
            event = await self.event_queue.get()
            yield f"data: {json.dumps(event)}\n\n"

# Singleton instance
state_manager = StateManager()
