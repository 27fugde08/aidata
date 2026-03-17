import asyncio
import json
import datetime
import os
from typing import List, Dict, Any, Callable, Coroutine

class EventEngine:
    """
    Hệ thống điều phối dựa trên sự kiện (Event-Driven Engine).
    Cho phép đăng ký listeners cho các sự kiện như FILE_CHANGE, WEBHOOK, TASK_DONE.
    """
    def __init__(self, log_file: str = "logs/system.log"):
        self.listeners: Dict[str, List[Callable]] = {}
        self.event_history: List[Dict[str, Any]] = []
        self.log_file = log_file
        
        # Ensure log directory exists
        log_dir = os.path.dirname(self.log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

    def subscribe(self, event_type: str, callback: Callable):
        """Đăng ký một hàm xử lý cho loại sự kiện."""
        if event_type not in self.listeners:
            self.listeners[event_type] = []
        self.listeners[event_type].append(callback)

    async def emit(self, event_type: str, data: Any):
        """Phát một sự kiện vào hệ thống."""
        event_obj = {
            "type": event_type,
            "data": data,
            "timestamp": datetime.datetime.now().isoformat()
        }
        self.event_history.append(event_obj)
        if len(self.event_history) > 100:
            self.event_history.pop(0)
            
        # Write to log file
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(event_obj) + "\n")
        except Exception as e:
            # Fallback to console if file logging fails
            print(f"Error writing to log: {e}")

        if event_type in self.listeners:
            tasks = []
            for callback in self.listeners[event_type]:
                if asyncio.iscoroutinefunction(callback):
                    tasks.append(callback(data))
                else:
                    callback(data)
            
            if tasks:
                await asyncio.gather(*tasks)

    def get_history(self) -> List[Dict[str, Any]]:
        return self.event_history

# Khởi tạo instance duy nhất (Singleton pattern cho event bus)
events = EventEngine()
