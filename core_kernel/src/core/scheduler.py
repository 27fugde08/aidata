import os
import asyncio
import uuid
import datetime
from typing import List, Dict, Any, Optional

class AgentOSProcess:
    """Định nghĩa một tiến trình Agent trong hệ điều hành AI."""
    def __init__(self, name: str, task_func, args: tuple = (), priority: int = 1):
        self.pid = str(uuid.uuid4())[:8]
        self.name = name
        self.task_func = task_func
        self.args = args
        self.priority = priority
        self.status = "PENDING" # PENDING, RUNNING, PAUSED, COMPLETED, KILLED
        self.created_at = datetime.datetime.now()
        self.started_at = None
        self.ended_at = None
        self.result = None
        self._task = None # asyncio.Task object

    def to_dict(self):
        return {
            "pid": self.pid,
            "name": self.name,
            "priority": self.priority,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "result": str(self.result) if self.result else None
        }

class AgentOSScheduler:
    """Bộ điều phối tiến trình (Scheduler) cho AI OS."""
    def __init__(self):
        self.processes = {} # pid: AgentOSProcess
        self.queue = asyncio.PriorityQueue()

    async def spawn(self, name: str, func, args: tuple = (), priority: int = 1) -> str:
        """Tạo một tiến trình mới."""
        process = AgentOSProcess(name, func, args, priority)
        self.processes[process.pid] = process
        # Thêm vào hàng đợi (ưu tiên thấp hơn số nhỏ hơn)
        await self.queue.put((priority, process))
        return process.pid

    async def run_worker(self):
        """Worker loop xử lý hàng đợi tiến trình."""
        while True:
            priority, process = await self.queue.get()
            if process.status == "KILLED":
                self.queue.task_done()
                continue
            
            process.status = "RUNNING"
            process.started_at = datetime.datetime.now()
            
            try:
                if asyncio.iscoroutinefunction(process.task_func):
                    process.result = await process.task_func(*process.args)
                else:
                    process.result = process.task_func(*process.args)
                process.status = "COMPLETED"
            except Exception as e:
                process.status = "FAILED"
                process.result = str(e)
            finally:
                process.ended_at = datetime.datetime.now()
                self.queue.task_done()

    def kill_process(self, pid: str):
        """Dừng một tiến trình."""
        if pid in self.processes:
            self.processes[pid].status = "KILLED"
            # Lưu ý: Việc dừng asyncio.Task đang chạy thực sự yêu cầu xử lý phức tạp hơn
            return True
        return False

    def list_processes(self) -> List[Dict[str, Any]]:
        """Liệt kê tất cả tiến trình."""
        return [p.to_dict() for p in self.processes.values()]
