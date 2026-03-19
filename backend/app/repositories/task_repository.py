from app.models.all_models import Task
from app.schemas.task import TaskCreate, TaskUpdate
from app.repositories.base_repository import BaseRepository
from sqlalchemy.ext.asyncio import AsyncSession

class TaskRepository(BaseRepository[Task, TaskCreate, TaskUpdate]):
    def __init__(self, db: AsyncSession):
        super().__init__(Task, db)
