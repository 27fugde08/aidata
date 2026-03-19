import google.generativeai as genai
from app.core.config import settings
from app.services.task_service import TaskService
import logging

logger = logging.getLogger(__name__)

# Configure Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)

class AgentService:
    def __init__(self, task_service: TaskService):
        self.task_service = task_service
        
        # Updated tool definitions with better instructions
        
        async def create_task(title: str, description: str = ""):
            """
            Creates a new task in the database.
            Args:
                title: Title of the task
                description: A detailed description. IF A URL IS PROVIDED in the user prompt, IT MUST BE INCLUDED HERE.
            """
            logger.info(f"AI Tool Call: create_task({title})")
            task = await self.task_service.create_task(title, description)
            return {"id": task.id, "status": task.status}

        async def process_task(task_id: int):
            """
            Starts processing an existing task.
            Args:
                task_id: The ID of the task to process
            """
            logger.info(f"AI Tool Call: process_task({task_id})")
            return await self.task_service.trigger_process_task(task_id)

        async def get_task_status(task_id: int):
            """
            Checks the current status and results of a task.
            Args:
                task_id: The ID of the task
            """
            logger.info(f"AI Tool Call: get_task_status({task_id})")
            return await self.task_service.get_task_status_info(task_id)

        async def translate_video(task_id: int):
            """
            Translates and adds subtitles to a video using the automated pipeline.
            Args:
                task_id: The ID of the task to translate
            """
            logger.info(f"AI Tool Call: translate_video({task_id})")
            return await self.task_service.trigger_video_translation(task_id)

        self.model = genai.GenerativeModel(
            model_name=settings.GEMINI_MODEL,
            tools=[create_task, process_task, get_task_status, translate_video]
        )
        self.chat = self.model.start_chat(enable_automatic_function_calling=True)

    async def process_prompt(self, prompt: str) -> str:
        logger.info(f"Processing prompt: {prompt}")
        try:
            response = self.chat.send_message(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Agent Error: {e}")
            return f"I encountered an error while processing your request: {str(e)}"
