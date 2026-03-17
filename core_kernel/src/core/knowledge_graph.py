import os
import ast
import json
import datetime
from typing import Dict, List, Any, Optional

class KnowledgeGraph:
    """
    Xây dựng bản đồ tri thức cấu trúc của dự án.
    Phân tích quan hệ giữa các file, class, function, API và Workflow.
    Hỗ trợ quan hệ Semantic (ngữ nghĩa) tự định nghĩa.
    """
    def __init__(self, workspace_root: str):
        self.workspace_root = workspace_root
        self.graph_path = os.path.join(workspace_root, ".memory/knowledge_graph.json")
        self.nodes = {} # path: {type, members, links}
        self.relations = [] # [{source, relation, target}]
        self._load_graph()

    def _load_graph(self):
        if os.path.exists(self.graph_path):
            try:
                with open(self.graph_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.nodes = data.get("nodes", {})
                    self.relations = data.get("relations", [])
            except: pass

    def _save_graph(self):
        os.makedirs(os.path.dirname(self.graph_path), exist_ok=True)
        data = {
            "nodes": self.nodes,
            "relations": self.relations,
            "last_updated": datetime.datetime.now().isoformat()
        }
        with open(self.graph_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def add_relation(self, source: str, relation: str, target: str):
        """Adds a semantic relation between two entities."""
        rel = {"source": source, "relation": relation, "target": target}
        if rel not in self.relations:
            self.relations.append(rel)
            self._save_graph()

    def add_node(self, name: str, node_type: str, metadata: Dict[str, Any] = None):
        """Adds a manual node (e.g., 'Skill:WebSearch')."""
        self.nodes[name] = {
            "type": node_type,
            "metadata": metadata or {},
            "added_at": datetime.datetime.now().isoformat()
        }
        self._save_graph()

    def query_relations(self, entity: str) -> List[Dict[str, str]]:
        """Finds all relations connected to an entity."""
        return [r for r in self.relations if r["source"] == entity or r["target"] == entity]

    def build_graph(self):
        """Quét toàn bộ workspace và phân tích AST."""
        for root, _, files in os.walk(self.workspace_root):
            if any(x in root for x in [".git", "__pycache__", "node_modules", "dist", ".memory"]):
                continue
                
            for file in files:
                if file.endswith((".py", ".js", ".html")):
                    path = os.path.relpath(os.path.join(root, file), self.workspace_root)
                    self.nodes[path] = self._analyze_file(os.path.join(root, file))
        
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
                        for decorator in node.decorator_list:
                            if hasattr(decorator, 'func') and hasattr(decorator.func, 'attr'):
                                if decorator.func.attr in ['get', 'post', 'put', 'delete']:
                                    info["apis"].append(f"{decorator.func.attr.upper()} {decorator.args[0].s if decorator.args else 'unknown'}")
                    elif isinstance(node, ast.Import):
                        for n in node.names: info["imports"].append(n.name)
                    elif isinstance(node, ast.ImportFrom):
                        info["imports"].append(node.module or "")
            return info
        except Exception as e:
            return {"type": "file", "error": str(e)}
