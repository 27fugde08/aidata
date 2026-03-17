import os
import time
from celery import Celery
from dotenv import load_dotenv

# Load env
load_dotenv()

# Redis URL defaults to localhost if not in Docker
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Initialize Celery
celery_app = Celery(
    "aios_worker",
    broker=REDIS_URL,
    backend=REDIS_URL
)

# Configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    worker_concurrency=int(os.getenv("WORKER_CONCURRENCY", 2)) # Default 2 threads per container
)

@celery_app.task(bind=True)
def run_agent_task(self, task_type: str, payload: dict):
    """
    Tác vụ chạy Agent trong môi trường phân tán.
    Đây là nơi các 'Worker' thực sự làm việc.
    """
    print(f"🚀 [Worker] Received task: {task_type} | ID: {self.request.id}")
    
    # Giả lập xử lý nặng (Video Rendering, AI Thinking)
    # Trong thực tế, chúng ta sẽ gọi AgentEngine hoặc VideoService ở đây
    
    if task_type == "video_render":
        total_steps = 5
        for i in range(total_steps):
            time.sleep(2) # Giả lập render tốn thời gian
            self.update_state(state='PROGRESS', meta={'current': i, 'total': total_steps})
            print(f"⚙️ [Worker] Rendering... {i+1}/{total_steps}")
            
    elif task_type == "ai_research":
        time.sleep(5)
        print("🧠 [Worker] AI Research complete.")
        
    return {"status": "success", "result": f"Processed {task_type}"}
