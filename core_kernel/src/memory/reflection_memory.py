import json
import os
from datetime import datetime
from typing import List, Dict, Any

class ReflectionMemory:
    def __init__(self, file_path: str = "backend/memory/learnings.json"):
        self.file_path = file_path
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        if not os.path.exists(self.file_path):
            self._save({"learnings": []})

    def _load(self) -> Dict[str, Any]:
        with open(self.file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save(self, data: Dict[str, Any]):
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def add_learning(self, task_name: str, status: str, insight: str, improvement: str):
        data = self._load()
        data["learnings"].append({
            "timestamp": datetime.now().isoformat(),
            "task": task_name,
            "status": status,
            "insight": insight,
            "improvement": improvement
        })
        # Giữ lại 50 bài học gần nhất để tránh file quá lớn
        data["learnings"] = data["learnings"][-50:]
        self._save(data)

    def get_learnings_for_task(self, task_name: str) -> str:
        data = self._load()
        relevant = [l for l in data["learnings"] if l["task"] == task_name or task_name in l["improvement"]]
        if not relevant:
            return "No previous experience for this task."
        
        context = "--- PAST REFLECTIONS ---\n"
        for l in relevant[-3:]: # Lấy 3 bài học gần nhất
            context += f"- Result: {l['status']}\n  Insight: {l['insight']}\n  Action: {l['improvement']}\n"
        return context
