from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None

class TaskCreate(TaskBase):
    pass

class TaskUpdate(TaskBase):
    status: Optional[str] = None
    result: Optional[Dict[str, Any]] = None

class TaskInDB(TaskBase):
    id: int
    status: str
    result: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    owner_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)

class TaskResponse(TaskInDB):
    pass

class AgentRequest(BaseModel):
    prompt: str
