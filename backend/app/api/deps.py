from typing import AsyncGenerator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.task_service import TaskService
from app.services.agent_service import AgentService

async def get_task_service(db: AsyncSession = Depends(get_db)) -> TaskService:
    return TaskService(db)

async def get_agent_service(task_service: TaskService = Depends(get_task_service)) -> AgentService:
    return AgentService(task_service)
