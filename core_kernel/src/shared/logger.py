import logging
import sys
import os
import asyncio
from logging.handlers import RotatingFileHandler

# Tạo thư mục logs nếu chưa có
LOG_DIR = os.path.dirname(os.path.abspath(__file__)) # Sửa lại để trỏ đúng thư mục logs của kernel
os.makedirs(os.path.join(LOG_DIR, "..", "logs"), exist_ok=True)

class SSELogHandler(logging.Handler):
    """Gửi log trực tiếp vào SSE stream của StateManager."""
    def emit(self, record):
        try:
            from core.state_manager import state_manager
            msg = self.format(record)
            # Chạy async task để không block logger chính
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(state_manager.add_event("log", {"message": msg, "level": record.levelname}))
            except RuntimeError:
                pass # No running event loop
        except ImportError:
            pass

class AIOSLogger:
    @staticmethod
    def get_logger(name: str):
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            # 1. Console Handler
            console_handler = logging.StreamHandler(sys.stdout)
            console_formatter = logging.Formatter('%(asctime)s | %(levelname)-5s | %(message)s', datefmt='%H:%M:%S')
            console_handler.setFormatter(console_formatter)
            logger.addHandler(console_handler)

            # 2. SSE Stream Handler (2025 Integration)
            sse_handler = SSELogHandler()
            sse_handler.setFormatter(logging.Formatter('%(message)s'))
            logger.addHandler(sse_handler)

        return logger

# Global instance
logger = AIOSLogger.get_logger("AIOS_KERNEL")
