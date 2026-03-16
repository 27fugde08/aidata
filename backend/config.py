import os

# --- CẤU HÌNH AI CỦA DUY ---

# 1. Google Gemini API Key
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "") 

# 2. Không gian làm việc
WORKSPACE_ROOT = "spaceofduy"

# 3. Model mặc định (CHUYỂN SANG GEMINI 2.0 FLASH SIÊU MẠNH)
DEFAULT_MODEL = "gemini-2.0-flash"

# 4. Sandbox (Docker) - Bật/Tắt chế độ chạy trong Docker
ENABLE_DOCKER_SANDBOX = False 
DOCKER_IMAGE = "python:3.10-slim"

# 5. Vector Memory
VECTOR_DB_PATH = os.path.join(WORKSPACE_ROOT, ".memory/vector_db.json")

# --- KẾT THÚC CẤU HÌNH ---

if not os.path.exists(WORKSPACE_ROOT):
    os.makedirs(WORKSPACE_ROOT)

if not os.path.exists(os.path.dirname(VECTOR_DB_PATH)):
    os.makedirs(os.path.dirname(VECTOR_DB_PATH))
