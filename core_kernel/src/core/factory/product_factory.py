import os
import asyncio
import json
from typing import List, Dict, Any
from ..orchestrator import MultiAgentOrchestrator
from ..file_manager import FileManager
import config

class ProductFactory:
    """
    AI Product Factory.
    Builds products (SaaS, CLIs, Web Apps) inside project environments.
    """
    def __init__(self, workspace_root: str, orchestrator: MultiAgentOrchestrator):
        self.workspace_root = workspace_root
        self.orchestrator = orchestrator
        self.products_db_path = os.path.join(workspace_root, ".memory/products_db.json")

    async def build_product(self, project_name: str, product_type: str, requirement: str):
        """Starts a product build mission within a project."""
        mission_goal = f"Build a {product_type} for project '{project_name}' based on requirements: {requirement}"
        
        async for chunk in self.orchestrator.start_mission(mission_goal):
            print(chunk, end="")
            
        return f"Product '{product_type}' built for project '{project_name}'."

    async def generate_saas(self, project_name: str, niche: str):
        """Specialized mission to build a full-stack SaaS prototype."""
        mission_goal = f"Build a full-stack SaaS (FastAPI + React) for project '{project_name}' in the niche: '{niche}'"
        
        async for chunk in self.orchestrator.start_mission(mission_goal):
            print(chunk, end="")
            
        return f"SaaS prototype for '{niche}' is ready in project '{project_name}'."
