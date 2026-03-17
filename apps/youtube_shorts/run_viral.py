import argparse
import httpx
import asyncio
import sys
import time
import os

# Cấu hình
API_URL = "http://localhost:8888/api/video"

def extract_video_id(url):
    import re
    regExp = r"^.*((youtu.be\/)|(v\/)|(\/u\/\w\/)|(embed\/)|(watch\?))\??v?=?([^#&?]*).*"
    match = re.search(regExp, url)
    if match and len(match.group(7)) == 11:
        return match.group(7)
    if "/shorts/" in url:
        return url.split("/shorts/")[1].split("?")[0]
    return "unknown_video"

async def main():
    parser = argparse.ArgumentParser(description="AI Viral Shorts Automation One-Command")
    parser.add_argument("--url", required=True, help="YouTube Video or Shorts URL")
    args = parser.parse_args()

    video_id = extract_video_id(args.url)
    
    print(f"🚀 [START] Bắt đầu quy trình Viral Pipeline cho: {video_id}")
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        # 1. Gửi yêu cầu xử lý
        try:
            res = await client.post(f"{API_URL}/api/video/process", json={"url": args.url, "id": video_id})
            if res.status_code != 200:
                print(f"❌ Lỗi: Server Backend chưa chạy hoặc lỗi kết nối. Hãy chạy 'python backend/main.py' trước.")
                return
        except Exception as e:
            print(f"❌ Lỗi: Không thể kết nối tới Backend tại {API_URL}. {e}")
            return

        print("📡 Đang khởi tạo AI & Tải video...")
        
        # 2. Theo dõi tiến trình
        last_step = ""
        while True:
            status_res = await client.get(f"{API_URL}/api/video/last-result/{video_id}")
            data = status_res.json()
            
            status = data.get("status")
            step = data.get("step", "Đang xử lý")
            progress = data.get("progress", 0)
            
            if step != last_step:
                print(f"🔄 [BƯỚC] {step} ({progress}%)")
                last_step = step
            
            if status == "completed":
                print("\n✨ [HOÀN TẤT] AI đã xử lý xong toàn bộ video!")
                print("--------------------------------------------------")
                for clip in data.get("details", []):
                    print(f"🎬 CLIP: {clip['name']}")
                    print(f"📝 TIÊU ĐỀ: {clip.get('title', 'N/A')}")
                    print(f"📊 VIRAL SCORE: {clip.get('score', 0)}/100")
                    print(f"📂 CATEGORY: {clip.get('category', 'N/A')}")
                    print(f"💡 EXPLANATION: {clip.get('explanation', 'N/A')}")
                    print(f"📁 ĐƯỜNG DẪN: spaceofduy/projects/youtube_shorts_automation/outputs/shorts/TIKTOK_{clip['name']}.mp4")
                    print("--------------------------------------------------")
                break
            elif status == "error":
                print(f"❌ [LỖI] Pipeline thất bại: {data.get('message')}")
                break
                
            await asyncio.sleep(3)

if __name__ == "__main__":
    asyncio.run(main())
