# AIOS Optimized Architecture

## Overview
The AIOS system has been audited and optimized for stability, reliability, and security. It operates as a multi-agent orchestration platform with a FastAPI kernel and a web-based Control Tower.

## Core Components

### 1. Kernel (`backend/main.py`)
- **Role:** Central API gateway and service orchestrator.
- **Key Services:**
  - `AgentOSScheduler`: Manages background processes.
  - `MultiAgentOrchestrator`: Coordinates complex multi-agent workflows.
  - `EventEngine`: Handles system-wide events and logging.
  - `MemoryManager`: Manages short-term and vector-based long-term memory.

### 2. Agent Layer (`backend/core/agent_engine.py`)
- **Engine:** Google Gemini 2.0 Flash.
- **Reliability:** 
  - **Retries:** Built-in retry mechanism for LLM calls to handle transient network errors.
  - **Sandboxing:** Code execution is sandboxed (Docker optional).
  - **Context:** Smart context retrieval using Vector Memory.

### 3. Orchestration & Workflows (`backend/core/orchestrator.py`)
- **Workflow Engine:** Executes structured tasks defined in JSON.
- **Checkpointing:** State is saved after each step to `.workflow_state.json` to allow recovery.
- **Roles:** specialized agents (Architect, Developer, Tester, etc.) are dynamically instantiated.

### 4. Event & Monitoring (`backend/core/event_engine.py`)
- **Event Bus:** Pub/sub system for inter-component communication.
- **Logging:** All system events are persisted to `logs/system.log`.
- **Metrics:** Real-time CPU/RAM and Token usage tracking.

### 5. Frontend ("Control Tower")
- **Technology:** Vanilla JS + HTML5 (optimized for low overhead).
- **Communication:** REST API + Server-Sent Events (SSE) for streaming agent outputs.
- **Dashboard:** Unified view for Chat, Agent Status, System Resources, and Deployment History.

## Security Improvements
- **API Keys:** Hardcoded keys removed. Now uses `os.environ["GEMINI_API_KEY"]`.
- **Sandboxing:** Local execution fallback is explicit; Docker is recommended for production.

## Directory Structure
```
root/
├── backend/
│   ├── main.py            # Unified Entry Point
│   ├── config.py          # Secure Configuration
│   └── core/
│       ├── agent_engine.py      # AI Logic + Retries
│       ├── orchestrator.py      # Workflow Management + Checkpoints
│       └── event_engine.py      # Logging System
├── frontend/
│   ├── index.html         # Control Tower UI
│   └── script.js          # API Client
└── logs/
    └── system.log         # Persistent Event Log
```
