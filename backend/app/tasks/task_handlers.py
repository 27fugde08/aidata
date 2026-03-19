import asyncio
import re
import json
import yt_dlp
from app.core.celery_app import celery_app
from app.db.session import AsyncSessionLocal
from app.models.all_models import Task, TaskStatus
from sqlalchemy import update
import logging

logger = logging.getLogger(__name__)

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

@celery_app.task(name="tasks.process_task_job")
def process_task_job(task_id: int):
    """
    Background worker logic:
    1. Retrieve Task
    2. Extract URL from description
    3. Use yt-dlp to get video metadata
    4. Save to DB
    """
    async def _execute():
        async with AsyncSessionLocal() as db:
            task = await db.get(Task, task_id)
            if not task:
                logger.error(f"Task {task_id} not found.")
                return

            try:
                # 1. Update Status -> PROCESSING
                await db.execute(
                    update(Task)
                    .where(Task.id == task_id)
                    .values(status=TaskStatus.PROCESSING)
                )
                await db.commit()
                logger.info(f"Task {task_id} started processing.")

                # 2. Logic: Extract URL & Process
                url = extract_url(task.description)
                result_data = {}

                if url:
                    logger.info(f"Analyzing URL: {url}")
                    ydl_opts = {
                        'quiet': True,
                        'no_warnings': True,
                        'skip_download': True, # Only get metadata, don't download video file
                        'extract_flat': True   # Faster for playlists
                    }
                    
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(url, download=False)
                        
                        # Filter relevant info to keep JSON clean
                        result_data = {
                            "source": "youtube",
                            "original_url": url,
                            "video_title": info.get('title'),
                            "uploader": info.get('uploader'),
                            "view_count": info.get('view_count'),
                            "duration": info.get('duration'),
                            "upload_date": info.get('upload_date'),
                            "thumbnail": info.get('thumbnail'),
                            "tags": info.get('tags', [])[:5], # Take top 5 tags
                            "metadata_processed": True
                        }
                else:
                    # Fallback if no URL found
                    result_data = {
                        "status": "completed_no_url",
                        "message": "No valid URL found in task description. Simulation skipped.",
                        "original_description": task.description
                    }

                # 3. Finalize -> COMPLETED
                await db.execute(
                    update(Task)
                    .where(Task.id == task_id)
                    .values(status=TaskStatus.COMPLETED, result=result_data)
                )
                await db.commit()
                logger.info(f"Task {task_id} completed successfully with real data.")
                
            except Exception as e:
                logger.error(f"Task {task_id} failed: {e}")
                await db.rollback()
                await db.execute(
                    update(Task)
                    .where(Task.id == task_id)
                    .values(status=TaskStatus.FAILED, result={"error": str(e)})
                )
                await db.commit()

    run_async(_execute())
    return {"task_id": task_id, "status": "processed"}
