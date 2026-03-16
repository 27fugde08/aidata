from typing import List, Dict, Any, Optional, AsyncGenerator
import os
import json
import asyncio
import datetime
from .agent_engine import AgentEngine
from .workflow_engine import WorkflowEngine
from .plugin_manager import PluginManager
from .task_queue.queue import TaskQueue, TaskStatus
from .collaboration.chat import AgentCollaboration
from .model_orchestrator import ModelOrchestrator
from .global_brain.memory_engine import GlobalMemoryBrain
import config

class MultiAgentOrchestrator:
    """
    Tổng chỉ huy (Mission Controller) quản lý đội ngũ AI Agents.
    Phân phối task cho từng agent chuyên biệt thông qua TaskQueue.
    Hỗ trợ phối hợp (Collaboration) và tri thức toàn hệ thống (Global Brain).
    """
    def __init__(self, workspace_root: str = config.WORKSPACE_ROOT):
        self.workspace_root = workspace_root
        self.task_queue = TaskQueue(workspace_root)
        self.collaboration = AgentCollaboration(workspace_root)
        self.model_router = ModelOrchestrator(workspace_root=workspace_root)
        self.global_brain = GlobalMemoryBrain(workspace_root)
        self.workflow_engine = WorkflowEngine(workspace_root)
        self.plugin_manager = PluginManager(workspace_root)
        
        # Cache for initialized agents
        self._agents: Dict[str, AgentEngine] = {}

    def get_agent(self, role: str) -> AgentEngine:
        """Lấy hoặc tạo mới Agent với vai trò cụ thể."""
        if role in self._agents:
            return self._agents[role]
            
        agent = AgentEngine(self.workspace_root)
        
        # Load Plugins
        plugins = self.plugin_manager.load_plugins()
        agent.tools.extend(plugins)
        
        # Role-specific instructions
        role_instructions = {
            "architect": "Software Architect. Focus on structure, classes, and data flow. High-level design.",
            "developer": "Senior Developer. Write high-quality, clean, and optimized code.",
            "tester": "QA Engineer. Write unit tests, test cases, and find logical bugs.",
            "reviewer": "Code Reviewer. Find security issues, performance bottlenecks, and refactoring needs.",
            "manager": "Mission Controller. Break down goals into tasks, coordinate agents, and track progress."
        }
        
        agent.role_instruction = role_instructions.get(role.lower(), "AI Assistant.")
        agent.reload_model()
        
        self._agents[role] = agent
        return agent

    async def start_mission(self, mission_goal: str) -> AsyncGenerator[str, None]:
        """
        Khởi chạy một Mission mới. 
        Quy trình: Goal -> Breakdown (Manager) -> Tasks (Queue) -> Execute (Agents).
        """
        yield f"🎯 Mission Received: {mission_goal}\n"
        
        # 0. Global Brain Retrieval (Learn from past missions)
        yield "🧠 Retrieving global context...\n"
        global_context = await self.global_brain.get_context_for_task(mission_goal)
        if global_context:
            yield f"💡 Insight retrieved from brain: {global_context[:100]}...\n"

        # 1. Task Breakdown (Role: Manager)
        yield "📋 Breaking down mission into tasks...\n"
        manager = self.get_agent("manager")
        
        # Prompt breakdown with global context
        breakdown_prompt = f"""
        MISSION GOAL: {mission_goal}
        
        PAST KNOWLEDGE (GLOBAL BRAIN):
        {global_context}
        
        Hãy phân tích mục tiêu trên và chia nhỏ thành các task cụ thể.
        Trả về kết quả dưới dạng JSON array:
        [
          {{"task": "mô tả task 1", "role": "vai trò thực hiện (architect/developer/etc)", "priority": 1}},
          ...
        ]
        """
        
        breakdown_json = ""
        async for chunk in manager.work_stream(breakdown_prompt):
            breakdown_json += chunk
            
        try:
            if "```json" in breakdown_json:
                breakdown_json = breakdown_json.split("```json")[1].split("```")[0]
            
            tasks = json.loads(breakdown_json)
            for t in tasks:
                tid = await self.task_queue.add_task(
                    description=t["task"],
                    role=t["role"],
                    priority=t.get("priority", 0)
                )
                yield f"  ✅ Task Created [{tid}]: {t['task']} (Role: {t['role']})\n"
        except Exception as e:
            yield f"❌ Error in task breakdown: {str(e)}\n"
            return

        # 2. Execute Tasks
        yield "\n🚀 Starting execution loop...\n"
        while True:
            task = await self.task_queue.get_next_task()
            if not task:
                break # All tasks done
                
            yield f"\n⚡ Executing Task [{task.id}]: {task.description} (Role: {task.role})\n"
            
            agent = self.get_agent(task.role)
            
            # Context priority: Global Brain -> Blackboard
            task_context = await self.global_brain.get_context_for_task(task.description)
            blackboard_context = json.dumps(self.collaboration.blackboard, indent=2)
            
            exec_prompt = f"""
            GLOBAL CONTEXT:
            {task_context}
            
            WORKING BLACKBOARD:
            {blackboard_context}
            
            YOUR TASK:
            {task.description}
            
            Hãy thực hiện nhiệm vụ của bạn.
            """
            
            output = ""
            async for chunk in agent.work_stream(exec_prompt):
                yield chunk
                output += chunk
                
            # 3. Learning (Feedback into Global Brain)
            await self.global_brain.learn_insight(
                insight=f"Task Result ({task.role}): {output[:500]}",
                source=f"task_{task.id}",
                category="mission_insight"
            )
            
            # Update Task & Blackboard
            await self.task_queue.update_task(task.id, TaskStatus.COMPLETED, {"output": output})
            self.collaboration.update_blackboard(f"output_{task.id}", output[:500] + "...")
            
            yield f"\n✅ Task [{task.id}] completed and learned.\n"

        yield "\n🏁 Mission Accomplished."

    async def run_workflow(self, workflow_name: str, initial_context: str):
        """Legacy workflow support, refactored to use agents consistently."""
        workflow = self.workflow_engine.load_workflow(workflow_name)
        if "error" in workflow:
            workflow = self.workflow_engine.get_default_dev_workflow()
            
        steps = workflow.get("steps", [])
        context = initial_context
        
        yield f"🚀 Starting Workflow: {workflow.get('name')}\n"
        
        for step in steps:
            role = step["role"]
            task = step["task"]
            yield f"\n👤 Agent: **{role.upper()}**\n"
            
            agent = self.get_agent(role)
            step_prompt = f"CONTEXT:\n{context}\n\nTASK:\n{task}"
            
            step_output = ""
            async for chunk in agent.work_stream(step_prompt):
                yield chunk
                step_output += chunk
                
            context = f"PREVIOUS ({role}): {step_output}\n" + context
            
        yield "\n✅ Completed."
