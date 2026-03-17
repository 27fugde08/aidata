import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime

class DBManager:
    """
    Quản lý dữ liệu lịch sử tải video Douyin bằng file JSON.
    """
    def __init__(self, db_path: str = "backend/database/douyin_db.json"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        if not os.path.exists(self.db_path):
            with open(self.db_path, "w", encoding="utf-8") as f:
                json.dump({"videos": [], "settings": {}}, f)

    def _read_db(self) -> Dict[str, Any]:
        with open(self.db_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write_db(self, data: Dict[str, Any]):
        with open(self.db_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def add_video(self, video_info: Dict[str, Any]):
        db = self._read_db()
        video_info["created_at"] = datetime.now().isoformat()
        db["videos"].append(video_info)
        self._write_db(db)

    def get_all_videos(self) -> List[Dict[str, Any]]:
        return self._read_db().get("videos", [])

    def find_video_by_id(self, video_id: str) -> Optional[Dict[str, Any]]:
        videos = self.get_all_videos()
        for v in videos:
            if v.get("id") == video_id:
                return v
        return None
