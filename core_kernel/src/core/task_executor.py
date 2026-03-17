import asyncio
from typing import Dict, Any, Optional
from agents.pipeline.dev_pipeline import DevPipeline
from core.logger import logger

class TaskExecutor:
    """
    Thực hiện các task khác nhau trong hệ thống AIOS.
    Bao gồm các task mô phỏng và các task AI Agent phức tạp.
    """
    # Khởi tạo pipeline dev cho các nhiệm vụ lập trình
    dev_pipeline = DevPipeline()

    @staticmethod
    async def execute(task_name: str, params: Dict[str, Any]) -> str:
        logger.info(f"⚙️ [Executor] Analyzing command: {task_name}")
        
        # 1. Nhận diện các task liên quan đến Phát triển phần mềm (Dev Missions)
        # Hỗ trợ cả: build_..., dev_..., hoặc build (với params)
        if task_name.startswith("build") or task_name.startswith("dev"):
            # Nếu task_name chỉ là "build", ta lấy project name từ params
            prompt = task_name
            if task_name == "build" and "raw_args" in params:
                prompt = f"build_{params['raw_args'].strip()}"
            
            logger.info(f"🚀 [Executor] Triggering DevPipeline for: {prompt}")
            
            # Kích hoạt hệ thống Multi-Agent (Manager -> Coder -> Evaluator)
            result = await TaskExecutor.dev_pipeline.run_mission(
                task_id=params.get("task_id", "aios-dev-mission"),
                prompt=prompt
            )
            
            return f"DEV MISSION {result['status'].upper()}: {result.get('feedback', 'Completed')}"

        # 2. Các task hệ thống mô phỏng (Mock tasks)
        if task_name == "update_os_health_ui":
            await asyncio.sleep(2)
            return "SUCCESS: OS Health UI updated to latest metrics."
            
        elif task_name == "optimize_system_monitor":
            await asyncio.sleep(2)
            return "SUCCESS: System monitor optimized."
            
        elif task_name == "cleanup_logs":
            return "SUCCESS: Logs cleared."
            
        else:
            # Fallback: Nếu không khớp task nào, ta vẫn có thể dùng AI để "thử" thực hiện
            logger.warning(f"⚠️ [Executor] Task '{task_name}' not found. Attempting AI reasoning...")
            return f"ERROR: Task '{task_name}' is not registered in the system."
