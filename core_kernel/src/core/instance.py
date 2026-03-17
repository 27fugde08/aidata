import os
import sys

# Ensure root path is known
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from .orchestrator import MultiAgentOrchestrator

# Unified Global Orchestrator Singleton
orchestrator = MultiAgentOrchestrator(workspace_root=config.WORKSPACE_ROOT)
