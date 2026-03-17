import os
import asyncio
import json
from typing import List, Dict, Any
from ..model_orchestrator import ModelOrchestrator
from ..global_brain.memory_engine import GlobalMemoryBrain
import config

class SelfEvolution:
    """
    Self Evolution System (Basic).
    Analyzes logs and successful workflows to propose system improvements.
    Can generate patches for configuration or prompts.
    """
    def __init__(self, workspace_root: str, global_brain: GlobalMemoryBrain):
        self.workspace_root = workspace_root
        self.brain = global_brain
        self.model_router = ModelOrchestrator(workspace_root=workspace_root)
        self.improvements_path = os.path.join(workspace_root, ".memory/proposed_improvements.json")

    async def analyze_and_evolve(self):
        """Analyzes recent performance and proposes an improvement."""
        # 1. Get recent insights from brain
        insights = await self.brain.get_context_for_task("system performance and bottlenecks", top_k=10)
        
        # 2. Use LLM to propose improvement
        prompt = f"""
        RELEVANT SYSTEM INSIGHTS:
        {insights}
        
        Bạn là hệ thống Tự Tiến Hóa (Self-Evolution). 
        Hãy phân tích dữ liệu trên và đề xuất 1 cải tiến cụ thể cho hệ thống AI Automation OS.
        Cải tiến có thể là: prompt mới cho agent, cấu hình model tối ưu hơn, hoặc một logic tool mới.
        
        Trả về kết quả JSON:
        {{
          "improvement": "mô tả",
          "reason": "tại sao",
          "action_type": "patch/prompt/config",
          "target_file": "path/to/file",
          "proposed_change": "code hoặc text mới"
        }}
        """
        
        proposal_json = await self.model_router.chat(prompt, model="gemini-2.0-flash")
        
        # 3. Store proposal for review (Autonomous apply is Phase 4)
        try:
            if "```json" in proposal_json:
                proposal_json = proposal_json.split("```json")[1].split("```")[0]
            
            proposal = json.loads(proposal_json)
            await self._save_proposal(proposal)
            return f"Proposed improvement: {proposal['improvement']}"
        except Exception as e:
            return f"Evolution analysis failed: {str(e)}"

    async def _save_proposal(self, proposal: Dict[str, Any]):
        proposals = []
        if os.path.exists(self.improvements_path):
            try:
                with open(self.improvements_path, "r", encoding="utf-8") as f:
                    proposals = json.load(f)
            except: pass
            
        proposals.append({
            **proposal,
            "timestamp": asyncio.get_event_loop().time(),
            "status": "pending_review"
        })
        
        with open(self.improvements_path, "w", encoding="utf-8") as f:
            json.dump(proposals, f, indent=2)
