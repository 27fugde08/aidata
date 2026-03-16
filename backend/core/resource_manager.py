import os
import time
import datetime
from typing import Dict, List, Any
import sys

# Thêm đường dẫn gốc để import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

class ResourceManager:
    """
    Quản lý tài nguyên hệ thống (Hardware) và chi phí AI (Tokens).
    Theo dõi CPU, RAM và lưu lịch sử sử dụng.
    """
    def __init__(self, workspace_root: str):
        self.workspace_root = workspace_root
        self.stats_file = os.path.join(workspace_root, ".memory/resource_stats.json")
        self.token_usage = self._load_stats()

    def _load_stats(self) -> Dict[str, Any]:
        """Tải thông tin sử dụng token từ bộ nhớ."""
        if os.path.exists(self.stats_file):
            import json
            try:
                with open(self.stats_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return {"total_tokens": 0, "calls": [], "models": {}}
        return {"total_tokens": 0, "calls": [], "models": {}}

    def _save_stats(self):
        """Lưu thông tin sử dụng token."""
        import json
        os.makedirs(os.path.dirname(self.stats_file), exist_ok=True)
        with open(self.stats_file, "w", encoding="utf-8") as f:
            json.dump(self.token_usage, f, indent=2)

    def log_token_usage(self, model: str, prompt_tokens: int, completion_tokens: int):
        """Ghi lại số lượng token đã sử dụng cho một lần gọi AI."""
        total = prompt_tokens + completion_tokens
        self.token_usage["total_tokens"] += total
        
        if model not in self.token_usage["models"]:
            self.token_usage["models"][model] = 0
        self.token_usage["models"][model] += total
        
        self.token_usage["calls"].append({
            "timestamp": datetime.datetime.now().isoformat(),
            "model": model,
            "total": total
        })
        
        # Giới hạn lịch sử lưu trữ
        if len(self.token_usage["calls"]) > 100:
            self.token_usage["calls"].pop(0)
            
        self._save_stats()

    def get_hardware_stats(self) -> Dict[str, Any]:
        """Lấy thông số CPU và RAM hiện tại."""
        try:
            import psutil
            cpu = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            return {
                "cpu_percent": cpu,
                "ram_percent": memory.percent,
                "ram_used_gb": round(memory.used / (1024**3), 2),
                "ram_total_gb": round(memory.total / (1024**3), 2)
            }
        except ImportError:
            return {"error": "psutil not installed"}

    def get_token_summary(self) -> Dict[str, Any]:
        """Trả về tổng quan sử dụng token."""
        return {
            "total": self.token_usage["total_tokens"],
            "by_model": self.token_usage["models"]
        }
