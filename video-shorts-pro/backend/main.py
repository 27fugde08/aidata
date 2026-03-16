from fastapi import FastAPI, HTTPException, Body, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import os
import uuid
import uvicorn

from models import SessionLocal, Video, Clip, init_db
from downloader import DownloaderService
from processor import ProcessorService

app = FastAPI(title="Video Shorts Pro API")

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize DB
init_db()

# Services
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VIDEOS_DIR = os.path.join(BASE_DIR, "videos")
SHORTS_DIR = os.path.join(BASE_DIR, "shorts")

downloader = DownloaderService(VIDEOS_DIR)
processor = ProcessorService(SHORTS_DIR)

# DB Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- API Endpoints ---

@app.post("/api/download")
async def download_video(background_tasks: BackgroundTasks, db: Session = Depends(get_db), data: dict = Body(...)):
    url = data.get("url")
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")
    
    # Check if already exists
    existing = db.query(Video).filter(Video.url == url).first()
    if existing:
        return {"status": "exists", "id": existing.id}
    
    # Download
    result = downloader.download(url)
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["error"])
    
    # Save to DB
    new_video = Video(
        url=url,
        platform=result["platform"],
        title=result["title"],
        duration=result["duration"],
        file_path=result["file_path"],
        thumbnail=result["thumbnail"]
    )
    db.add(new_video)
    db.commit()
    db.refresh(new_video)
    
    return {"status": "success", "id": new_video.id}

@app.get("/api/videos")
def list_videos(db: Session = Depends(get_db)):
    videos = db.query(Video).all()
    # Ensure relative paths for static mounting
    results = []
    for v in videos:
        results.append({
            "id": v.id,
            "title": v.title,
            "platform": v.platform,
            "duration": v.duration,
            "thumbnail": v.thumbnail,
            "url": f"/videos/{os.path.basename(v.file_path)}"
        })
    return results

@app.get("/api/video/{video_id}")
def get_video(video_id: int, db: Session = Depends(get_db)):
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    return video

@app.post("/api/clip")
async def create_clip(data: dict = Body(...), db: Session = Depends(get_db)):
    video_id = data.get("video_id")
    start = data.get("start_time", 0)
    end = data.get("end_time", 60)
    
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    # Process
    result = processor.process_short(video.file_path, start, end)
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["error"])
    
    # Save Clip to DB
    new_clip = Clip(
        video_id=video_id,
        start_time=start,
        end_time=end,
        output_path=result["output_path"],
        status="completed"
    )
    db.add(new_clip)
    db.commit()
    db.refresh(new_clip)
    
    return {"status": "success", "clip_id": new_clip.id, "url": f"/shorts/{os.path.basename(new_clip.output_path)}"}

@app.get("/api/shorts")
def list_shorts(db: Session = Depends(get_db)):
    clips = db.query(Clip).all()
    results = []
    for c in clips:
        results.append({
            "id": c.id,
            "video_id": c.video_id,
            "start": c.start_time,
            "end": c.end_time,
            "url": f"/shorts/{os.path.basename(c.output_path)}"
        })
    return results

# Static Mounting
app.mount("/videos", StaticFiles(directory=VIDEOS_DIR), name="videos")
app.mount("/shorts", StaticFiles(directory=SHORTS_DIR), name="shorts")

if os.path.exists(os.path.join(BASE_DIR, "frontend")):
    app.mount("/", StaticFiles(directory=os.path.join(BASE_DIR, "frontend"), html=True), name="frontend")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8005)
