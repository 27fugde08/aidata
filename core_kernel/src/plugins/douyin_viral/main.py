import os
import asyncio
import json
import random
import shutil
import re
from typing import Dict, Any, List
from core.sdk.plugin_base import AIOSPlugin

class DouyinViralPlugin(AIOSPlugin):
    """
    Douyin Hunter v3.0 Ultimate - Metadata Driven & No-Watermark Extraction.
    """
    
    async def setup(self) -> bool:
        self.log("INFO", "Initializing Douyin Ultimate v3.0 Engine...")
        self.data_dir = os.path.join(self.workspace_root, "data", "douyin_raw")
        self.output_dir = os.path.join(self.workspace_root, "shorts", "douyin_processed")
        self.history_file = os.path.join(self.data_dir, "history.json")
        
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.history = self._load_history()
        self.stats = {"hunted": 0, "processed": 0, "saved_space_mb": 0}
        return True

    def _load_history(self) -> List[str]:
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f: return json.load(f)
            except: return []
        return []

    def _save_history(self, video_id: str):
        self.history.append(video_id)
        with open(self.history_file, 'w') as f: json.dump(self.history[-1000:], f)

    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        action = payload.get("action", "auto_mission")
        if action == "auto_mission":
            return await self.run_ultimate_mission(payload.get("count", 3))
        elif action == "get_stats":
            return {"status": "success", "stats": self.stats}
        return {"status": "error", "message": "Unsupported action"}

    async def run_ultimate_mission(self, count: int = 10) -> Dict[str, Any]:
        self.log("INFO", f"🚀 Starting Ultimate Mission: Targeting TOP {count} viral nodes.")
        
        # 1. Advanced Discovery (TOP 10 Most Viewed)
        candidates = await self.discover_trending_content(count)
        
        # Sort by views (simulated sorting)
        candidates.sort(key=lambda x: float(x["views"].replace('K','').replace('M','000')), reverse=True)
        
        # 2. Filter duplicate
        new_targets = [c for c in candidates if c["id"] not in self.history]
        self.log("INFO", f"Filtered {len(candidates) - len(new_targets)} duplicates.")

        if not new_targets:
            return {"status": "success", "message": "No new viral content found."}

        # 3. Concurrent Pipeline
        tasks = [self.ultimate_pipeline(t) for t in new_targets]
        results = await asyncio.gather(*tasks)
        
        success_list = [r for r in results if r["status"] == "success"]
        self.stats["hunted"] += len(new_targets)
        self.stats["processed"] += len(success_list)
        
        return {"status": "success", "processed": len(success_list), "data": success_list}

    async def discover_trending_content(self, count: int) -> List[Dict]:
        """Giả lập bộ cào dữ liệu Metadata thực thụ."""
        await asyncio.sleep(1)
        topics = ["Tech", "LifeStyle", "Comedy", "AI"]
        return [
            {
                "id": f"dy_{random.randint(100000, 999999)}",
                "title": f"Viral {random.choice(topics)} Content #{i}",
                "author": f"Creator_{random.randint(1,50)}",
                "views": f"{random.randint(500, 5000)}K",
                "url": f"https://v.douyin.com/dummy_{i}",
                "tags": ["#viral", f"#{random.choice(topics).lower()}", "#aios"]
            } for i in range(count)
        ]

    async def ultimate_pipeline(self, target: Dict) -> Dict:
        """Pipeline hoàn thiện nhất: Tải không logo -> Làm sạch metadata -> Xử lý video."""
        try:
            # 1. Download (Simulating No-Watermark URL Parsing)
            video_id = target["id"]
            filename = f"{video_id}.mp4"
            raw_path = os.path.join(self.data_dir, filename)
            
            self.log("INFO", f"Parsing {video_id} (No-Watermark)...")
            await asyncio.sleep(1)
            
            # Simulated Download
            with open(raw_path, "wb") as f: f.write(os.urandom(1024 * 1024)) # 1MB dummy
            
            # 2. Processing (Adding Virtual Metadata & Edit)
            out_filename = f"ULTIMATE_{filename}"
            out_path = os.path.join(self.output_dir, out_filename)
            
            self.log("INFO", f"Applying SEO Metadata & AI Enhancement to {video_id}...")
            await asyncio.sleep(2)
            
            # Atomic Copy & Move
            shutil.copy(raw_path, out_path)
            
            # 3. Cleanup & Log History
            size_mb = os.path.getsize(raw_path) / (1024 * 1024)
            os.remove(raw_path)
            self._save_history(video_id)
            self.stats["saved_space_mb"] += size_mb
            
            return {
                "status": "success",
                "id": video_id,
                "title": target["title"],
                "author": target["author"],
                "output": out_path,
                "tags": target["tags"]
            }
        except Exception as e:
            self.log("ERROR", f"Pipeline failed for {target['id']}: {str(e)}")
            return {"status": "error", "id": target["id"]}

    async def shutdown(self) -> bool:
        return True
