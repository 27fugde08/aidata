# AIOS SaaS Architecture: Plugin-First Ecosystem

## 1. Vision & Philosophy
Chuyển đổi AIOS thành **"The WordPress/VS Code for AI Agents"**.
- **Kernel (OS):** Quản lý vòng đời, bảo mật, bộ nhớ, thanh toán và xác thực.
- **Plugins (Apps):** Các module chức năng có thể cài đặt/gỡ bỏ (Ví dụ: *Video Engine, GitHub Connector, SEO Writer*).
- **SaaS Standard:** Multi-tenancy (đa người dùng), Metering (đo đếm token/usage), Security Sandbox.

## 2. High-Level Architecture

```mermaid
graph TD
    User((User)) -->|HTTPS| LoadBalancer[Load Balancer]
    LoadBalancer --> Gateway[API Gateway / Auth Layer]
    
    subgraph "AIOS Kernel (The Core)"
        Gateway --> Orchestrator[Mission Orchestrator]
        Orchestrator --> EventBus[Event Bus (Redis)]
        Orchestrator --> Memory[Global Brain / Vector DB]
        
        subgraph "Plugin Engine (Sandbox)"
            PM[Plugin Manager] -->|Load| P1[Plugin: Video Gen]
            PM -->|Load| P2[Plugin: Coder]
            PM -->|Load| P3[Plugin: Social Bot]
        end
    end
    
    subgraph "Data Layer"
        DB[(PostgreSQL - Users/Billing)]
        VDB[(ChromaDB - Knowledge)]
        Files[S3 / MinIO - Assets]
    end

    EventBus <--> PM
```

## 3. The Plugin Standard (Manifest V1)
Mọi plugin đều phải tuân theo cấu trúc `manifest.json` chuẩn để Kernel có thể hiểu và tải lên.

### Structure
```json
{
  "id": "com.aios.video-engine",
  "version": "1.0.0",
  "name": "Viral Video Creator",
  "description": "Auto-generate TikTok/Shorts from URLs",
  "author": "SpaceOfDuy",
  "pricing": "pro_tier",
  "permissions": [
    "filesystem.read",
    "filesystem.write",
    "network.download"
  ],
  "entry_point": "main.py",
  "class": "VideoPlugin"
}
```

## 4. Core Modules Re-design

### A. The Kernel (Backend)
Giữ lại FastAPI nhưng tái cấu trúc thành các module lõi:
- **`core.auth`**: Quản lý JWT, API Keys, Team Management.
- **`core.billing`**: Tích hợp Stripe, đếm số lượng Token/GPU usage của từng Plugin.
- **`core.plugin_loader`**: Quét thư mục `plugins/`, validate manifest, và hot-load Python classes.

### B. The Sandbox (Security)
Để đảm bảo an toàn cho SaaS:
- Các Plugin không được gọi trực tiếp `os.system`.
- Kernel cung cấp **SDK** (`aios_sdk`) để Plugin giao tiếp với bên ngoài.
- **Isolation:** Mỗi phiên chạy nặng (như render video) nên chạy trong một Docker Container tạm thời (Ephemeral Container).

### C. The Marketplace (Registry)
Một API riêng để liệt kê các Plugin có sẵn.
- User click "Install" -> Kernel tải zip plugin về -> Giải nén vào `workspace/plugins/` -> Register vào DB.

## 5. Directory Structure (Proposed)

```text
/
├── core/                   # Kernel Logic (Never changes by plugins)
│   ├── api/                # System APIs (Auth, Billing, Plugin Mgmt)
│   ├── engine/             # LLM Inference Engine
│   └── sdk/                # AIOS SDK for Plugin Developers
├── plugins/                # Installed Plugins (Gitignored)
│   ├── official_video/     # Example Plugin
│   │   ├── manifest.json
│   │   ├── main.py
│   │   └── router.py
│   └── community_seo/
├── data/                   # Tenant Data (Isolated by Tenant ID)
│   ├── tenant_A/
│   └── tenant_B/
└── marketplace/            # Registry Service (Separate Repo/Service)
```

## 6. Implementation Roadmap

1.  **Phase 1: SDK Definition** - ✅ Done: AIOSPlugin base class created.
2.  **Phase 2: Plugin Loader** - ✅ Done: PluginManager with dynamic loading & SDK injection.
3.  **Phase 3: Migration** - ✅ Done: VideoEngine ported to `plugins/video_generator`. Orchestrator worker handles task queue.
4.  **Phase 4: Marketplace UI** - ⏳ In Progress: Backend API ready, Frontend UI needs full integration.
