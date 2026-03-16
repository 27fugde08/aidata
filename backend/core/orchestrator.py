from typing import List, Dict, Any, Optional
import os
import json
import asyncio
from .agent_engine import AgentEngine
from .workflow_engine import WorkflowEngine
from .plugin_manager import PluginManager

class MultiAgentOrchestrator:
    """
    Tổng chỉ huy (Orchestrator) quản lý đội ngũ AI Agents.
    Phân phối task cho từng agent chuyên biệt.
    """
    def __init__(self, workspace_root: str, api_key: str):
        self.workspace_root = workspace_root
        self.api_key = api_key
        self.workflow_engine = WorkflowEngine(workspace_root)
        self.plugin_manager = PluginManager(workspace_root)
        
        # Load Plugins để cung cấp cho các agent con
        self.plugins = self.plugin_manager.load_plugins()

    def create_agent(self, role: str) -> AgentEngine:
        """Tạo một Agent với vai trò cụ thể."""
        agent = AgentEngine(self.workspace_root, self.api_key)
        
        # Gán thêm tools từ Plugins
        agent.tools.extend(self.plugins)
        agent.reload_model() # Re-init model với tools mới
        
        # Cấu hình System Instruction riêng cho từng Role
        role_instructions = {
            "architect": "Bạn là Kiến trúc sư phần mềm. Tập trung vào cấu trúc thư mục, thiết kế class, và flow dữ liệu. KHÔNG viết chi tiết code.",
            "developer": "Bạn là Senior Developer. Nhiệm vụ là viết code chất lượng cao, tối ưu và clean code.",
            "tester": "Bạn là QA Engineer. Viết test case, unit test và tìm lỗi logic.",
            "reviewer": "Bạn là Code Reviewer. Đánh giá code, tìm lỗi bảo mật và đề xuất tối ưu.",
            "security": "Bạn là Security Auditor. Phân tích code để tìm lỗ hổng bảo mật (SQL Injection, XSS, v.v.) và đề xuất cách khắc phục.",
            "devops": "Bạn là DevOps Engineer. Cấu hình Docker, CI/CD, script triển khai và quản lý môi trường.",
            "manager": "Bạn là Project Manager. Lên kế hoạch và chia nhỏ task."
        }
        
        agent.role_instruction = role_instructions.get(role.lower(), "Bạn là AI Assistant.")
        return agent

    async def run_workflow(self, workflow_name: str, initial_context: str):
        """Chạy một quy trình làm việc với nhiều agent phối hợp."""
        workflow = self.workflow_engine.load_workflow(workflow_name)
        if "error" in workflow:
            # Fallback nếu không tìm thấy, dùng default
            workflow = self.workflow_engine.get_default_dev_workflow()
            
        steps = workflow.get("steps", [])
        history = []
        
        yield f"🚀 Starting Workflow: {workflow.get('name')}\n"
        
        context = initial_context
        
        for i, step in enumerate(steps):
            role = step["role"]
            task = step["task"]
            
            yield f"\n👤 Switch to Agent: **{role.upper()}**\nTask: {task}\n"
            
            # Khởi tạo agent chuyên biệt
            agent = self.create_agent(role)
            
            # Tạo prompt kết hợp context từ bước trước
            step_prompt = f"""
            CONTEXT TỪ CÁC BƯỚC TRƯỚC:
            {context}
            
            NHIỆM VỤ CỦA BẠN ({role}):
            {task}
            
            Hãy thực hiện nhiệm vụ trên.
            """
            
            # Chạy agent và stream kết quả
            step_output = ""
            async for chunk in agent.work_stream(step_prompt):
                yield chunk
                step_output += chunk
                
            # Cập nhật context cho bước sau
            context = f"PREVIOUS STEP OUTPUT ({role}):\n{step_output}\n\n" + context
            history.append({"role": role, "output": step_output})
            
            # Save Checkpoint
            try:
                checkpoint_path = os.path.join(self.workspace_root, ".workflow_state.json")
                with open(checkpoint_path, "w", encoding="utf-8") as f:
                    json.dump({
                        "workflow": workflow_name,
                        "step": i + 1,
                        "history": history,
                        "timestamp": asyncio.get_event_loop().time()
                    }, f, indent=2)
            except Exception as e:
                yield f"\n⚠️ Warning: Failed to save checkpoint: {str(e)}\n"
            
        yield "\n✅ Workflow Completed."
