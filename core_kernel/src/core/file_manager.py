import os
import shutil
from typing import List, Dict, Optional

class FileManager:
    """
    Quản lý file an toàn cho AI IDE.
    Mọi thao tác bắt buộc nằm trong ROOT_DIR (thường là spaceofduy).
    """
    def __init__(self, root_dir: str):
        self.root_dir = os.path.abspath(root_dir)
        if not os.path.exists(self.root_dir):
            os.makedirs(self.root_dir)

    def get_safe_path(self, rel_path: str) -> str:
        """Đảm bảo path luôn nằm trong root."""
        full_path = os.path.abspath(os.path.join(self.root_dir, rel_path))
        if not full_path.startswith(self.root_dir):
            raise PermissionError(f"Access denied: {rel_path} is outside workspace")
        return full_path

    def list_tree(self, path: str = "") -> List[Dict]:
        """Trả về cấu trúc cây thư mục."""
        target = self.get_safe_path(path)
        tree = []
        for item in os.listdir(target):
            item_path = os.path.join(target, item)
            rel_path = os.path.relpath(item_path, self.root_dir).replace("\\", "/")
            is_dir = os.path.isdir(item_path)
            tree.append({
                "name": item,
                "path": rel_path,
                "type": "directory" if is_dir else "file",
                "children": self.list_tree(rel_path) if is_dir else []
            })
        return tree

    def read(self, path: str) -> str:
        with open(self.get_safe_path(path), "r", encoding="utf-8") as f:
            return f.read()

    def write(self, path: str, content: str):
        full_path = self.get_safe_path(path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)

    def delete(self, path: str):
        full_path = self.get_safe_path(path)
        if os.path.isdir(full_path):
            shutil.rmtree(full_path)
        else:
            os.remove(full_path)
