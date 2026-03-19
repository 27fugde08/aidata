import httpx
import asyncio
import json
import sys

# AIOS Kernel API Base
AIOS_URL = "http://127.0.0.1:8000/api/v1"

async def control_apps():
    print("🧠 AIOS KERNEL: INDEPENDENT CONTROL MODE")
    print("-" * 50)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # 1. Kiểm tra trạng thái hệ thống và các app đã mount
        try:
            resp = await client.get(f"http://127.0.0.1:8000/")
            data = resp.json()
            print(f"✅ AIOS Kernel v{data['version']} is ONLINE")
            print(f"📦 Mounted Apps: {list(data['endpoints']['automation'].keys())}")
        except Exception as e:
            print(f"❌ AIOS Kernel is OFFLINE. Hãy chạy 'python manage.py runserver' trước.")
            return

        # 2. Gửi lệnh điều khiển qua Command Center
        # Lệnh này sẽ được CommandParser phân tích và đưa vào TaskQueue
        command = "/aios run video_automation_mission --url https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        print(f"\n🎮 Sending Command: {command}")
        
        try:
            cmd_resp = await client.post(f"{AIOS_URL}/command/execute", json={"command": command})
            cmd_data = cmd_resp.json()
            task_id = cmd_data.get("task_id")
            print(f"🚀 Command Accepted! Task ID: {task_id}")
            
            # 3. Theo dõi Task Queue (AIOS Orchestrator đang xử lý ngầm)
            print("\n⏳ Monitoring Task Queue...")
            for _ in range(5):
                tasks_resp = await client.get(f"{AIOS_URL}/command/tasks")
                tasks = tasks_resp.json()
                # Tìm task vừa tạo
                this_task = next((t for t in tasks if t['id'] == task_id), None)
                if this_task:
                    print(f"📊 Task Status: {this_task['status']} | Progress: {this_task.get('progress', 0)}%")
                    if this_task['status'] in ['done', 'completed', 'failed']:
                        break
                await asyncio.sleep(2)
        
        except Exception as e:
            print(f"❌ Error sending command: {e}")

        # 4. Trực tiếp gọi App Router qua AIOS Gateway
        print("\n🔗 Direct App Control via AIOS Gateway:")
        try:
            # Gọi Douyin Automation qua AIOS
            douyin_resp = await client.post(f"{AIOS_URL}/douyin_automation/douyin/info", 
                                          json={"url": "https://v.douyin.com/abc/"})
            print(f"📱 Douyin App Response: {douyin_resp.status_code}")
        except Exception as e:
            print(f"⚠️ App direct call failed (Expected if mock URL): {e}")

    print("-" * 50)
    print("🏁 CONTROL SESSION COMPLETE")

if __name__ == "__main__":
    asyncio.run(control_apps())
