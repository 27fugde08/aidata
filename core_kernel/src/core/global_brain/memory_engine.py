import asyncio
import os
import json
from typing import List, Dict, Any, Optional
from ..vector_memory import VectorMemory
from ..knowledge_graph import KnowledgeGraph
import config

class GlobalMemoryBrain:
    """
    The 'Unified Brain' of the AI Automation OS.
    Connects Vector Memory (Unstructured) and Knowledge Graph (Structured).
    Provides cross-project and cross-agent context.
    """
    def __init__(self, workspace_root: str = config.WORKSPACE_ROOT):
        self.workspace_root = workspace_root
        self.vector_memory = VectorMemory()
        self.knowledge_graph = KnowledgeGraph(workspace_root)
        self.brain_summary_path = os.path.join(workspace_root, ".memory/brain_summary.json")
        self.summary = self._load_summary()

    def _load_summary(self) -> Dict[str, Any]:
        if os.path.exists(self.brain_summary_path):
            try:
                with open(self.brain_summary_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def _save_summary(self):
        os.makedirs(os.path.dirname(self.brain_summary_path), exist_ok=True)
        with open(self.brain_summary_path, "w", encoding="utf-8") as f:
            json.dump(self.summary, f, indent=2, ensure_ascii=False)

    async def learn_insight(self, insight: str, source: str, category: str = "general"):
        """Stores a new insight into both vector and graph systems."""
        # 1. Vector Memory for search
        await self.vector_memory.add_memory(insight, category=category, metadata={"source": source})
        
        # 2. Update Summary/Stats
        self.summary["total_insights"] = self.summary.get("total_insights", 0) + 1
        self.summary["last_updated"] = asyncio.get_event_loop().time()
        self._save_summary()

    async def get_context_for_task(self, task_description: str, top_k: int = 5) -> str:
        """Retrieves most relevant context from the brain."""
        # Query Vector Memory
        recalled_text = await self.vector_memory.recall(task_description, top_k=top_k)
        
        # Query Graph (optional: extract keywords from task first)
        # For now, simple vector recall is the primary context
        return recalled_text

    def link_entities(self, entity1: str, relation: str, entity2: str):
        """Adds a structured relationship to the Knowledge Graph."""
        self.knowledge_graph.add_relation(entity1, relation, entity2)
