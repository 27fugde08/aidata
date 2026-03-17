import json
import os
from datetime import datetime
from typing import Dict, Any, List

class DevMemory:
    """Persistent storage for Dev Missions and Lessons Learned."""
    def __init__(self, memory_path: str = "backend/memory/dev_logs.json"):
        self.memory_path = memory_path
        os.makedirs(os.path.dirname(self.memory_path), exist_ok=True)
        if not os.path.exists(self.memory_path):
            with open(self.memory_path, "w") as f:
                json.dump({"history": [], "lessons_learned": []}, f)

    def _load(self) -> Dict[str, Any]:
        with open(self.memory_path, "r") as f:
            return json.load(f)

    def _save(self, data: Dict[str, Any]):
        with open(self.memory_path, "w") as f:
            json.dump(data, f, indent=4)

    def log_task(self, task_id: str, plan: List[str], final_code: str, status: str, feedback: str):
        data = self._load()
        entry = {
            "task_id": task_id,
            "timestamp": datetime.now().isoformat(),
            "plan": plan,
            "status": status,
            "feedback": feedback
        }
        data["history"].append(entry)
        if status == "failed":
            data["lessons_learned"].append(f"Avoid error: {feedback}")
        self._save(data)

    def get_context(self) -> str:
        data = self._load()
        lessons = "\n".join(data["lessons_learned"][-5:])
        return f"Past Lessons:\n{lessons}" if lessons else "No past errors recorded."
