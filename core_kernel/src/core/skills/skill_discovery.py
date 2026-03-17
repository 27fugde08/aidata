import os
import asyncio
import json
from typing import List, Dict, Any
from ..skill_runner import SkillRunner
from ..internet_brain.internet_agent import InternetAgent

class SkillDiscovery:
    """
    Auto Skill Discovery.
    Finds new tools on GitHub or web, creates skill modules, and integrates them.
    """
    def __init__(self, workspace_root: str, internet_agent: InternetAgent):
        self.workspace_root = workspace_root
        self.internet_agent = internet_agent
        self.runner = SkillRunner(workspace_root)
        self.skills_db_path = os.path.join(workspace_root, ".memory/skills_db.json")
        self.skills_dir = os.path.join(workspace_root, "backend/core/skills")
        os.makedirs(self.skills_dir, exist_ok=True)

    async def discover_new_skill(self, requirement: str):
        """Searches for a tool and attempts to 'learn' it."""
        # 1. Search for a tool
        findings = await self.internet_agent.find_tools(requirement)
        
        # 2. Extract GitHub URLs (Simple regex for now)
        import re
        github_urls = re.findall(r"(https://github\.com/[\w\-]+/[\w\-]+)", findings)
        
        if not github_urls:
            return "No GitHub tools found for this requirement."
            
        target_repo = github_urls[0]
        repo_name = target_repo.split("/")[-1]
        
        # 3. Clone or download (placeholder for safety/complexity)
        # In a real system, we'd clone into a sandbox and analyze
        return f"Discovered potential tool: {target_repo}. Analysis pending sandbox verification."

    async def create_skill_wrapper(self, skill_name: str, code: str):
        """Manually or automatically creates a new skill module."""
        file_path = os.path.join(self.skills_dir, f"{skill_name.lower()}.py")
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(code)
            
        # Update skills DB
        await self._register_skill(skill_name, file_path)
        return f"New skill '{skill_name}' integrated at {file_path}"

    async def _register_skill(self, name: str, path: str):
        skills_db = {}
        if os.path.exists(self.skills_db_path):
            try:
                with open(self.skills_db_path, "r", encoding="utf-8") as f:
                    skills_db = json.load(f)
            except: pass
            
        skills_db[name] = {
            "path": os.path.relpath(path, self.workspace_root),
            "added_at": asyncio.get_event_loop().time()
        }
        
        with open(self.skills_db_path, "w", encoding="utf-8") as f:
            json.dump(skills_db, f, indent=2)
