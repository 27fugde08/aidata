import asyncio
import json
import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
import datetime

@dataclass
class Message:
    sender: str
    receiver: str
    content: str
    timestamp: str = field(default_factory=lambda: datetime.datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)

class AgentCollaboration:
    """
    Enables agents to communicate, share insights, and coordinate on complex missions.
    Provides a shared 'Blackboard' and direct messaging.
    """
    def __init__(self, workspace_root: str):
        self.workspace_root = workspace_root
        self.history_path = os.path.join(workspace_root, ".memory/collaboration_history.json")
        self.messages: List[Message] = []
        self.blackboard: Dict[str, Any] = {}
        self._load_history()

    def _load_history(self):
        if os.path.exists(self.history_path):
            try:
                with open(self.history_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.messages = [Message(**m) for m in data.get("messages", [])]
                    self.blackboard = data.get("blackboard", {})
            except Exception as e:
                print(f"Error loading collaboration history: {e}")

    def _save_history(self):
        os.makedirs(os.path.dirname(self.history_path), exist_ok=True)
        data = {
            "messages": [m.__dict__ for m in self.messages],
            "blackboard": self.blackboard
        }
        with open(self.history_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    async def send_message(self, sender: str, receiver: str, content: str, metadata: Dict[str, Any] = None):
        """Sends a message from one agent to another (or 'all')."""
        msg = Message(sender=sender, receiver=receiver, content=content, metadata=metadata or {})
        self.messages.append(msg)
        self._save_history()
        return msg

    def get_messages(self, agent_name: str) -> List[Message]:
        """Gets messages addressed to a specific agent or 'all'."""
        return [m for m in self.messages if m.receiver == agent_name or m.receiver == "all"]

    def update_blackboard(self, key: str, value: Any):
        """Updates a shared variable on the blackboard."""
        self.blackboard[key] = value
        self._save_history()

    def read_blackboard(self, key: str) -> Any:
        """Reads a variable from the blackboard."""
        return self.blackboard.get(key)

    async def broadcast_insight(self, sender: str, insight: str):
        """Broadcasts an insight to all active agents."""
        await self.send_message(sender, "all", f"INSIGHT: {insight}")
