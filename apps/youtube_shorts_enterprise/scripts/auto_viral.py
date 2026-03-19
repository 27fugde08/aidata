import asyncio
import os
import sys
import logging

# Thiết lập đường dẫn để import từ backend của dự án
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

# Mock import các agent từ hệ thống chính (AIOS)
# Trong thực tế, ta sẽ gọi qua API hoặc import trực tiếp từ backend trung tâm
from apps.youtube_shorts_enterprise.core.video_engine import YouTubeShortEngine

# Giả lập Researcher Agent
class TrendResearcher:
    async def get_trending_topic(self):
        print("🔍 [AutoViral] Searching for trending topics...")
        await asyncio.sleep(2)
        return "AI Revolution in 2026"

# Giả lập Manager Agent (Script Writer)
class ScriptManager:
    async def write_script(self, topic):
        print(f"📋 [AutoViral] Drafting script for: {topic}")
        await asyncio.sleep(1)
        return f"How {topic} is changing the world in 60 seconds."

async def run_viral_loop():
    print("🚀 --- AIOS AUTO-VIRAL ENGINE STARTED ---")
    
    researcher = TrendResearcher()
    manager = ScriptManager()
    engine = YouTubeShortEngine(workspace="data")
    
    # 1. Research
    topic = await researcher.get_trending_topic()
    print(f"🔥 Found Trending Topic: {topic}")
    
    # 2. Planning/Scripting
    script = await manager.write_script(topic)
    print(f"📝 Script Ready: {script}")
    
    # 3. Execution (Tạo video)
    print("🎬 Sending to Production Engine...")
    result = await engine.create_short(
        source_url="https://aios.internal/source/viral_clips",
        title=topic
    )
    
    if result["status"] == "success":
        print(f"✅ SUCCESS: Video created at {result['path']}")
        print(f"📊 Ready for upload: {topic}")
    else:
        print(f"❌ FAILED: {result['message']}")

    print("🏁 --- END OF SESSION ---")

if __name__ == "__main__":
    asyncio.run(run_viral_loop())
