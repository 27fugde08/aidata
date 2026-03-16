import os
from dotenv import load_dotenv

# Tự động tải .env nếu có
load_dotenv()

# --- CẤU HÌNH AI CỦA DUY ---

# 1. Google Gemini API Key
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
# Support multiple keys for rotation (comma separated)
GEMINI_API_KEYS = [k.strip() for k in os.environ.get("GEMINI_API_KEYS", GEMINI_API_KEY).split(",") if k.strip()]

# OpenAI & Anthropic (Optional)
OPENAI_API_KEYS = [k.strip() for k in os.environ.get("OPENAI_API_KEYS", "").split(",") if k.strip()]
ANTHROPIC_API_KEYS = [k.strip() for k in os.environ.get("ANTHROPIC_API_KEYS", "").split(",") if k.strip()]

# 2. Không gian làm việc
WORKSPACE_ROOT = "spaceofduy"

# 3. Model mặc định (CHUYỂN SANG GEMINI 2.0 FLASH SIÊU MẠNH)
DEFAULT_MODEL = "gemini-2.0-flash"
LOCAL_MODEL = "mistral" # Default local model

# 4. Sandbox (Docker) - Bật/Tắt chế độ chạy trong Docker
ENABLE_DOCKER_SANDBOX = False 
DOCKER_IMAGE = "python:3.10-slim"

# 5. Vector Memory
# Old JSON path (deprecated but kept for migration)
VECTOR_DB_PATH_OLD = os.path.join(WORKSPACE_ROOT, ".memory/vector_db.json")
# New ChromaDB path
VECTOR_DB_PATH = os.path.join(WORKSPACE_ROOT, ".memory/chroma_db")

# --- KẾT THÚC CẤU HÌNH ---

if not os.path.exists(WORKSPACE_ROOT):
    os.makedirs(WORKSPACE_ROOT)

if not os.path.exists(os.path.dirname(VECTOR_DB_PATH_OLD)):
    os.makedirs(os.path.dirname(VECTOR_DB_PATH_OLD))
