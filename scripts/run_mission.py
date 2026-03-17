import asyncio
import os
import sys

# Thiết lập đường dẫn gốc cho toàn bộ backend
backend_path = os.path.join(os.getcwd(), "backend")
sys.path.append(backend_path)

from agents.pipeline.dev_pipeline import DevPipeline
from core.logger import logger

async def simulate_mission():
    pipeline = DevPipeline()
    task_id = "aios-yt-automation-v3"
    prompt = "build_youtube_short_automation"
    
    print("🌟 AIOS MULTI-AGENT DEV MISSION STARTED (FINAL) 🌟")
    print(f"🎯 Objective: {prompt}")
    print("-" * 50)
    
    # Thực hiện quy trình: Research -> Plan -> Code -> Audit -> Memory
    result = await pipeline.run_mission(task_id, prompt)
    
    print("\n" + "=" * 50)
    print(f"🏆 MISSION STATUS: {result['status'].upper()}")
    print(f"📊 Steps Completed: {result['steps_completed']}")
    print("-" * 50)
    
    # Kiểm tra phản tỉnh
    from memory.dev_memory import DevMemory
    memory = DevMemory()
    print("\n📝 [Memory] Learnings for next time:")
    print(memory.get_context())

if __name__ == "__main__":
    asyncio.run(simulate_mission())
