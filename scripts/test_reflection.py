import asyncio
import os
import sys

# Đảm bảo import được các module từ backend
sys.path.append(os.path.join(os.getcwd(), "backend"))

from core.task_queue import TaskQueue
from core.worker import AIOSWorker

async def run_reflection_test():
    worker = AIOSWorker()
    queue = TaskQueue()
    
    task_name = "update_os_health_ui"
    print(f"🚀 [Test] Adding task: {task_name}")
    
    # 1. Thêm task vào hàng đợi
    task_id = await queue.add_task(task_name, {})
    
    # 2. Chạy worker một vòng lặp để xử lý task
    # (Vì worker.start() là vòng lặp vô tận, tôi sẽ simulate xử lý)
    task_item = await queue.get_next_task()
    print(f"📦 [Test] Dequeued: {task_item.task}")
    
    # 3. Logic Reflection trong Worker
    # (Tôi sẽ gọi các phương thức giống như Worker thực tế)
    from core.task_executor import TaskExecutor
    from core.reflection_engine import ReflectionEngine
    
    reflector = ReflectionEngine()
    
    # Lấy kinh nghiệm cũ
    past = reflector.get_past_context(task_name)
    print(f"📚 [Test] Past context: {past[:50]}...")
    
    # Thực thi
    result = await TaskExecutor.execute(task_name, {})
    
    # Phản tỉnh (Self-Reflection)
    report = await reflector.reflect(task_name, "done", result)
    print(f"✅ [Test] Reflection Insight: {report['insight']}")
    print(f"✅ [Test] Reflection Improvement: {report['improvement']}")

if __name__ == "__main__":
    asyncio.run(run_reflection_test())
