from typing import Tuple, Dict, Any
from core.logger import logger

class EvaluatorAgent:
    """
    Agent chuyên trách việc đánh giá kết quả (Critique).
    Có quyền từ chối (Reject) nếu kết quả không đạt chuẩn chất lượng.
    """
    async def evaluate(self, code: str, requirements: str) -> Tuple[bool, str, int]:
        """
        Đánh giá code dựa trên yêu cầu.
        Trả về: (Is_Success, Feedback, Quality_Score)
        """
        logger.info(f"🧐 [Evaluator] Auditing code against requirements: {requirements[:50]}...")
        
        # Mô phỏng logic đánh giá chuyên sâu
        score = 0
        feedback = []
        
        # 1. Kiểm tra cấu trúc cơ bản
        if "def" in code or "class" in code:
            score += 40
        else:
            feedback.append("Missing core structure (functions/classes).")
            
        # 2. Kiểm tra xử lý lỗi
        if "try:" in code or "except" in code:
            score += 30
        else:
            feedback.append("Missing error handling blocks.")
            
        # 3. Kiểm tra chú thích
        if '"""' in code or "'''" in code:
            score += 20
        else:
            feedback.append("Missing docstrings/documentation.")
            
        # 4. Kiểm tra logic (Mô phỏng)
        score += 10 # Base score cho logic sơ bộ
        
        is_passed = score >= 70
        final_feedback = " | ".join(feedback) if feedback else "Perfect implementation."
        
        if is_passed:
            logger.info(f"✅ [Evaluator] Code passed with score: {score}/100")
        else:
            logger.warning(f"❌ [Evaluator] Code rejected! Score: {score}/100. Feedback: {final_feedback}")
            
        return is_passed, final_feedback, score
