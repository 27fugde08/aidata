from typing import List, Dict, Any
from core.tools.web_search import WebSearchTool
from core.logger import logger

class InternetAgent:
    """
    Researcher: Chuyên gia tìm kiếm các giải pháp, dự án mở để học hỏi và cập nhật.
    """
    def __init__(self):
        self.search_tool = WebSearchTool()

    async def research(self, topic: str) -> str:
        logger.info(f"🔍 [InternetAgent] Investigating: {topic}")
        
        # 1. Thực hiện tìm kiếm
        results = await self.search_tool.search(topic)
        
        # 2. Tổng hợp kiến thức (Lấy tinh túy từ các nguồn)
        knowledge_summary = f"Research Findings for: {topic}\n"
        for i, res in enumerate(results):
            knowledge_summary += f"{i+1}. {res['title']}: {res['snippet']} ({res['link']})\n"
            
        # 3. Kết luận và đề xuất áp dụng vào AIOS
        proposal = f"\nAIOS Proposal: Implement {topic} using the patterns found above for stability."
        
        return knowledge_summary + proposal
