import asyncio
from ..tools.web_search import WebSearch
from ..global_brain.memory_engine import GlobalMemoryBrain
from typing import List, Dict, Any

class InternetAgent:
    """
    Autonomous Internet Agent.
    Can scan trends, research topics, and feed insights into the Global Brain.
    """
    def __init__(self, global_brain: GlobalMemoryBrain):
        self.web_search = WebSearch()
        self.brain = global_brain

    async def research_topic(self, topic: str):
        """Researches a topic and stores findings in Global Memory."""
        results = await self.web_search.search(topic)
        if not results:
            return "Topic research failed (no results)."
        
        snippets = "\n".join([f"- {r['title']}: {r['snippet']}" for r in results])
        summary = f"RESEARCH ON '{topic}':\n{snippets}"
        
        # Learn from this research
        await self.brain.learn_insight(
            insight=summary,
            source="internet_agent",
            category="research"
        )
        return summary

    async def scan_trends(self, niche: str = "AI Automation"):
        """Scans the web for trends and updates the brain."""
        query = f"latest trends in {niche} 2026"
        trend_summary = await self.research_topic(query)
        
        # Extract keywords and update Knowledge Graph (Simple approach for now)
        # This will evolve as the agent gets smarter
        return trend_summary

    async def find_tools(self, requirement: str):
        """Finds new tools on GitHub or web to fulfill a requirement."""
        query = f"github tools for {requirement}"
        return await self.research_topic(query)
