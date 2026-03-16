import os
import importlib.util
import inspect
from typing import List, Callable, Dict

class PluginManager:
    """
    Quản lý các kỹ năng mở rộng (Skills) cho AI.
    Load dynamic các file .py từ thư mục skills/.
    """
    def __init__(self, workspace_root: str):
        self.skills_dir = os.path.join(workspace_root, "skills")
        if not os.path.exists(self.skills_dir):
            os.makedirs(self.skills_dir)
        self.loaded_skills: Dict[str, Callable] = {}

    def load_plugins(self) -> List[Callable]:
        """Quét và load tất cả functions từ thư mục skills."""
        self.loaded_skills = {}
        tools = []
        
        if not os.path.exists(self.skills_dir):
            return []

        for filename in os.listdir(self.skills_dir):
            if filename.endswith(".py") and not filename.startswith("_"):
                file_path = os.path.join(self.skills_dir, filename)
                module_name = filename[:-3]
                
                try:
                    # Dynamic import
                    spec = importlib.util.spec_from_file_location(module_name, file_path)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # Lấy tất cả function không bắt đầu bằng _
                    for name, func in inspect.getmembers(module, inspect.isfunction):
                        if not name.startswith("_"):
                            # Wrap để giữ metadata cho Gemini
                            self.loaded_skills[name] = func
                            tools.append(func)
                except Exception as e:
                    print(f"Error loading skill {filename}: {e}")
                    
        return tools
