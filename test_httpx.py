import httpx
import asyncio

async def test():
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get("http://127.0.0.1:8000/")
            print(f"Status: {resp.status_code}")
            print(f"Body: {resp.text}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())
