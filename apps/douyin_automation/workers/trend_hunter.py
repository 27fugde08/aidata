from typing import Dict, Any
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from core_kernel.src.core.advanced_orchestrator import AdvancedOrchestrator
from core_kernel.src.shared.logger import logger

class TrendHunter:
    """
    Worker chuyên dụng để săn tìm xu hướng và lập kế hoạch video tự động.
    Sử dụng LangGraph Orchestrator mới (2025).
    """
    def __init__(self):
        try:
            self.orchestrator = AdvancedOrchestrator()
            self.status = "idle"
        except Exception as e:
            logger.error(f"Failed to init AdvancedOrchestrator: {e}")
            self.status = "error"

    async def hunt(self, keyword: str = "technology") -> Dict[str, Any]:
        """
        Thực hiện quy trình săn trend:
        1. Research (Giả lập/API)
        2. Scripting (LangGraph)
        3. Planning (LangGraph)
        """
        if self.status == "error":
            return {"error": "TrendHunter failed to initialize."}

        self.status = "working"
        logger.info(f"TrendHunter started for: {keyword}")
        
        try:
            # Chạy LangGraph Workflow
            # Note: run_mission is blocking, in real app might need running in executor
            result = self.orchestrator.run_mission(keyword)
            
            self.status = "idle"
            return {
                "status": "success",
                "trend_data": result.get("trend_data"),
                "script": result.get("script"),
                "plan": result.get("video_plan")
            }
        except Exception as e:
            logger.error(f"TrendHunting failed: {e}")
            self.status = "error"
            return {"error": str(e)}

if __name__ == "__main__":
    import asyncio
    hunter = TrendHunter()
    res = asyncio.run(hunter.hunt("AI Agent 2025"))
    print(res)
