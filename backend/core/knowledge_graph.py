import os
import ast
import json
from typing import Dict, List, Any

class KnowledgeGraph:
    """
    Xây dựng bản đồ tri thức cấu trúc của dự án.
    Phân tích quan hệ giữa các file, class, function, API và Workflow.
    """
    def __init__(self, workspace_root: str):
        self.workspace_root = workspace_root
        self.graph_path = os.path.join(workspace_root, ".memory/knowledge_graph.json")
        self.nodes = {} # path: {type, members, links}

    def build_graph(self):
        """Quét toàn bộ workspace và phân tích AST."""
        new_nodes = {}
        for root, _, files in os.walk(self.workspace_root):
            if any(x in root for x in [".git", "__pycache__", "node_modules", "dist", ".memory"]):
                continue
                
            for file in files:
                if file.endswith((".py", ".js", ".html")):
                    path = os.path.relpath(os.path.join(root, file), self.workspace_root)
                    new_nodes[path] = self._analyze_file(os.path.join(root, file))
        
        # Thêm thông tin về Workflows (nếu có)
        self._detect_workflows(new_nodes)
        
        self.nodes = new_nodes
        self._save_graph()
        return self.nodes

    def _analyze_file(self, file_path: str) -> Dict[str, Any]:
        """Phân tích nội dung file dùng AST (cho Python) hoặc Regex (cho JS/HTML)."""
        ext = os.path.splitext(file_path)[1]
        info = {"type": "file", "classes": [], "functions": [], "imports": [], "apis": []}
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                
            if ext == ".py":
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        info["classes"].append(node.name)
                    elif isinstance(node, ast.FunctionDef):
                        info["functions"].append(node.name)
                        # Detect FastAPI/Flask routes
                        for decorator in node.decorator_list:
                            if hasattr(decorator, 'func') and hasattr(decorator.func, 'attr'):
                                if decorator.func.attr in ['get', 'post', 'put', 'delete']:
                                    info["apis"].append(f"{decorator.func.attr.upper()} {decorator.args[0].s if decorator.args else 'unknown'}")
                    elif isinstance(node, ast.Import):
                        for n in node.names: info["imports"].append(n.name)
                    elif isinstance(node, ast.ImportFrom):
                        info["imports"].append(node.module or "")
            elif ext == ".js":
                # Phân tích JS đơn giản qua regex (placeholder)
                import re
                info["functions"] = re.findall(r"function\s+(\w+)", content)
                info["apis"] = re.findall(r"\.(?:get|post|put|delete)\(['\"]([^'\"]+)['\"]", content)
                
            return info
        except Exception as e:
            return {"type": "file", "error": str(e)}

    def _detect_workflows(self, nodes):
        """Phát hiện các workflow được định nghĩa trong dự án."""
        # Giả sử workflow được lưu trong automations/*.json
        automations_dir = os.path.join(self.workspace_root, "automations")
        if os.path.exists(automations_dir):
            for f in os.listdir(automations_dir):
                if f.endswith(".json"):
                    nodes[f"workflow:{f}"] = {"type": "workflow", "source": f}

    def _save_graph(self):
        os.makedirs(os.path.dirname(self.graph_path), exist_ok=True)
        with open(self.graph_path, "w", encoding="utf-8") as f:
            json.dump(self.nodes, f, indent=2)

    def query_relations(self, file_path: str) -> List[str]:
        """Truy vấn các liên kết Semantic của file/node."""
        if file_path in self.nodes:
            return self.nodes[file_path]
        return {}
