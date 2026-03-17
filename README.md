# AIOS - AI Operating System Kernel (Enterprise Edition 2025)

AIOS is a modular, high-performance monorepo designed for orchestrating autonomous AI agents, managing distributed workflows, and automating multi-platform content creation (Douyin, TikTok, YouTube).

---

## 🚀 Quick Start

### 1. Prerequisites
- **Python**: 3.10+
- **Docker & Docker Compose**: (Recommended for isolated execution)
- **API Keys**: Google Gemini (Required), OpenAI/Anthropic (Optional)

### 2. Setup Environment
```bash
# Install dependencies locally
pip install -r requirements.txt

# Configure Environment Variables
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

### 3. Run the Application

#### Option A: Docker Execution (Production Ready)
This starts the Kernel, Redis broker, and a scalable Worker Swarm.
```bash
# Build and Start everything
docker-compose up --build -d

# Scale workers if needed
docker-compose up -d --scale aios-worker=3

# View Logs
docker logs -f aios-kernel
```

#### Option B: Local Execution (Development)
```bash
# Start the unified manager
python manage.py runserver

# Run the test suite
python manage.py test
```

---

## 🏛️ System Architecture

AIOS is built on a **Micro-Kernel** philosophy, ensuring the core remains stable while external apps operate as isolated plugins.

### 1. AI Core Engine
- **Engine**: Google Gemini 2.0 Flash (Latest 2025 version).
- **Orchestration**: Integrated **LangGraph** for stateful, complex multi-agent reasoning.
- **Memory**: Dual-layer system with short-term context and long-term **Vector Memory (ChromaDB)**.

### 2. Distributed Infrastructure
- **Task Queue**: Powered by **Redis** and **Celery** for asynchronous, non-blocking execution.
- **Auto-Scaling**: Horizontal scaling of Worker nodes via Docker to handle high-volume video rendering or AI research.
- **Real-time Comms**: **Server-Sent Events (SSE)** for live log streaming and "Thought Traces" to the frontend.

### 3. AI Web IDE & Skills
- **Integrated IDE**: Monaco-based editor with syntax highlighting and terminal access.
- **Dynamic Skills**: Python-based skills loaded at runtime from the `storage/skills` directory.

---

## 📂 Project Structure

```text
root/
├── core_kernel/          # The Heart of AIOS
│   └── src/
│       ├── api/          # REST Endpoints (Projects, Queue, System)
│       ├── core/         # Logic (AgentEngine, LangGraph Orchestrator)
│       └── shared/       # Configuration & Real-time Logger
├── apps/                 # Modular Applications (Isolated Plugins)
│   ├── douyin_automation/
│   └── youtube_shorts/
├── frontend/             # Control Tower Dashboard (Vanilla JS Reactive SPA)
├── storage/              # Persistent Data (SQLite, JSON State, Outputs)
├── manage.py             # Unified CLI Management Script
└── docker-compose.yml    # Enterprise Orchestration
```

---

## 🛠 Features

- **Dynamic App Discovery**: Apps in `apps/` are automatically detected and mounted without modifying the core.
- **Isolated Execution**: Crashes in external apps do not affect the stability of the AIOS Kernel.
- **Bento Grid Dashboard**: High-density UI for monitoring system health (CPU/RAM), logs, and agent reasoning.
- **Persistent State**: System state is saved to `kernel_state.json`, ensuring data survives restarts.

---

## 📚 Contributing

1. **Modular Apps**: Add new features as folders in `apps/` with an `api/` subfolder containing a `router` object.
2. **Testing**: Always run `python manage.py test` before pushing changes.
3. **Environment**: Keep `.env` strictly local; use `.env.example` for documentation.

---

## 📝 License
Proprietary / Internal Use for AIOS Project.
