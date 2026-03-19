from fastapi import APIRouter, Depends
from app.schemas.task import AgentRequest
from app.services.agent_service import AgentService
from app.api import deps

router = APIRouter()

@router.post("/run")
async def run_agent(
    request: AgentRequest,
    service: AgentService = Depends(deps.get_agent_service)
):
    """
    Main AIOS endpoint:
    Processes natural language prompts, executes AI reasoning loop,
    triggers database and queue operations, and returns final response.
    """
    response = await service.process_prompt(request.prompt)
    return {"response": response}
