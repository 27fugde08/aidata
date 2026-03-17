from memory.reflection_memory import ReflectionMemory
from typing import Dict, Any, List

class ReflectionEngine:
    """
    Engine phản tỉnh đa tiêu chí, giúp Agent tự học hỏi sau mỗi task.
    """
    def __init__(self):
        self.memory = ReflectionMemory()
        self.rubric = [
            "Accuracy: Did the task meet all technical requirements?",
            "Efficiency: Was the execution optimal in terms of time/resources?",
            "Security: Are there any vulnerabilities introduced?",
            "Maintainability: Is the output clean and well-structured?",
            "User Experience: Does the result provide clear value/feedback?"
        ]

    async def reflect(self, task_name: str, status: str, result: str) -> Dict[str, str]:
        """
        Phân tích kết quả dựa trên rubric và lưu vào Learning Memory.
        """
        print(f"🧠 [ReflectionEngine] Deep analyzing: {task_name}")
        
        # Ở phiên bản cao cấp, ta có thể dùng LLM để tự động phân tích rubric này.
        # Hiện tại, ta sẽ giả lập logic phân tích dựa trên chuỗi kết quả.
        
        insight = ""
        improvement = ""

        if status == "done":
            if "SUCCESS" in result:
                insight = f"Task '{task_name}' succeeded. Core logic followed technical specs."
                improvement = "Standardize this pattern for future similar features."
            else:
                insight = f"Task '{task_name}' completed but with potential edge case issues."
                improvement = "Add unit tests to verify boundaries in next iteration."
        else:
            insight = f"Failure in '{task_name}'. Execution broke during the middle phase."
            improvement = "Analyze state management and add checkpointing for recovery."

        # Lưu vào Learning Memory (Dữ liệu này sẽ được dùng cho Few-shot prompting lần sau)
        self.memory.add_learning(task_name, status, insight, improvement)
        
        return {
            "insight": insight,
            "improvement": improvement
        }

    def get_past_context(self, task_name: str) -> str:
        """Lấy 3 bài học gần nhất liên quan đến task hiện tại."""
        return self.memory.get_learnings_for_task(task_name)
