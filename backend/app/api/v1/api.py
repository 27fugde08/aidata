from fastapi import APIRouter
from app.api.v1.endpoints import tasks, agent

api_router = APIRouter()
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(agent.router, prefix="/agent", tags=["agent"])
