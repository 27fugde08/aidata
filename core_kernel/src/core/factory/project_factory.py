import os
import asyncio
import json
from typing import List, Dict, Any
from ..orchestrator import MultiAgentOrchestrator
from ..file_manager import FileManager
import config

class ProjectFactory:
    """
    AI Project Factory.
    Can autonomously spawn new project directories, initialize git, and set up environments.
    """
    def __init__(self, workspace_root: str, orchestrator: MultiAgentOrchestrator):
        self.workspace_root = workspace_root
        self.orchestrator = orchestrator
        self.fm = FileManager(workspace_root)
        self.projects_db_path = os.path.join(workspace_root, ".memory/projects_db.json")
        self.projects_dir = os.path.join(workspace_root, "factory/projects")
        os.makedirs(self.projects_dir, exist_ok=True)

    async def spawn_project(self, name: str, description: str):
        """Creates a new project environment and starts an initial mission."""
        project_path = os.path.join(self.projects_dir, name.lower().replace(" ", "-"))
        os.makedirs(project_path, exist_ok=True)
        
        # 1. Initialize project structure
        self.fm.write(f"{project_path}/README.md", f"# {name}\n\n{description}")
        
        # 2. Register project
        await self._register_project(name, project_path, description)
        
        # 3. Start initial architecture mission
        mission_goal = f"Design the software architecture for project '{name}': {description}"
        async for chunk in self.orchestrator.start_mission(mission_goal):
            # Log progress (could be streamed to a dashboard)
            print(chunk, end="")
            
        return f"Project '{name}' spawned at {project_path}"

    async def _register_project(self, name: str, path: str, description: str):
        projects_db = []
        if os.path.exists(self.projects_db_path):
            try:
                with open(self.projects_db_path, "r", encoding="utf-8") as f:
                    projects_db = json.load(f)
            except: pass
            
        projects_db.append({
            "name": name,
            "path": os.path.relpath(path, self.workspace_root),
            "description": description,
            "created_at": asyncio.get_event_loop().time()
        })
        
        with open(self.projects_db_path, "w", encoding="utf-8") as f:
            json.dump(projects_db, f, indent=2)
