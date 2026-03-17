import sys
import os
import asyncio

# Absolute Imports cho AIOS Enterprise
from agents.manager import ManagerAgent
from agents.coder import CoderAgent
from agents.reviewer import ReviewerAgent
from agents.evaluator import EvaluatorAgent
from agents.internet_agent import InternetAgent
from memory.dev_memory import DevMemory
from core.logger import logger

class DevPipeline:
    """
    Orchestrator cho Dev Workflow: Research -> Manager -> Coder <-> Evaluator -> Done.
    """
    def __init__(self):
        self.researcher = InternetAgent()
        self.manager = ManagerAgent()
        self.coder = CoderAgent()
        self.evaluator = EvaluatorAgent()
        self.memory = DevMemory()

    async def run_mission(self, task_id: str, prompt: str):
        logger.info(f"🚀 [Pipeline] Launching Multi-Agent Mission: {task_id}")
        
        # 1. Research (InternetAgent: Học hỏi từ bên ngoài)
        research_findings = await self.researcher.research(prompt)
        logger.info(f"🔍 [Pipeline] Research results integrated: {research_findings[:100]}...")
        
        # 2. Lấy kinh nghiệm từ quá khứ (Phản tỉnh nội bộ)
        context = self.memory.get_context()
        
        # Kết hợp kiến thức Nội bộ (Memory) và Bên ngoài (Research)
        enriched_context = f"{context}\n\nExternal Research Info:\n{research_findings}"
        
        # 3. Planning (Manager)
        plan = await self.manager.create_plan(prompt)
        
        final_output = []
        overall_status = "success"

        # 4. Execution & Refinement Loop
        for i, step in enumerate(plan):
            logger.info(f"📍 [Pipeline] Processing Step {i+1}/{len(plan)}: {step}")
            
            # Coder thực hiện nhiệm vụ, có thể lặp lại nếu Evaluator từ chối
            attempts = 0
            max_attempts = 3
            step_code = ""
            is_passed = False
            feedback = ""

            while attempts < max_attempts and not is_passed:
                attempts += 1
                logger.info(f"💻 [Pipeline] Coder Attempt {attempts} for: {step}")
                
                # Coder viết code (có tham khảo enriched_context)
                coder_input = f"{step}\nFeedback from previous attempt: {feedback}" if feedback else step
                step_code = await self.coder.write_code(coder_input, enriched_context)
                
                # Evaluator kiểm tra
                is_passed, feedback, score = await self.evaluator.evaluate(step_code, step)
                
                if not is_passed:
                    logger.warning(f"⚠️ [Pipeline] Step {i+1} rejected by Evaluator. Score: {score}/100. Retrying...")

            if not is_passed:
                logger.critical(f"❌ [Pipeline] Mission FAILED at Step {i+1} after {max_attempts} attempts.")
                overall_status = "failed"
                break
            
            final_output.append(step_code)

        # 4. Lưu vào Memory & Reflection
        final_code_full = "\n\n".join(final_output)
        self.memory.log_task(
            task_id=task_id,
            plan=plan,
            final_code=final_code_full,
            status=overall_status,
            feedback="Mission completed with Evaluator audit." if overall_status == "success" else "Rejected by Evaluator."
        )
        
        return {
            "status": overall_status,
            "code": final_code_full,
            "steps_completed": len(final_output)
        }
