import subprocess
import time
import sys
import os
from datetime import datetime

# Màu sắc cho terminal
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'

def log(msg, color=RESET):
    print(f"{color}[{datetime.now().strftime('%H:%M:%S')}] {msg}{RESET}")

def run_backend():
    backend_path = os.path.join(os.getcwd(), "backend", "main.py")
    cmd = [sys.executable, backend_path]
    
    while True:
        log("🚀 Starting AIOS Backend...", GREEN)
        
        # Chạy Backend như một tiến trình con
        process = subprocess.Popen(
            cmd,
            cwd=os.path.join(os.getcwd(), "backend"),
            stdout=sys.stdout,
            stderr=sys.stderr
        )
        
        try:
            # Chờ tiến trình kết thúc (nếu nó crash)
            process.wait()
        except KeyboardInterrupt:
            log("🛑 Stopping AIOS Monitor...", YELLOW)
            process.terminate()
            break
        
        # Nếu process thoát (crash), log lỗi và restart
        if process.returncode != 0:
            log(f"⚠️ Backend crashed with code {process.returncode}. Restarting in 3 seconds...", RED)
            time.sleep(3)
        else:
            log("✅ Backend stopped gracefully.", GREEN)
            break

if __name__ == "__main__":
    log("🛡️  AIOS GUARDIAN: System Protection Active", GREEN)
    run_backend()
