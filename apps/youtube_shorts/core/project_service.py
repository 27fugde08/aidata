import os
import asyncio
import json
from typing import List, Dict
from spaceofduy.projects.youtube_shorts_automation.backend.database.db_manager import DatabaseManager
from spaceofduy.projects.youtube_shorts_automation.backend.services.video_service import VideoService

class ProjectService:
    def __init__(self):
        self.db = DatabaseManager()
        self.video_service = VideoService()

    async def start_full_pipeline(self, video_url: str, video_id: str, callback=None):
        """Chạy toàn bộ pipeline và lưu vào DB."""
        # 1. Khởi tạo project
        project = self.db.get_project(video_id)
        if not project:
            project = self.db.create_project(video_id, f"Project {video_id}", video_url)

        try:
            # 2. Transcription Stage
            if callback: await callback("Tải video & Chuyển văn bản", 10)
            video_path = await self.video_service.download_video(video_url, video_id)
            
            # 3. AI Analysis Stage
            if callback: await callback("AI Đang phân tích nội dung", 30)
            analysis_result = await self.video_service.detect_highlights_semantic(video_path)
            highlights = analysis_result["highlights"]
            all_segments = analysis_result["all_segments"]
            
            self.db.update_project(video_id, {
                "status": "analyzed",
                "transcript": all_segments,
                "highlights": highlights
            })

            # 4. Batch Rendering Stage
            if callback: await callback(f"Đang render {len(highlights)} clips", 50)
            
            async def render_task(i, h):
                short_name = f"viral_{video_id}_{i}"
                await self.video_service.render_short_with_subs(
                    video_path, h["start"], h["end"], short_name, 
                    all_segments, is_podcast=h.get("is_podcast", False), 
                    accent_color=h.get("accent_color", "yellow"),
                    layout_type=h.get("layout_type", "auto"),
                    emoji_map=h.get("emoji_map", {})
                )
                
                short_meta = {
                    "project_id": video_id,
                    "name": short_name,
                    "title": h.get("tiktok_title", "Amazing Clip"),
                    "hashtags": h.get("hashtags", "#shorts"),
                    "score": h.get("virality_score", 0),
                    "category": h.get("category", "General"),
                    "explanation": h.get("virality_explanation", ""),
                    "layout_type": h.get("layout_type", "focus"),
                    "video_url": f"/outputs/{short_name}.mp4"
                }
                
                # Save metadata to DB
                self.db.add_short(short_meta)
                
                # Also save to JSON file for easy listing
                meta_path = os.path.join(self.video_service.output_dir, f"{short_name}.json")
                with open(meta_path, "w", encoding="utf-8") as f:
                    json.dump(short_meta, f, ensure_ascii=False, indent=2)
                    
                return short_meta

            tasks = [render_task(i, h) for i, h in enumerate(highlights)]
            shorts = await asyncio.gather(*tasks)
            
            self.db.update_project(video_id, {"status": "completed"})
            if callback: await callback("Hoàn tất", 100)
            return shorts

        except Exception as e:
            self.db.update_project(video_id, {"status": "error", "error_msg": str(e)})
            raise e

    def get_all_projects(self):
        return self.db.list_projects()

    def get_project_details(self, video_id):
        project = self.db.get_project(video_id)
        shorts = self.db.get_shorts_by_project(video_id)
        return {"project": project, "shorts": shorts}
