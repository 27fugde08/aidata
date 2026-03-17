import asyncio
import signal
import sys
from core.logger import logger
from core.instance import orchestrator
from core.scheduler import AgentOSScheduler
from core.automation_scheduler import AutomationScheduler
from core.worker import AIOSWorker
import config

class AIOSSystemLifecycle:
    _instance = None
    
    def __new__(cls):
        if not cls._instance:
            cls._instance = super(AIOSSystemLifecycle, cls).__new__(cls)
            cls._instance.is_running = False
            cls._instance.os_scheduler = AgentOSScheduler()
            cls._instance.automation_scheduler = AutomationScheduler(config.WORKSPACE_ROOT)
            cls._instance.aios_worker = AIOSWorker()
        return cls._instance

    async def startup(self):
        """Khởi động toàn bộ hệ sinh thái AIOS."""
        if self.is_running:
            return
            
        logger.info("🚀 [Lifecycle] Starting AIOS Kernel Ecosystem...")
        
        try:
            # 1. Khởi động AIOS Orchestrator
            logger.info("Initializing Orchestrator...")
            await orchestrator.start()
            
            # 2. Khởi động các Background Workers
            logger.info("Starting Background Workers...")
            asyncio.create_task(self.os_scheduler.run_worker())
            asyncio.create_task(self.aios_worker.start())
            
            # 3. Khởi động Scheduler
            logger.info("Starting Automation Scheduler...")
            self.automation_scheduler.scheduler.start()
            
            self.is_running = True
            logger.info("✅ [Lifecycle] AIOS is fully operational!")
            
        except Exception as e:
            logger.critical(f"❌ [Lifecycle] Startup Failed: {e}", exc_info=True)
            sys.exit(1)

    async def shutdown(self):
        """Dừng hệ thống một cách an toàn (Graceful Shutdown)."""
        logger.warning("🛑 [Lifecycle] Initiating Shutdown Sequence...")
        
        try:
            # Dừng các Worker trước
            self.aios_worker.stop()
            
            # Dừng Scheduler
            self.automation_scheduler.scheduler.shutdown()
            
            # Lưu trạng thái cuối cùng (nếu cần)
            # await save_state()
            
            self.is_running = False
            logger.info("👋 [Lifecycle] AIOS Shutdown Complete. Goodbye!")
            
        except Exception as e:
            logger.error(f"⚠️ [Lifecycle] Error during shutdown: {e}")

# Global Access Point
lifecycle = AIOSSystemLifecycle()
