from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime

class TaskStatus(str, Enum):
    PENDING = "pending"
    PLANNING = "planning"
    EXECUTING = "executing"
    REVIEWING = "reviewing"
    OPTIMIZING = "optimizing"
    DONE = "done"
    FAILED = "failed"

class TaskLog(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.now)
    agent: str
    message: str
    data: Optional[Dict[str, Any]] = None

class AIOS_Task(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    logs: List[TaskLog] = []
    result: Optional[str] = None
    reflection: Optional[Dict[str, str]] = None # insight, improvement
    created_at: datetime = Field(default_factory=datetime.now)

class CommandRequest(BaseModel):
    command: str
    context: Optional[Dict[str, Any]] = None

class CommandResponse(BaseModel):
    status: str
    task_id: str
    message: str
    meta: Optional[Dict[str, Any]] = None
