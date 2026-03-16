from fastapi import FastAPI, HTTPException, Body, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
import sys
import os
import json
import asyncio

# Đảm bảo đường dẫn gốc được nhận diện
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api import project, workflow, generate, deploy, review
from core.file_manager import FileManager
from core.skill_runner import SkillRunner
from core.agent_engine import AgentEngine
from core.watcher import Watcher
from core.orchestrator import MultiAgentOrchestrator
from core.scheduler import AgentOSScheduler
from core.automation_scheduler import AutomationScheduler
from core.deployer import DeploymentEngine
from core.resource_manager import ResourceManager
import config

# Unified AI Automation OS Core
orchestrator = MultiAgentOrchestrator(workspace_root=config.WORKSPACE_ROOT)

app = FastAPI(title="AI Automation OS (AI Factory Edition)")

# --- AI OS Services ---
os_scheduler = AgentOSScheduler()
automation_scheduler = AutomationScheduler(config.WORKSPACE_ROOT)
resource_manager = ResourceManager(config.WORKSPACE_ROOT)
deploy_engine = DeploymentEngine(config.WORKSPACE_ROOT)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(os_scheduler.run_worker())
    automation_scheduler.scheduler.start()

# --- Deployment API ---
@app.post("/api/deploy/execute")
async def execute_deployment(data: dict = Body(...)):
    project_path = data.get("path")
    env = data.get("env", "production")
    result = await deploy_engine.deploy(project_path, env)
    return result

@app.get("/api/deploy/history")
def get_deployment_history():
    return {"history": deploy_engine.get_history()}

# --- Resource API ---
@app.get("/api/system/resources")
def get_resources():
    return {
        "hardware": resource_manager.get_hardware_stats(),
        "tokens": resource_manager.get_token_summary()
    }

# --- Scheduler API ---
@app.get("/api/scheduler/list")
def list_scheduled_jobs():
    return {"jobs": automation_scheduler.list_jobs()}

@app.post("/api/scheduler/create")
async def create_scheduled_job(data: dict = Body(...)):
    job_id = data.get("id")
    automation_scheduler.add_job(job_id, data)
    return {"status": "success", "job_id": job_id}

# --- OS Process API ---
@app.get("/api/os/processes")
def list_processes():
    return {"processes": os_scheduler.list_processes()}

@app.get("/api/os/events")
def list_events():
    from core.event_engine import events
    return {"events": events.get_history()}

@app.post("/api/os/kill/{pid}")
def kill_process(pid: str):
    success = os_scheduler.kill_process(pid)
    return {"status": "killed" if success else "failed"}

# --- Automation Store API ---
@app.get("/api/automations/store")
def list_automation_recipes():
    return {
        "recipes": [
            {"id": "yt-auto", "name": "YouTube Automation", "description": "Auto generate and upload videos.", "steps": ["Architect", "Automation Agent"]},
            {"id": "tk-auto", "name": "TikTok Bot", "description": "Trending content scraper and uploader.", "steps": ["Scraper", "Video Editor"]},
            {"id": "saas-gen", "name": "SaaS Builder", "description": "Full-stack SaaS boilerplate generator.", "steps": ["Architect", "Developer", "Tester"]}
        ]
    }

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Khởi tạo core
fm = FileManager(config.WORKSPACE_ROOT)
runner = SkillRunner(config.WORKSPACE_ROOT)

# Đăng ký các route API chuyên dụng
app.include_router(project.router, prefix="/api/projects", tags=["projects"])
app.include_router(workflow.router, prefix="/api/workflow", tags=["workflow"])
app.include_router(generate.router, prefix="/api/generate", tags=["generate"])
app.include_router(deploy.router, prefix="/api/deploy", tags=["deploy"])
app.include_router(review.router, prefix="/api/review", tags=["review"])

# --- Live Sync WebSocket ---
@app.websocket("/ws/files")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    loop = asyncio.get_event_loop()
    
    # Khởi tạo Watcher cho thư mục workspace
    watcher = Watcher(config.WORKSPACE_ROOT)
    watcher.start(websocket, loop)
    
    try:
        while True:
            # Giữ kết nối mở để nhận sự kiện từ Watcher
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        watcher.stop()

# --- Endpoints tương thích với Frontend ---

@app.post("/api/video/download")
async def video_download(background_tasks: BackgroundTasks, data: dict = Body(...)):
    url = data.get("url")
    if not url: return {"status": "error", "message": "URL is required"}
    
    target_dir = os.path.join(config.WORKSPACE_ROOT, "videos")
    os.makedirs(target_dir, exist_ok=True)
    
    async def run_download():
        import subprocess
        # Sử dụng yt-dlp để tải video
        cmd = [
            "yt-dlp", 
            "-o", f"{target_dir}/%(title)s.%(ext)s", 
            "--no-playlist",
            "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            url
        ]
        process = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await process.communicate()
        if process.returncode != 0:
            from core.event_engine import events
            events.log("ERROR", f"Download failed: {stderr.decode()}")
            
    background_tasks.add_task(run_download)
    return {"status": "success", "message": "Download started in background"}

