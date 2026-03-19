import uvicorn
import sys
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from apps.youtube_shorts.api.shorts import router as shorts_router

app = FastAPI(
    title="YouTube Shorts Automation (Enterprise Rebuild)",
    description="Professional video automation service powered by AIOS Agents.",
    version="2.0.0"
)

# Cấu hình CORS cho phép Control Tower kết nối
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Đăng ký các Router
app.include_router(shorts_router, prefix="/api")

@app.get("/")
def read_root():
    return {"status": "YouTube Shorts Automation Service is Online", "version": "2.0.0"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=True)
