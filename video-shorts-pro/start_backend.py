import uvicorn
import os
import sys

# Add backend to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

if __name__ == "__main__":
    print("🚀 Starting Video Shorts Pro Backend on http://localhost:8005")
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8005, reload=True)
