import os
from tinydb import TinyDB, Query
from datetime import datetime

class DatabaseManager:
    def __init__(self):
        root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
        db_path = os.path.join(root, "database/studio_db.json")
        self.db = TinyDB(db_path)
        self.projects = self.db.table('projects')
        self.shorts = self.db.table('shorts')

    def create_project(self, video_id, title, url):
        project = {
            "id": video_id,
            "title": title,
            "url": url,
            "created_at": datetime.now().isoformat(),
            "status": "initialized",
            "transcript": None,
            "highlights": []
        }
        self.projects.insert(project)
        return project

    def update_project(self, video_id, data):
        self.projects.update(data, Query().id == video_id)

    def get_project(self, video_id):
        return self.db.table('projects').get(Query().id == video_id)

    def list_projects(self):
        return self.projects.all()

    def add_short(self, short_data):
        self.shorts.insert(short_data)

    def get_shorts_by_project(self, video_id):
        return self.shorts.search(Query().project_id == video_id)
