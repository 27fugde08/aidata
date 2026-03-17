import os
import json
import asyncio
from typing import Dict, List, Any
import datetime

class MonitoringDashboard:
    """
    AI Monitoring Dashboard Backend.
    Provides data for the frontend to visualize active agents, costs, and mission status.
    """
    def __init__(self, workspace_root: str):
        self.workspace_root = workspace_root
        self.stats_path = os.path.join(workspace_root, ".memory/dashboard_stats.json")

    async def get_system_summary(self) -> Dict[str, Any]:
        """Collects stats from all memory modules."""
        stats = {
            "timestamp": datetime.datetime.now().isoformat(),
            "active_agents": self._get_active_agents_count(),
            "missions": self._get_mission_stats(),
            "projects": self._get_project_count(),
            "api_usage": self._get_usage_estimate(),
            "global_knowledge": self._get_knowledge_stats()
        }
        return stats

    def _get_active_agents_count(self) -> int:
        # Placeholder (this would track runtime agent instances)
        return 7

    def _get_mission_stats(self) -> Dict[str, Any]:
        queue_path = os.path.join(self.workspace_root, ".memory/task_queue.json")
        if os.path.exists(queue_path):
            try:
                with open(queue_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    total = len(data)
                    completed = sum(1 for t in data.values() if t["status"] == "completed")
                    return {"total": total, "completed": completed, "pending": total - completed}
            except: pass
        return {"total": 0, "completed": 0, "pending": 0}

    def _get_project_count(self) -> int:
        db_path = os.path.join(self.workspace_root, ".memory/projects_db.json")
        if os.path.exists(db_path):
            try:
                with open(db_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return len(data)
            except: pass
        return 0

    def _get_usage_estimate(self) -> Dict[str, float]:
        # Placeholder for cost tracking
        return {"cloud_api": 0.45, "local_inference": 0.0}

    def _get_knowledge_stats(self) -> Dict[str, Any]:
        brain_path = os.path.join(self.workspace_root, ".memory/brain_summary.json")
        if os.path.exists(brain_path):
            try:
                with open(brain_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except: pass
        return {"total_insights": 0}
