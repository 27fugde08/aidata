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
import config

from core.scheduler import AgentOSScheduler
from core.automation_scheduler import AutomationScheduler
from core.deployer import DeploymentEngine
from core.resource_manager import ResourceManager
from core.video_downloader import DownloaderService
from core.video_processor import ProcessorService
import config

# Khởi tạo AI Router trực tiếp từ module generate
from api.generate import ai

app = FastAPI(title="Gemini AI IDE (SpaceOfDuy Edition)")

# --- AI OS Services ---
os_scheduler = AgentOSScheduler()
automation_scheduler = AutomationScheduler(config.WORKSPACE_ROOT)
resource_manager = ResourceManager(config.WORKSPACE_ROOT)
deploy_engine = DeploymentEngine(config.WORKSPACE_ROOT)

# Video Services
VIDEOS_DIR = os.path.join(config.WORKSPACE_ROOT, "videos")
SHORTS_DIR = os.path.join(config.WORKSPACE_ROOT, "shorts")
downloader = DownloaderService(VIDEOS_DIR)
processor = ProcessorService(SHORTS_DIR)

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
agent = AgentEngine(config.WORKSPACE_ROOT)

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
async def video_download(data: dict = Body(...)):
    url = data.get("url")
    if not url: raise HTTPException(status_code=400, detail="URL required")
    # Downloader.download is currently synchronous, run in thread
    result = await asyncio.to_thread(downloader.download, url)
    if result["status"] == "error": raise HTTPException(status_code=500, detail=result["error"])
    return result

@app.get("/api/video/list")
def list_video_library():
    videos = []
    if os.path.exists(VIDEOS_DIR):
        for f in os.listdir(VIDEOS_DIR):
            if f.endswith(".mp4"):
                videos.append({"name": f, "url": f"/videos/{f}", "size": os.path.getsize(os.path.join(VIDEOS_DIR, f))})
    shorts = []
    if os.path.exists(SHORTS_DIR):
        for f in os.listdir(SHORTS_DIR):
            if f.endswith(".mp4"):
                shorts.append({"name": f, "url": f"/shorts/{f}", "size": os.path.getsize(os.path.join(SHORTS_DIR, f))})
    return {"videos": videos, "shorts": shorts}

@app.post("/api/video/clip")
async def create_video_clip(background_tasks: BackgroundTasks, data: dict = Body(...)):
    filename = data.get("filename")
    start = data.get("start", 0)
    end = data.get("end", 60)
    
    input_path = os.path.join(VIDEOS_DIR, filename)
    if not os.path.exists(input_path): raise HTTPException(status_code=404, detail="File not found")
    
    # Run processing in background
    async def run_proc():
        await processor.process_short(input_path, start, end)
        
    background_tasks.add_task(run_proc)
    return {"status": "processing", "message": "Short is being generated in the background."}

# Static Mounting
app.mount("/videos", StaticFiles(directory=VIDEOS_DIR), name="videos")
app.mount("/shorts", StaticFiles(directory=SHORTS_DIR), name="shorts")

@app.post("/api/agent/work")
async def agent_work(data: dict = Body(...)):
    """
    AI Agent tự thực hiện task phức tạp (Debug, Terminal, Build Project).
    """
    prompt = data.get("prompt", "")
    api_key = data.get("api_key")
    mode = data.get("mode", "single") # single | workflow
    
    if mode == "workflow":
        # Chạy quy trình Multi-Agent
        orchestrator = MultiAgentOrchestrator(config.WORKSPACE_ROOT, api_key or config.GEMINI_API_KEY)
        async def workflow_gen():
            async for step in orchestrator.run_workflow("Full Feature Development", prompt):
                yield step
        return StreamingResponse(workflow_gen(), media_type="text/plain")
    else:
        # Chạy Single Agent (như cũ)
        current_agent = AgentEngine(config.WORKSPACE_ROOT, api_key=api_key)
        async def agent_gen():
            async for step in current_agent.work_stream(prompt):
                yield step
        return StreamingResponse(agent_gen(), media_type="text/plain")

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
    Endpoint chat CHỈ DÙNG GEMINI.
    Bỏ qua mọi cấu hình OpenAI từ web.
    """
    messages = data.get("messages", [])
    
    try:
        # Sử dụng Gemini Router đã cấu hình
        response_text = await ai.chat(messages)
        
        async def gemini_gen():
            yield response_text
            
        return StreamingResponse(gemini_gen(), media_type="text/plain")
    except Exception as e:
        async def err_gen():
            yield f"❌ Lỗi Gemini: {str(e)}"
        return StreamingResponse(err_gen(), media_type="text/plain")

@app.get("/")
def home():
    return {"status": "Gemini AI IDE Running", "workspace": config.WORKSPACE_ROOT}

# --- Skill Marketplace API ---

@app.get("/api/skills/archive")
def list_archived_skills():
    archive_dir = os.path.join(config.WORKSPACE_ROOT, "..", ".skills_archive")
    if not os.path.exists(archive_dir):
        return {"skills": []}
    
    skills = []
    for f in os.listdir(archive_dir):
        if f.endswith(".py"):
            skills.append({
                "name": f,
                "path": f,
                "description": f"Specialized AI Skill: {f}"
            })
    return {"skills": skills}

@app.get("/api/skills/installed")
def list_installed_skills():
    skills_dir = os.path.join(config.WORKSPACE_ROOT, "skills")
    if not os.path.exists(skills_dir):
        return {"skills": []}
    
    skills = []
    for f in os.listdir(skills_dir):
        if f.endswith(".py"):
            skills.append({
                "name": f,
                "path": f
            })
    return {"skills": skills}

@app.get("/api/project/memory")
def get_project_memory():
    from core.memory_manager import MemoryManager
    memory = MemoryManager(config.WORKSPACE_ROOT)
    return memory.memory

@app.post("/api/skills/install")
def install_skill(data: dict = Body(...)):
    skill_name = data.get("name")
    archive_dir = os.path.join(config.WORKSPACE_ROOT, "..", ".skills_archive")
    skills_dir = os.path.join(config.WORKSPACE_ROOT, "skills")
    
    if not os.path.exists(skills_dir):
        os.makedirs(skills_dir)
        
    src = os.path.join(archive_dir, skill_name)
    dst = os.path.join(skills_dir, skill_name)
    
    if os.path.exists(src):
        import shutil
        shutil.copy(src, dst)
        return {"status": "success", "message": f"Skill {skill_name} installed."}
    else:
        raise HTTPException(status_code=404, detail="Skill not found in archive")

# --- Automation Marketplace API ---

@app.get("/api/automations/store")
def list_automation_recipes():
    # Giả lập danh sách các công thức tự động hóa từ archive
    return {
        "recipes": [
            {
                "id": "full-stack-gen",
                "name": "Full-stack App Generator",
                "description": "Tạo nhanh ứng dụng FastAPI + React.",
                "steps": ["Architect", "Backend Dev", "Frontend Dev", "Tester"]
            },
            {
                "id": "security-audit",
                "name": "Security Auditor",
                "description": "Quét lỗ hổng bảo mật và đề xuất bản vá.",
                "steps": ["Security Agent", "Reviewer"]
            },
            {
                "id": "doc-generator",
                "name": "Documentation Bot",
                "description": "Tự động viết README và API Docs.",
                "steps": ["Architect", "Technical Writer"]
            }
        ]
    }

@app.post("/api/automations/install")
def install_automation(data: dict = Body(...)):
    recipe_id = data.get("id")
    # Logic để nạp recipe vào Workflow Builder
    return {"status": "success", "recipe_id": recipe_id}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8888)
