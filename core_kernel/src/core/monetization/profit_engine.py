import os
import asyncio
import json
from typing import List, Dict, Any
from ..internet_brain.internet_agent import InternetAgent
from ..global_brain.memory_engine import GlobalMemoryBrain
import config

class ProfitEngine:
    """
    AI Profit Engine.
    Scans for market gaps, affiliate opportunities, and SaaS needs.
    """
    def __init__(self, workspace_root: str, internet_agent: InternetAgent, brain: GlobalMemoryBrain):
        self.workspace_root = workspace_root
        self.internet_agent = internet_agent
        self.brain = brain
        self.profit_ideas_path = os.path.join(workspace_root, ".memory/profit_ideas.json")

    async def find_opportunities(self, niche: str = "AI Automation"):
        """Scans the web for trends and identifies profit opportunities."""
        findings = await self.internet_agent.scan_trends(niche)
        
        # Analyze findings with Brain and propose an opportunity
        # (This would use an LLM call normally, similar to SelfEvolution)
        opportunity = {
            "niche": niche,
            "opportunity": f"Automated {niche} SaaS",
            "reason": "High demand, low competition for specialized micro-SaaS",
            "strategy": "Build a prototype with ProductFactory",
            "timestamp": asyncio.get_event_loop().time()
        }
        
        await self._save_opportunity(opportunity)
        return opportunity

    async def _save_opportunity(self, idea: Dict[str, Any]):
        ideas = []
        if os.path.exists(self.profit_ideas_path):
            try:
                with open(self.profit_ideas_path, "r", encoding="utf-8") as f:
                    ideas = json.load(f)
            except: pass
            
        ideas.append(idea)
        with open(self.profit_ideas_path, "w", encoding="utf-8") as f:
            json.dump(ideas, f, indent=2)
