import asyncio
import uuid
import datetime
import json
import os
from enum import Enum
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field, asdict

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class Task:
    id: str
    description: str
    role: str
    priority: int = 0
    status: TaskStatus = TaskStatus.PENDING
    created_at: str = field(default_factory=lambda: datetime.datetime.now().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    parent_id: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)

class TaskQueue:
    """
    Advanced task queue for AI Automation OS.
    Supports priorities, dependencies, and persistence.
    """
    def __init__(self, workspace_root: str):
        self.workspace_root = workspace_root
        self.queue_path = os.path.join(workspace_root, ".memory/task_queue.json")
        self.tasks: Dict[str, Task] = {}
        self._load_queue()
        self.lock = asyncio.Lock()

    def _load_queue(self):
        if os.path.exists(self.queue_path):
            try:
                with open(self.queue_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for tid, tdata in data.items():
                        tdata["status"] = TaskStatus(tdata["status"])
                        self.tasks[tid] = Task(**tdata)
            except Exception as e:
                print(f"Error loading task queue: {e}")

    async def _save_queue(self):
        os.makedirs(os.path.dirname(self.queue_path), exist_ok=True)
        async with self.lock:
            data = {tid: asdict(t) for tid, t in self.tasks.items()}
            # Convert Enum to string for JSON serialization
            for tid in data:
                data[tid]["status"] = data[tid]["status"].value
            
            with open(self.queue_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

    async def add_task(self, description: str, role: str, priority: int = 0, 
                       input_data: Dict[str, Any] = None, dependencies: List[str] = None) -> str:
        tid = str(uuid.uuid4())[:8]
        task = Task(
            id=tid,
            description=description,
            role=role,
            priority=priority,
            input_data=input_data or {},
            dependencies=dependencies or []
        )
        self.tasks[tid] = task
        await self._save_queue()
        return tid

    async def get_next_task(self) -> Optional[Task]:
        async with self.lock:
            # Sort by priority (high first) and creation time
            pending_tasks = [t for t in self.tasks.values() if t.status == TaskStatus.PENDING]
            
            # Filter tasks whose dependencies are not completed
            ready_tasks = []
            for t in pending_tasks:
                all_deps_done = True
                for dep_id in t.dependencies:
                    if dep_id in self.tasks and self.tasks[dep_id].status != TaskStatus.COMPLETED:
                        all_deps_done = False
                        break
                if all_deps_done:
                    ready_tasks.append(t)

            if not ready_tasks:
                return None
                
            ready_tasks.sort(key=lambda x: (-x.priority, x.created_at))
            next_task = ready_tasks[0]
            next_task.status = TaskStatus.RUNNING
            next_task.started_at = datetime.datetime.now().isoformat()
            
            return next_task

    async def update_task(self, tid: str, status: TaskStatus, output_data: Dict[str, Any] = None, error: str = None):
        if tid in self.tasks:
            task = self.tasks[tid]
            task.status = status
            if status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                task.completed_at = datetime.datetime.now().isoformat()
            if output_data:
                task.output_data = output_data
            if error:
                task.error = error
            await self._save_queue()

    def get_task_status(self, tid: str) -> Optional[TaskStatus]:
        if tid in self.tasks:
            return self.tasks[tid].status
        return None
