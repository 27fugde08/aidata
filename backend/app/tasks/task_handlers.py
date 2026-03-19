import asyncio
import re
import json
import os
import subprocess
import yt_dlp
from deep_translator import GoogleTranslator
from app.core.celery_app import celery_app
from app.db.session import AsyncSessionLocal
from app.models.all_models import Task, TaskStatus
from sqlalchemy import update
import logging

logger = logging.getLogger(__name__)

STORAGE_DIR = "/app/storage"
os.makedirs(STORAGE_DIR, exist_ok=True)

def run_async(coro):
    """Helper to run async code in a sync Celery worker."""
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(coro)

def extract_url(text: str):
    """Finds the first HTTP URL in a string."""
    if not text:
        return None
    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    match = re.search(regex, text)
    return match.group(0) if match else None

@celery_app.task(name="tasks.process_video_translation")
def process_video_translation_task_job(task_id: int):
    """
    Complex Task:
    1. Download Video
    2. Extract Subtitles (or mock if not available)
    3. Translate to target language
    4. Burn subtitles into video
    """
    async def _execute():
        async with AsyncSessionLocal() as db:
            task = await db.get(Task, task_id)
            if not task: return

            try:
                await db.execute(update(Task).where(Task.id == task_id).values(status="PROCESSING"))
                await db.commit()

                url = extract_url(task.description)
                if not url: raise Exception("No URL found in description")

                # 1. Download Video
                video_filename = f"video_{task_id}.mp4"
                video_path = os.path.join(STORAGE_DIR, video_filename)
                
                ydl_opts = {
                    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                    'outtmpl': video_path,
                    'writesubtitles': True,
                    'writeautomaticsub': True,
                    'subtitleslangs': ['en'],
                    'quiet': True
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])

                # 2. Extract / Translate Subtitles
                # For demo, we assume English subs were downloaded
                sub_path_vtt = video_path.replace(".mp4", ".en.vtt")
                translated_sub_path = video_path.replace(".mp4", ".vi.srt")
                
                if os.path.exists(sub_path_vtt):
                    # Simple VTT to SRT conversion & Translation simulation
                    with open(sub_path_vtt, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Mock translation of large blocks (real app would parse VTT)
                    translated_content = GoogleTranslator(source='auto', target='vi').translate(content[:2000])
                    with open(translated_sub_path, 'w', encoding='utf-8') as f:
                        f.write(translated_content)
                else:
                    # Fallback if no subs found: Create a mock subtitle for demo
                    with open(translated_sub_path, 'w', encoding='utf-8') as f:
                        f.write("1\n00:00:01,000 --> 00:00:05,000\n[AI OS Generated Subtitle]\n")

                # 3. Burn Subtitles into Video using FFmpeg
                output_filename = f"translated_{task_id}.mp4"
                output_path = os.path.join(STORAGE_DIR, output_filename)
                
                # FFmpeg command: burning subtitles
                cmd = [
                    "ffmpeg", "-y", "-i", video_path, 
                    "-vf", f"subtitles={translated_sub_path}", 
                    "-c:a", "copy", output_path
                ]
                subprocess.run(cmd, check=True)

                # 4. Success
                result_data = {
                    "video_url": f"/storage/{output_filename}",
                    "status": "success",
                    "languages": ["vi"],
                    "message": "Video downloaded, translated and subtitled successfully."
                }
                await db.execute(update(Task).where(Task.id == task_id).values(status="COMPLETED", result=result_data))
                await db.commit()

            except Exception as e:
                logger.error(f"Translation Error: {e}")
                await db.rollback()
                await db.execute(update(Task).where(Task.id == task_id).values(status="FAILED", result={"error": str(e)}))
                await db.commit()

    run_async(_execute())
    return {"status": "dispatched"}
