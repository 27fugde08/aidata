from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.task_repository import TaskRepository
from app.schemas.task import TaskCreate, TaskUpdate
from app.models.all_models import Task, TaskStatus
from app.core.celery_app import celery_app
import logging

logger = logging.getLogger(__name__)

class TaskService:
    def __init__(self, db: AsyncSession):
        self.repository = TaskRepository(db)

    async def create_task(self, title: str, description: str = None) -> Task:
        task_in = TaskCreate(title=title, description=description)
        return await self.repository.create(task_in)

    async def get_task(self, task_id: int) -> Task:
        return await self.repository.get(task_id)

    async def list_tasks(self, skip: int = 0, limit: int = 100):
        return await self.repository.get_multi(skip, limit)

    async def trigger_process_task(self, task_id: int):
        """Pushes job to Redis queue for background processing."""
        task = await self.get_task(task_id)
        if not task:
            return {"error": f"Task {task_id} not found."}
        
        # Trigger Celery task
        # We specify the name explicitly as defined in task_handlers.py
        celery_app.send_task("tasks.process_task_job", args=[task_id])
        logger.info(f"Triggered process_task_job for task_id: {task_id}")
        return {"task_id": task_id, "status": "processing_queued"}

    async def trigger_video_translation(self, task_id: int):
        """Pushes video translation job to Redis queue."""
        task = await self.get_task(task_id)
        if not task:
            return {"error": f"Task {task_id} not found."}
        
        celery_app.send_task("tasks.process_video_translation", args=[task_id])
        logger.info(f"Triggered process_video_translation for task_id: {task_id}")
        return {"task_id": task_id, "status": "translation_queued"}

    async def get_task_status_info(self, task_id: int):
        task = await self.get_task(task_id)
        if not task:
            return {"error": "Task not found."}
        return {
            "id": task.id,
            "status": task.status,
            "result": task.result,
            "created_at": str(task.created_at)
        }
