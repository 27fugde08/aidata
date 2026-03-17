import subprocess
import time
import sys
import os

def run_douyin_app():
    print("🚀 Đang khởi động Douyin Real Video Automation...")
    
    # 1. Khởi động Backend
    backend_dir = os.path.join(os.getcwd(), "backend")
    print(f"📂 Khởi động Backend tại: {backend_dir}")
    
    # Sử dụng sys.executable để chạy đúng môi trường python hiện tại
    backend_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"],
        cwd=backend_dir
    )
    
    # 2. Khởi động Frontend (Simple HTTP Server)
    frontend_dir = os.path.join(os.getcwd(), "frontend")
    print(f"🌐 Khởi động Frontend tại: {frontend_dir}")
    frontend_proc = subprocess.Popen(
        [sys.executable, "-m", "http.server", "8081"],
        cwd=frontend_dir
    )
    
    print("\n✅ Ứng dụng đã sẵn sàng!")
    print("🔗 API: http://localhost:8001")
    print("🔗 Giao diện: http://localhost:8081")
    print("按 Ctrl+C để dừng ứng dụng.")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Đang dừng ứng dụng...")
        backend_proc.terminate()
        frontend_proc.terminate()
        print("👋 Tạm biệt!")

if __name__ == "__main__":
    run_douyin_app()
