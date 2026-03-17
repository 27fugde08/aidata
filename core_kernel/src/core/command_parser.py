import re
from typing import Dict, Any, Optional

class CommandParser:
    """
    Phân tích cú pháp lệnh từ chuỗi văn bản.
    Ví dụ: "/aios run update_os_health_ui --param value"
    """
    @staticmethod
    def parse(raw_command: str) -> Optional[Dict[str, Any]]:
        if not raw_command.startswith("/aios "):
            return None
        
        # Xóa tiền tố /aios
        cmd_body = raw_command[6:].strip()
        
        # Regex để bắt lệnh 'run' và tên task
        match = re.match(r"^run\s+([\w_]+)(.*)", cmd_body)
        if not match:
            return None
            
        task_name = match.group(1)
        params_str = match.group(2).strip()
        
        # Parse thêm params nếu cần (đơn giản hóa ở đây)
        params = {}
        if params_str:
            params["raw_args"] = params_str

        return {
            "action": "run",
            "task": task_name,
            "params": params
        }