@app.get("/api/video/list")
def list_video_library():
    video_dir = os.path.join(config.WORKSPACE_ROOT, "videos")
    shorts_dir = os.path.join(config.WORKSPACE_ROOT, "shorts")
    
    os.makedirs(video_dir, exist_ok=True)
    os.makedirs(shorts_dir, exist_ok=True)
    
    def get_files(directory):
        files = []
        for f in os.listdir(directory):
            if f.endswith((".mp4", ".mkv", ".avi", ".webm")):
                path = os.path.join(directory, f)
                stats = os.stat(path)
                files.append({
                    "name": f,
                    "size": stats.st_size,
                    "url": f"/api/video/stream/{os.path.basename(directory)}/{f}"
                })
        return files

    return {
        "videos": get_files(video_dir),
        "shorts": get_files(shorts_dir)
    }

@app.get("/api/video/stream/{folder}/{filename}")
async def stream_video(folder: str, filename: str):
    from fastapi.responses import FileResponse
    path = os.path.join(config.WORKSPACE_ROOT, folder, filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path)

@app.post("/api/video/clip")
async def video_clip(background_tasks: BackgroundTasks, data: dict = Body(...)):
    filename = data.get("filename")
    start = data.get("start", 0)
    end = data.get("end", 30)
    
    source_path = os.path.join(config.WORKSPACE_ROOT, "videos", filename)
    target_dir = os.path.join(config.WORKSPACE_ROOT, "shorts")
    os.makedirs(target_dir, exist_ok=True)
    
    output_filename = f"short_{filename}"
    output_path = os.path.join(target_dir, output_filename)
    
    async def run_clip():
        import subprocess
        # FFmpeg command to clip and crop to 9:16 (vertical)
        # crop=ih*9/16:ih to center crop for portrait
        cmd = [
            "ffmpeg", "-y",
            "-i", source_path,
            "-ss", str(start),
            "-t", str(end - start),
            "-vf", "crop=ih*9/16:ih,scale=720:1280",
            "-c:v", "libx264", "-crf", "23", "-preset", "veryfast",
            "-c:a", "aac", "-b:a", "128k",
            output_path
        ]
        process = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        await process.communicate()
        
    background_tasks.add_task(run_clip)
    return {"status": "success", "message": f"Clipping job for {filename} started"}

async def agent_work(data: dict = Body(...)):
    """
    AI Agent tự thực hiện task phức tạp qua Mission Controller.
    """
    prompt = data.get("prompt", "")
    mode = data.get("mode", "mission") # mission | workflow
    
    if mode == "workflow":
        async def workflow_gen():
            async for step in orchestrator.run_workflow("Custom Workflow", prompt):
                yield step
        return StreamingResponse(workflow_gen(), media_type="text/plain")
    else:
        # Chạy Mission Controller mới
        async def mission_gen():
            async for chunk in orchestrator.start_mission(prompt):
                yield chunk
        return StreamingResponse(mission_gen(), media_type="text/plain")

@app.get("/api/files")
def list_files_compat(path: str = ""):
    try:
        def flatten_tree(nodes):
            flat = []
            for node in nodes:
                flat.append({"name": node["name"], "path": node["path"], "type": node["type"]})
                if node["children"]: flat.extend(flatten_tree(node["children"]))
            return flat
        tree = fm.list_tree(path)
        return {"files": flatten_tree(tree)}
    except Exception as e: return {"files": [], "error": str(e)}

@app.get("/api/files/content")
def read_file_compat(path: str):
    try:
        content = fm.read(path)
        return {"content": content, "path": path}
    except Exception as e: raise HTTPException(status_code=404, detail=str(e))

@app.post("/api/files/content")
def save_file_compat(data: dict = Body(...)):
    try:
        fm.write(data["path"], data["content"])
        return {"status": "success"}
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/run")
async def run_command_compat(data: dict = Body(...)):
    cmd = data.get("command", "")
    async def event_generator():
        process = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, cwd=config.WORKSPACE_ROOT)
        async def read_stream(stream, type_name):
            while True:
                line = await stream.readline()
                if not line: break
                yield json.dumps({"type": type_name, "data": line.decode('utf-8', errors='replace')}) + "\n"
        async for output in read_stream(process.stdout, "stdout"): yield output
        async for error in read_stream(process.stderr, "stderr"): yield error
        await process.wait()
        yield json.dumps({"type": "system", "data": f"Exited with code {process.returncode}"}) + "\n"
    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.post("/api/ai/chat")
async def ai_chat_compat(data: dict = Body(...)):
    """
    Endpoint chat sử dụng Hybrid Router.
    """
    messages = data.get("messages", [])
    if not messages: return StreamingResponse(iter(["No messages"]), media_type="text/plain")
    
    user_input = messages[-1]['content']
    try:
        model = orchestrator.model_router.route_task(user_input)
        response_text = await orchestrator.model_router.chat(user_input, model=model)
        
        async def gen():
            yield response_text
            
        return StreamingResponse(gen(), media_type="text/plain")
    except Exception as e:
        async def err_gen():
            yield f"❌ Error: {str(e)}"
        return StreamingResponse(err_gen(), media_type="text/plain")

@app.get("/")
def home():
    return {"status": "AI Automation OS Running", "workspace": config.WORKSPACE_ROOT}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8888)
