import httpx
import json
import asyncio

async def test():
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get("http://127.0.0.1:8000/openapi.json")
            data = resp.json()
            paths = [k for k in data['paths'].keys() if 'enterprise' in k]
            print(f"Enterprise paths: {paths}")
            
            paths_all = list(data['paths'].keys())
            print(f"All paths: {paths_all}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test())
