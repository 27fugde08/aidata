import os
import json
import datetime
from typing import List, Dict, Any, Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

class AutomationScheduler:
    """
    Quản lý việc lập lịch cho các workflow và automation.
    Hỗ trợ lập lịch theo chu kỳ (Cron) hoặc khoảng thời gian (Interval).
    """
    def __init__(self, workspace_root: str):
        self.workspace_root = workspace_root
        self.scheduler = AsyncIOScheduler()
        self.jobs_file = os.path.join(workspace_root, ".memory/scheduled_jobs.json")
        # Do not start here, start in FastAPI startup
        self._load_jobs()

    def _load_jobs(self):
        if os.path.exists(self.jobs_file):
            try:
                with open(self.jobs_file, "r", encoding="utf-8") as f:
                    jobs = json.load(f)
                    for job_id, job_data in jobs.items():
                        self.add_job(job_id, job_data)
            except:
                pass

    def _save_jobs(self):
        jobs = {}
        for job in self.scheduler.get_jobs():
            # Lưu meta data của job
            jobs[job.id] = {
                "name": job.name,
                "trigger_type": "cron" if isinstance(job.trigger, CronTrigger) else "interval",
                "trigger_args": str(job.trigger), # Đơn giản hóa để lưu trữ
                "task_type": "workflow", # placeholder
                "task_args": {} # placeholder
            }
        
        os.makedirs(os.path.dirname(self.jobs_file), exist_ok=True)
        with open(self.jobs_file, "w", encoding="utf-8") as f:
            json.dump(jobs, f, indent=2)

    def add_job(self, job_id: str, job_data: dict):
        """Thêm một job mới vào scheduler."""
        # Giả lập function thực thi
        async def task_func():
             print(f"Executing scheduled job: {job_id} - {job_data['name']}")
             # Ở đây sẽ gọi Orchestrator.run_workflow
             
        trigger = None
        if job_data["trigger_type"] == "cron":
            # cron expression (e.g. '0 0 * * *')
             trigger = CronTrigger.from_crontab(job_data["trigger_args"])
        else:
             # interval in seconds
             trigger = IntervalTrigger(seconds=int(job_data["trigger_args"]))

        self.scheduler.add_job(
            task_func,
            trigger,
            id=job_id,
            name=job_data["name"],
            replace_existing=True
        )
        self._save_jobs()

    def list_jobs(self) -> List[Dict[str, Any]]:
        """Liệt kê các jobs đang chạy."""
        return [
            {
                "id": job.id,
                "name": job.name,
                "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger)
            }
            for job in self.scheduler.get_jobs()
        ]

    def remove_job(self, job_id: str):
        """Xóa một job."""
        if self.scheduler.get_job(job_id):
            self.scheduler.remove_job(job_id)
            self._save_jobs()
            return True
        return False
