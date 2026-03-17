import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from spaceofduy.projects.douyin_automation.backend.api import douyin

app = FastAPI(
    title="Douyin Real Video Downloader API",
    description="API cho phép lấy link video Douyin thực tế và tải không logo.",
    version="1.0.0"
)

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Đăng ký các router
app.include_router(douyin.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Douyin Automation API is running!"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
