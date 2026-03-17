import uuid
import asyncio
from typing import Dict, Any, List, Optional
from enum import Enum
from datetime import datetime

class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"

class TaskItem:
    def __init__(self, task_name: str, params: Dict[str, Any]):
        self.id = str(uuid.uuid4())
        self.task = task_name
        self.params = params
        self.status = TaskStatus.PENDING
        self.created_at = datetime.now()
        self.finished_at: Optional[datetime] = None
        self.result: Optional[str] = None

class TaskQueue:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(TaskQueue, cls).__new__(cls)
            cls._instance.queue = asyncio.Queue()
            cls._instance.registry: Dict[str, TaskItem] = {}
        return cls._instance

    async def add_task(self, task_name: str, params: Dict[str, Any]) -> str:
        task = TaskItem(task_name, params)
        self.registry[task.id] = task
        await self.queue.put(task)
        return task.id

    async def get_next_task(self) -> TaskItem:
        return await self.queue.get()

    def get_task_status(self, task_id: str) -> Optional[TaskItem]:
        return self.registry.get(task_id)

    def get_all_tasks(self) -> List[TaskItem]:
        return list(self.registry.values())
