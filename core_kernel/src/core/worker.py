import asyncio
from datetime import datetime
from core.task_queue.queue import TaskQueue, TaskStatus
from .task_executor import TaskExecutor
from .reflection_engine import ReflectionEngine

class AIOSWorker:
    """
    Vòng lặp nền xử lý các task AIOS tự động với khả năng Self-Reflection.
    """
    def __init__(self):
        self.queue = TaskQueue()
        self.reflector = ReflectionEngine()
        self.is_running = False

    async def start(self):
        if self.is_running:
            return
        self.is_running = True
        print("🚀 [Worker] AIOS Background Worker started with Self-Reflection.")
        
        while self.is_running:
            try:
                # Chờ task mới
                task_item = await self.queue.get_next_task()
                
                print(f"📦 [Worker] Dequeued task: {task_item.task} (ID: {task_item.id})")
                task_item.status = TaskStatus.RUNNING
                
                # 1. Lấy kinh nghiệm từ quá khứ
                past_lessons = self.reflector.get_past_context(task_item.task)
                print(f"📚 [Worker] Knowledge context: {past_lessons[:50]}...")
                
                # 2. Thực thi task
                result = await TaskExecutor.execute(task_item.task, task_item.params)
                
                # 3. Cập nhật kết quả
                task_item.status = TaskStatus.DONE
                task_item.result = result
                task_item.finished_at = datetime.now()
                
                # 4. Phản tỉnh (Self-Reflection)
                report = await self.reflector.reflect(task_item.task, task_item.status, result)
                print(f"✅ [Worker] Task completed. Reflection Insight: {report['insight']}")
                
            except Exception as e:
                print(f"❌ [Worker] Error processing task: {str(e)}")
            
            # Nghỉ ngơi ngắn giữa các vòng lặp (nếu cần)
            await asyncio.sleep(0.5)

    def stop(self):
        self.is_running = False
        print("🛑 [Worker] AIOS Background Worker stopped.")
