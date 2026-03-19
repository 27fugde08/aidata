from fastapi import FastAPI, HTTPException, Body, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
import sys
import os
import asyncio

# --- Setup System Path ---
# Thêm PROJECT ROOT vào sys.path để có thể import apps.xxx và core_kernel.src.xxx
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# --- Import Shared Logic ---
from shared.config import config
from shared.logger import logger

from api import project, workflow, generate, deploy, review, video_automation, command, system, queue
from core.lifecycle import lifecycle
from core.instance import orchestrator
from core.plugin_manager import PluginManager
from core.file_manager import FileManager
from core.resource_manager import ResourceManager

# --- Application Setup ---
app = FastAPI(
    title="AIOS Kernel (Modular Monorepo)",
    description="The central nervous system for autonomous AI agents.",
    version="2.2.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instances & Plugin Loading
resource_manager = ResourceManager(config.WORKSPACE_ROOT)
plugin_manager = PluginManager(config.WORKSPACE_ROOT)

@app.on_event("startup")
async def startup_event():
    await lifecycle.startup()
    # Dynamic Discovery: Tải các app từ thư mục apps/ một cách độc lập
    plugin_manager.load_modular_apps(app)

@app.on_event("shutdown")
async def shutdown_event():
    await lifecycle.shutdown()

# --- Core Routers ---
app.include_router(project.router, prefix="/api/v1/projects", tags=["Projects"])
app.include_router(workflow.router, prefix="/api/v1/workflow", tags=["Workflow"])
app.include_router(generate.router, prefix="/api/v1/generate", tags=["Code Generation"])
app.include_router(deploy.router, prefix="/api/v1/deploy", tags=["Deployment"])
app.include_router(review.router, prefix="/api/v1/review", tags=["Code Review"])
app.include_router(video_automation.router, prefix="/api/v1/video", tags=["Video Automation"])
app.include_router(system.router, prefix="/api/v1/system", tags=["System Intelligence"])
app.include_router(command.router, prefix="/api/v1/command", tags=["Command Center"])
app.include_router(queue.router, prefix="/api/v1/queue", tags=["Task Queue (Auto-Scaling)"])

# Mount Storage
app.mount("/api/video/stream/shorts", StaticFiles(directory=os.path.join(config.WORKSPACE_ROOT, "outputs")), name="shorts_stream")

@app.get("/")
def home():
    return {
        "status": "online",
        "system": "AIOS Kernel (Modular Monorepo)",
        "version": "2.2.0",
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc"
        },
        "endpoints": {
            "core": {
                "projects": "/api/v1/projects",
                "workflow": "/api/v1/workflow",
                "code_generation": "/api/v1/generate",
                "deployment": "/api/v1/deploy",
                "code_review": "/api/v1/review",
                "command_center": "/api/v1/command",
                # "system_health": "/api/v1/system/health",
                "event_stream": "/api/v1/system/stream"
            },
            "automation": {
                "video_automation": "/api/v1/video",
                "douyin": "/api/v1/douyin_automation",
                "youtube_shorts": "/api/v1/youtube_shorts",
                "youtube_enterprise": "/api/v1/youtube_shorts_enterprise"
            },
            "storage": {
                "video_stream": "/api/video/stream/shorts"
            }
        },
        "workspace": config.WORKSPACE_ROOT
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8888, reload=True)
