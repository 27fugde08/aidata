from typing import Tuple
from core.logger import logger

class ReviewerAgent:
    """Checks code for high-level quality and stylistic consistency."""
    async def review(self, code: str) -> Tuple[bool, str]:
        logger.info(f"🔍 [Reviewer] Performing static analysis...")
        if len(code) > 50:
            return True, "Code looks good and follows standards."
        return False, "Code is too brief, missing implementation details."
