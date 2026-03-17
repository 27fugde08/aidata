import os
import json
import importlib.util
import inspect
from typing import List, Callable, Dict, Any, Type, Optional
from .sdk.plugin_base import AIOSPlugin

class PluginManager:
    """
    Quản lý hệ sinh thái Plugin cho AIOS Kernel.
    Hỗ trợ nạp Kernel Services vào SDK của Plugin.
    """
    def __init__(self, workspace_root: str, kernel_services: Any = None):
        self.workspace_root = workspace_root
        self.kernel_services = kernel_services # Đây là cầu nối LLM/Billing/Storage
        self.plugins_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "plugins")
        self.skills_dir = os.path.join(workspace_root, "skills")
        
        os.makedirs(self.plugins_dir, exist_ok=True)
        os.makedirs(self.skills_dir, exist_ok=True)
        
        self.plugins: Dict[str, AIOSPlugin] = {}

    def load_plugins(self) -> List[Callable]:
        """Tải toàn bộ Plugin SaaS và Skill cũ. Chỉ tải SaaS plugins nếu chưa được nạp."""
        tools = self._load_legacy_skills()
        
        if not self.plugins:
            self._load_saas_plugins()
        
        for plugin_id, plugin in self.plugins.items():
            async def plugin_tool(payload: Dict[str, Any] = {}):
                return await plugin.execute(payload)
            
            plugin_tool.__name__ = f"plugin_{plugin_id.replace('.', '_')}"
            plugin_tool.__doc__ = plugin.manifest.get("description", "AIOS Plugin.")
            tools.append(plugin_tool)
            
        return tools

    def reload_plugins(self) -> List[Callable]:
        """Xóa cache và tải lại toàn bộ plugin/skill."""
        self.plugins = {}
        self.loaded_skills = {}
        return self.load_plugins()

    def get_plugin(self, plugin_id: str) -> Optional[AIOSPlugin]:
        """Lấy một plugin theo ID."""
        return self.plugins.get(plugin_id)

    def _load_saas_plugins(self):
        """Quét và tải AIOS Plugins chuẩn SaaS."""
        for entry in os.listdir(self.plugins_dir):
            plugin_path = os.path.join(self.plugins_dir, entry)
            if not os.path.isdir(plugin_path) or not os.path.exists(os.path.join(plugin_path, "manifest.json")):
                continue
                
            try:
                with open(os.path.join(plugin_path, "manifest.json"), "r", encoding="utf-8") as f:
                    manifest = json.load(f)
                
                plugin_id = manifest.get("id")
                entry_point = manifest.get("entry_point", "main.py")
                class_name = manifest.get("class", "Plugin")
                
                # Dynamic load class
                module_path = os.path.join(plugin_path, entry_point)
                spec = importlib.util.spec_from_file_location(f"plugin.{plugin_id}", module_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                plugin_class = getattr(module, class_name)
                if issubclass(plugin_class, AIOSPlugin):
                    # Nạp KERNEL SERVICES vào Plugin khi khởi tạo
                    plugin_instance = plugin_class(self.workspace_root, manifest, self.kernel_services)
                    self.plugins[plugin_id] = plugin_instance
                    print(f"📦 [PluginManager] Loaded SaaS Plugin: {plugin_id}")
                else:
                    print(f"⚠️ [PluginManager] Invalid base class for {plugin_id}")
            except Exception as e:
                print(f"❌ [PluginManager] Failed to load {entry}: {str(e)}")

    def load_modular_apps(self, fastapi_app: Any):
        """
        Tự động quét thư mục apps/ ở root và nạp các router vào FastAPI.
        Cơ chế này đảm bảo Kernel chạy độc lập, app lỗi không làm sập Kernel.
        """
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        apps_dir = os.path.join(project_root, "apps")
        
        if not os.path.exists(apps_dir):
            return

        print(f"🔍 [AppDiscovery] Scanning for modular apps in {apps_dir}...")
        
        for entry in os.listdir(apps_dir):
            app_path = os.path.join(apps_dir, entry)
            if not os.path.isdir(app_path) or entry.startswith("__"):
                continue
                
            try:
                # Tìm kiếm router trong api/ folder của mỗi app
                api_module_path = f"apps.{entry}.api"
                # Thử tìm module 'api' bên trong app
                try:
                    # Kiểm tra xem có file api/__init__.py hoặc api.py không
                    importlib.import_module(api_module_path)
                except ImportError:
                    # Thử tìm file cụ thể nếu app cấu trúc khác (ví dụ douyin.py)
                    continue

                # Quét tất cả các file .py trong thư mục api/ của app đó
                api_dir = os.path.join(app_path, "api")
                if os.path.exists(api_dir):
                    for file in os.listdir(api_dir):
                        if file.endswith(".py") and not file.startswith("__"):
                            module_name = file[:-3]
                            full_module_path = f"apps.{entry}.api.{module_name}"
                            
                            try:
                                mod = importlib.import_module(full_module_path)
                                if hasattr(mod, "router"):
                                    # Nạp router với prefix tự động
                                    prefix = f"/api/v1/{entry}"
                                    if module_name != entry and module_name != "router":
                                        prefix += f"/{module_name}"
                                        
                                    fastapi_app.include_router(mod.router, prefix=prefix, tags=[entry.replace("_", " ").title()])
                                    print(f"✅ [AppDiscovery] Mounted: {entry} -> {prefix}")
                            except Exception as e:
                                print(f"⚠️ [AppDiscovery] Failed to mount module {full_module_path}: {e}")
            except Exception as e:
                print(f"❌ [AppDiscovery] Error processing app {entry}: {e}")
