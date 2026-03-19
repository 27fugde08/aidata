# AIOS Enterprise v2.2.0 (Day 2 Update)

## 🧠 AIOS: Autonomous Operating System for AI Agents
**AIOS** is a modular, kernel-based operating system designed to orchestrate independent AI apps (microservices) into a unified automation ecosystem.

---

## 🚀 Key Features (v2.2.0)
- **Modular Monorepo:** Separate `core` and `apps` architecture.
- **Micro-Kernel Architecture:** Apps run as independent Docker containers, controlled by the AIOS Kernel.
- **Dynamic App Discovery:** The Kernel automatically discovers and integrates available apps.
- **Task Queue & Orchestration:** Centralized command center for managing complex, multi-step missions.
- **Independent Control:** Run AIOS as a standalone orchestrator that controls all satellite projects.

---

## 🛠️ Architecture Overview

The system is composed of the following independent services:

1.  **AIOS Kernel (`aios-kernel`):** The central brain, API gateway, and orchestrator.
2.  **AIOS Worker Swarm (`aios-worker`):** Scalable Celery workers for heavy tasks.
3.  **Redis (`aios-redis`):** Message broker for inter-service communication.
4.  **YouTube Shorts (`aios-app-youtube`):** Independent service for YouTube Shorts automation.
5.  **YouTube Enterprise (`aios-app-youtube-ent`):** Enterprise-grade video engine.

---

## 📦 Installation & Usage (Docker)

The recommended way to run AIOS Enterprise is via Docker Compose. This ensures all apps run in isolated environments with their specific dependencies.

### Prerequisites
- Docker & Docker Compose
- Python 3.10+ (for local development)

### 1. Build and Run All Services
```bash
docker-compose up --build -d
```

This will start:
- **Kernel API:** http://localhost:8000
- **YouTube Service:** http://localhost:8002
- **Enterprise Service:** http://localhost:8003

### 2. Check System Health
You can check the status of the entire ecosystem via the Kernel:
```bash
curl http://localhost:8000/api/v1/system/health
```

### 3. Independent Control Mode
To demonstrate AIOS controlling other apps programmatically, run the provided script:
```bash
python scripts/aios_independent_control.py
```
This script connects to the Kernel and instructs it to orchestrate tasks across the available apps.

---

## 🔧 Local Development (Without Docker)

If you prefer to run components manually:

1.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Start the Kernel:**
    ```bash
    python manage.py runserver
    ```

3.  **Run an App Independently:**
    ```bash
    cd apps/youtube
    uvicorn main:app --port 8002
    ```

---

## 📂 Directory Structure

```
.
├── apps/                   # Modular Applications (Microservices)
│   ├── youtube/            # YouTube Shorts App
│   ├── youtube_ent/        # Enterprise Video Engine
│   └── ...
├── core/                   # AIOS Central Kernel
│   ├── api/                # Kernel API Endpoints
│   ├── shared/             # Shared Configuration & Utilities
│   └── ...
├── storage/                # Centralized Persistent Data
│   ├── db/                 # Databases
│   ├── logs/               # System Logs
│   └── outputs/            # Generated Media
├── docker/                 # Deployment Configurations
└── manage.py               # Unified Entry Point CLI
```

---

## 🛡️ License
AIOS Enterprise is proprietary software. All rights reserved.
