# 🤖 AIOS Enterprise v3.0 (Refactored & Optimized)

**AIOS Enterprise** is a high-performance, modular AI Automation Operating System designed to orchestrate AI agents, manage complex background tasks, and provide a seamless real-time user experience.

---

## 🚀 Key Features

- **Modular Backend:** Clean architecture with separation of concerns: `api`, `core`, `db`, `models`, `repositories`, `schemas`, and `services`.
- **Modern Frontend:** Built with **Next.js 14**, **Tailwind CSS**, and **React Query** for real-time task status polling and a polished UI.
- **Background Processing:** **Celery + Redis** integration for handling heavy tasks like media analysis and automated workflows.
- **Robust Database:** **PostgreSQL** with **Alembic** for version-controlled schema migrations.
- **AI Integration:** Powered by **Google Gemini AI** with dynamic function calling to interact with system services.
- **Dockerized Environment:** One-command deployment for the entire stack (Database, Redis, Backend, Worker, Frontend).

---

## 🛠️ Technology Stack

| Component | Technology |
| :--- | :--- |
| **Backend** | Python, FastAPI, SQLAlchemy 2.0, Pydantic v2 |
| **Frontend** | TypeScript, Next.js, Tailwind CSS, Lucide Icons |
| **Database** | PostgreSQL 15, Alembic |
| **Task Queue** | Celery, Redis |
| **AI Engine** | Google Gemini (Generative AI) |
| **DevOps** | Docker, Docker Compose |

---

## 📂 Project Structure

```text
.
├── backend/                # FastAPI Application
│   ├── app/                # Main Application Logic
│   │   ├── api/            # API Endpoints (v1)
│   │   ├── core/           # Configuration & Celery Setup
│   │   ├── db/             # Database Session Management
│   │   ├── models/         # SQLAlchemy Models
│   │   ├── repositories/   # Data Access Layer
│   │   ├── schemas/        # Pydantic Schemas
│   │   ├── services/       # Business Logic & AI Agents
│   │   └── tasks/          # Celery Task Handlers
│   ├── alembic/            # Database Migrations
│   └── main.py             # Entry Point
├── frontend/               # Next.js Application
│   ├── src/                # Source Code
│   │   ├── app/            # Next.js App Router (Pages & Layout)
│   │   ├── components/     # UI Components (Shadcn/UI based)
│   │   ├── lib/            # API Client & Utils
│   │   └── types/          # TypeScript Interfaces
│   └── tailwind.config.ts  # Theme Configuration
├── docker-compose.yml      # Orchestration Config
└── start.sh                # Deployment Script (Bash)
```

---

## ⚡ Quick Start

### 1. Prerequisites
- **Docker & Docker Compose** installed.
- **Gemini API Key** from [Google AI Studio](https://aistudio.google.com/).

### 2. Environment Setup
Create a `.env` file in the root directory:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. Build and Run
Run the automated start script (Linux/macOS):
```bash
chmod +x start.sh
./start.sh
```

**Or run manually (Windows/All):**
```powershell
# 1. Start containers
docker-compose up -d --build

# 2. Run database migrations
docker-compose exec backend alembic upgrade head
```

### 4. Access the Apps
- **Frontend UI:** [http://localhost:3000](http://localhost:3000)
- **Backend API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🇻🇳 Hướng Dẫn Sử Dụng (Vietnamese)

### Cài đặt nhanh
1. Sao chép khóa API Gemini vào file `.env`.
2. Chạy lệnh `docker-compose up -d --build`.
3. Chạy lệnh migrate database: `docker-compose exec backend alembic upgrade head`.

### Chức năng chính
- **Chat với AI:** Gửi yêu cầu bằng ngôn ngữ tự nhiên (ví dụ: "Phân tích video này: [URL]").
- **Theo dõi Task:** Danh sách task bên phải sẽ tự động cập nhật trạng thái (Pending -> Processing -> Completed).
- **Xem kết quả:** Click vào task để xem dữ liệu chi tiết (Metadata video, kết quả phân tích).

---

## 🛡️ License & Credits
AIOS Enterprise is maintained by the AIOS Development Team. All rights reserved.
