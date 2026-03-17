from typing import TypedDict, Annotated, Sequence
import operator
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    trend_data: str
    script: str
    video_plan: str

class AdvancedOrchestrator:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or config.GEMINI_API_KEY
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is missing")
            
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash", # Using stable model for LangChain integration
            google_api_key=self.api_key,
            temperature=0.7
        )
        self.workflow = self._build_graph()

    def _build_graph(self):
        # Define Nodes
        def research_node(state: AgentState):
            query = state["messages"][-1].content
            # Simulate research (in production, use tools)
            trend_report = f"Analyzed trends for: {query}. Found high engagement in niche X."
            return {"trend_data": trend_report, "messages": [SystemMessage(content=trend_report)]}

        def script_node(state: AgentState):
            trend = state["trend_data"]
            prompt = f"Based on this trend: '{trend}', write a viral 60s script."
            response = self.llm.invoke([HumanMessage(content=prompt)])
            return {"script": response.content}

        def planning_node(state: AgentState):
            script = state["script"]
            prompt = f"Create a shot list for this script: \n{script}"
            response = self.llm.invoke([HumanMessage(content=prompt)])
            return {"video_plan": response.content}

        # Build Graph
        workflow = StateGraph(AgentState)
        workflow.add_node("researcher", research_node)
        workflow.add_node("scriptwriter", script_node)
        workflow.add_node("director", planning_node)

        workflow.set_entry_point("researcher")
        workflow.add_edge("researcher", "scriptwriter")
        workflow.add_edge("scriptwriter", "director")
        workflow.add_edge("director", END)

        return workflow.compile()

    def run_mission(self, topic: str):
        """Runs the autonomous mission."""
        inputs = {"messages": [HumanMessage(content=topic)]}
        result = self.workflow.invoke(inputs)
        return result
