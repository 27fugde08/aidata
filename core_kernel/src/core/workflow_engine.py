import json
import os
from typing import List, Dict, Any

class WorkflowEngine:
    """
    Quản lý quy trình làm việc tự động.
    Lưu trữ và thực thi các template workflow.
    """
    def __init__(self, workspace_root: str):
        self.workflow_dir = os.path.join(workspace_root, "workflows")
        if not os.path.exists(self.workflow_dir):
            os.makedirs(self.workflow_dir)

    def list_workflows(self) -> List[str]:
        if not os.path.exists(self.workflow_dir):
            return []
        return [f[:-5] for f in os.listdir(self.workflow_dir) if f.endswith(".json")]

    def load_workflow(self, name: str) -> Dict[str, Any]:
        path = os.path.join(self.workflow_dir, f"{name}.json")
        if not os.path.exists(path):
            return {"error": "Workflow not found"}
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_workflow(self, name: str, content: Dict[str, Any]):
        path = os.path.join(self.workflow_dir, f"{name}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(content, f, indent=4)
            
    def get_default_dev_workflow(self):
        return {
            "name": "Full Feature Development",
            "steps": [
                {"role": "architect", "task": "Design structure"},
                {"role": "developer", "task": "Write code based on design"},
                {"role": "tester", "task": "Write unit tests"},
                {"role": "reviewer", "task": "Review code quality"}
            ]
        }
