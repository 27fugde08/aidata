import os
from dotenv import load_dotenv

# Tự động tải .env nếu có
load_dotenv()

# --- CẤU HÌNH AI CỦA DUY (Refactored) ---

# 1. Google Gemini API Key
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
# Support multiple keys for rotation (comma separated)
GEMINI_API_KEYS = [k.strip() for k in os.environ.get("GEMINI_API_KEYS", GEMINI_API_KEY).split(",") if k.strip()]

# OpenAI & Anthropic (Optional)
OPENAI_API_KEYS = [k.strip() for k in os.environ.get("OPENAI_API_KEYS", "").split(",") if k.strip()]
ANTHROPIC_API_KEYS = [k.strip() for k in os.environ.get("ANTHROPIC_API_KEYS", "").split(",") if k.strip()]

# 2. Không gian làm việc (Mới: Trỏ về storage/)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WORKSPACE_ROOT = os.path.join(PROJECT_ROOT, "storage")

# 3. Model mặc định
DEFAULT_MODEL = "gemini-2.0-flash"
LOCAL_MODEL = "mistral" 

# 4. Sandbox (Docker)
ENABLE_DOCKER_SANDBOX = False 
DOCKER_IMAGE = "python:3.10-slim"

# 5. Vector Memory (Chuyển vào storage/db)
VECTOR_DB_PATH = os.path.join(WORKSPACE_ROOT, "db", "chroma_db")

# --- KẾT THÚC CẤU HÌNH ---

# Đảm bảo các thư mục tồn tại
os.makedirs(os.path.join(WORKSPACE_ROOT, "db"), exist_ok=True)
os.makedirs(os.path.join(WORKSPACE_ROOT, "logs"), exist_ok=True)
os.makedirs(os.path.join(WORKSPACE_ROOT, "outputs"), exist_ok=True)
os.makedirs(os.path.join(WORKSPACE_ROOT, "temp"), exist_ok=True)

# Export as config object
import sys
config = sys.modules[__name__]
