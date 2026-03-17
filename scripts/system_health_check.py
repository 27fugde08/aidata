import httpx
import asyncio
import json

async def health_check():
    print("🛡️  AIOS SYSTEM HEALTH CHECK INITIALIZED")
    print("-" * 50)
    
    targets = {
        "Kernel (Main)": "http://localhost:8888/",
        "YouTube Rebuild": "http://localhost:8002/",
        "Resource API": "http://localhost:8888/api/v1/system/resources",
        "Command API": "http://localhost:8888/api/v1/command/tasks",
        "Scheduler API": "http://localhost:8888/api/scheduler/list"
    }

    async with httpx.AsyncClient(timeout=5.0) as client:
        for name, url in targets.items():
            try:
                response = await client.get(url)
                if response.status_code == 200:
                    status = "✅ ONLINE"
                    detail = f"Response OK"
                else:
                    status = f"⚠️ WARNING ({response.status_code})"
                    detail = response.text[:50]
                
                print(f"{name:<20} | {status} | {detail}")
            except Exception as e:
                print(f"{name:<20} | ❌ OFFLINE | Connection Error")

    print("-" * 50)
    print("🏁 HEALTH CHECK COMPLETE")

if __name__ == "__main__":
    asyncio.run(health_check())
