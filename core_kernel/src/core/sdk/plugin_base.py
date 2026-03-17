import os
import json
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List

class AIOSPlugin(ABC):
    """
    Lớp cơ sở mở rộng cho AIOS Plugin (SaaS Standard).
    Cung cấp SDK để Plugin giao tiếp an toàn với Kernel.
    """
    def __init__(self, workspace_root: str, manifest: Dict[str, Any], kernel_services: Any = None):
        self.workspace_root = workspace_root
        self.manifest = manifest
        self.plugin_id = manifest.get("id", "unknown")
        self.version = manifest.get("version", "0.0.1")
        self.kernel = kernel_services # Đối tượng chứa các hàm lõi của Kernel
        self.is_active = False

    @abstractmethod
    async def setup(self) -> bool:
        """Khởi tạo tài nguyên cho Plugin."""
        pass

    @abstractmethod
    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Thực thi logic chính."""
        pass

    @abstractmethod
    async def shutdown(self) -> bool:
        """Giải phóng tài nguyên."""
        pass

    # --- AIOS SDK HELPERS (The "Magic" for Developers) ---

    async def call_llm(self, prompt: str, model: Optional[str] = None) -> str:
        """Gọi trí tuệ nhân tạo của Kernel."""
        if self.kernel and hasattr(self.kernel, "chat"):
            return await self.kernel.chat(prompt, model=model)
        self.log("ERROR", "LLM Service not available in Kernel.")
        return "Error: LLM Service Unavailable"

    def get_config(self, key: str, default: Any = None) -> Any:
        """Lấy cấu hình từ manifest hoặc hệ thống."""
        return self.manifest.get("config", {}).get(key, default)

    async def record_usage(self, amount: float, unit: str = "tokens"):
        """Ghi nhận mức độ sử dụng để tính phí (SaaS Billing)."""
        if self.kernel and hasattr(self.kernel, "billing"):
            await self.kernel.billing.record(self.plugin_id, amount, unit)
        self.log("DEBUG", f"Usage recorded: {amount} {unit}")

    def log(self, level: str, message: str):
        """Hệ thống Logging tập trung."""
        print(f"[{level}] [Plugin:{self.plugin_id}] {message}")

    def get_plugin_data_dir(self) -> str:
        """Thư mục dữ liệu riêng tư của Plugin."""
        path = os.path.join(self.workspace_root, "data", "plugins", self.plugin_id)
        os.makedirs(path, exist_ok=True)
        return path
