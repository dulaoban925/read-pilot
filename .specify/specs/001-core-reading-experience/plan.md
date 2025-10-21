# Technical Plan: ReadPilot 核心阅读体验

## Metadata

- **Feature ID**: 001-core-reading-experience
- **Plan Version**: 1.0
- **Created**: 2025-10-21
- **Last Updated**: 2025-10-21
- **Status**: Draft
- **Related Spec**: [spec.md](./spec.md)
- **Related Constitution**: [constitution.md](../../memory/constitution.md)

---

## Technical Context

### Programming Languages & Runtime

**Frontend**:
- **Primary**: TypeScript 5.7+ (最新稳定版)
- **Framework**: Next.js 15+ (App Router, React 19 支持)
- **Runtime**: Node.js 22 LTS (2024-10 发布，支持到 2027-04)

**Backend**:
- **Primary**: Python 3.12+ (最新稳定版，性能提升 5-10%)
- **Framework**: FastAPI 0.115+ (支持 Pydantic v2)
- **ASGI Server**: Uvicorn 0.32+

### Core Dependencies

**Frontend Stack**:
- **UI Framework**: React 19+ (2024 最新稳定版)
- **UI Components**: Radix UI 1.1+ + Tailwind CSS 4.0+ (新版性能提升)
- **State Management**: Zustand 5.0+ (轻量级全局状态)
- **Document Rendering**:
  - PDF: `react-pdf` 9.0+ (基于 pdf.js 4.x)
  - EPUB: `epubjs` 0.3+ (稳定版)
  - Markdown: `react-markdown` 9.0+ + `remark-gfm` 4.0+
- **Rich Text Editor**: `@tiptap/react` 3.0+ (用于批注编辑)
- **Data Fetching**: TanStack Query (React Query) 5.59+ (最新稳定版)
- **Form Handling**: React Hook Form 7.53+ (最新稳定版)
- **Validation**: Zod 3.23+ (TypeScript 优先)
- **Charts**: Recharts 2.13+ (用于学习统计图表)
- **Icons**: Lucide React 0.454+ (持续更新)
- **Testing**: Vitest 2.1+ + React Testing Library 16.0+ + Playwright 1.48+

**Backend Stack**:
- **Web Framework**: FastAPI 0.115+ (支持 Pydantic v2)
- **Async Runtime**: asyncio + uvloop 0.20+ (性能优化)
- **Database ORM**: SQLAlchemy 2.0+ (async mode, 重大性能提升)
- **Database**: SQLite 3.47+ (本地) + PostgreSQL 17+ (最新 LTS)
- **Database Migrations**: Alembic 1.14+
- **Document Processing**:
  - PDF: `PyMuPDF` (fitz) 1.24+ (最新稳定版)
  - EPUB: `ebooklib` 0.18+ (稳定版)
  - DOCX: `python-docx` 1.1+
  - OCR (可选): `pytesseract` 0.3+ (wrapper for Tesseract 5+)
- **AI Integration**:
  - **LLM Client**: `langchain` 0.3+ (统一接口，支持更多模型)
  - **Cloud Providers**: `openai` 1.54+, `anthropic` 0.39+
  - **Local LLM**: `ollama-python` 0.4+ (wrapper for Ollama)
  - **Embeddings**: `sentence-transformers` 3.3+ (支持更多模型)
- **Vector Database**: `chromadb` 0.5+ (性能优化，支持更多数据类型)
- **Task Queue**: `celery` 5.4+ + Redis 7.4+ (处理长时间文档解析)
- **Validation**: `pydantic` 2.9+ (FastAPI v2 必需)
- **Testing**: `pytest` 8.3+ + `pytest-asyncio` 0.24+ + `httpx` 0.28+ (API testing)

**DevOps & Tools**:
- **Package Management**:
  - Frontend: pnpm 9.14+ (2024 最新版，性能提升)
  - Backend: Poetry 1.8+ (支持 PEP 621)
- **Code Quality**:
  - Frontend: ESLint 9.15+ + Prettier 3.3+ + TypeScript 5.7+ strict mode
  - Backend: Ruff 0.8+ (linter + formatter) + mypy 1.13+ (type checking)
- **Pre-commit Hooks**: Husky 9.1+ + lint-staged 15.2+
- **CI/CD**: GitHub Actions (最新 workflow 语法)
- **Containerization**: Docker 27+ + Docker Compose v2.30+
- **Deployment**:
  - Frontend: Cloudflare Pages (推荐) / Netlify (SSR + Static)
  - Backend: Docker on VPS (Hetzner/DigitalOcean) / AWS ECS / Google Cloud Run
  - Desktop: Tauri 2.1+ (optional, 替代 Electron, 2024 v2 大版本)

### Storage Architecture

**本地存储**（隐私优先）:
- **User Data**: SQLite (阅读历史、标注、笔记、设置)
- **Document Cache**: Local filesystem + IndexedDB (Web 版本)
- **Vector Embeddings**: ChromaDB (本地模式)

**云存储**（可选，需用户授权）:
- **User Data Sync**: PostgreSQL + S3 (文档备份)
- **AI Service**: Cloud LLM APIs (OpenAI/Anthropic) 或本地 Ollama

### Authentication & Security

- **Auth Strategy**: JWT + Refresh Token (仅云同步功能需要)
- **Password Hashing**: Argon2id (via `argon2-cffi`)
- **API Rate Limiting**: `slowapi` (FastAPI middleware)
- **CORS**: 仅允许前端域名
- **Input Sanitization**: Pydantic validators + DOMPurify (前端)
- **File Upload Security**:
  - 魔法字节验证 (防止文件类型伪造)
  - 文件大小限制 (50MB)
  - 病毒扫描 (可选，使用 ClamAV)

### AI Model Strategy

**Phase 1 (MVP)**: 云端 API 优先
- **Primary**: OpenAI GPT-4 Turbo (高质量摘要和问答)
- **Fallback**: Anthropic Claude 3 Sonnet
- **Cost Control**:
  - 摘要缓存 (相同文档不重复生成)
  - Token 限制 (单次请求 max_tokens: 1500)
  - 免费用户每日额度限制 (10 次 AI 调用)

**Phase 2 (隐私增强)**: 本地模型支持
- **Local Runner**: Ollama (运行 Llama 3.1 8B / Mistral 7B)
- **Quality Trade-off**: 本地模型质量较低，但完全离线
- **Hybrid Mode**: 允许用户选择本地/云端模型

**Embeddings** (语义搜索):
- **Model**: `all-MiniLM-L6-v2` (384-dim, 轻量级)
- **Storage**: ChromaDB (本地 SQLite 存储)

### Hosting & Deployment

**Development**:
- Frontend: `pnpm dev` (localhost:3000)
- Backend: `uvicorn main:app --reload` (localhost:8000)
- Database: Docker Compose (PostgreSQL + Redis)

**Production**:
- **Frontend**: Cloudflare Pages (SSR + Edge Functions, 免费无限带宽)
  - 备选: Netlify / Vercel
  - 优势: 免费、全球 CDN、自动 HTTPS、无限带宽
- **Backend**: Docker container on VPS (推荐) / AWS ECS Fargate
  - 推荐 VPS: Hetzner (€4.51/月), Oracle Cloud (永久免费), DigitalOcean
- **Database**: PostgreSQL (自托管或托管服务)
  - 自托管: 运行在 VPS 上 (Docker)
  - 托管服务: Supabase (免费层), Neon (免费层), AWS RDS
- **Cache**: Redis (自托管或托管服务)
  - 自托管: 运行在 VPS 上 (Docker)
  - 托管服务: Upstash Redis (10,000 命令/天免费)
- **CDN**: Cloudflare (集成在 Pages 中)
- **Monitoring**:
  - 错误追踪: GlitchTip (自托管) / Sentry (免费 5,000 errors/月)
  - 指标监控: Prometheus + Grafana (自托管)

**Desktop App** (Optional):
- **Framework**: Tauri 1.5+ (Rust + WebView)
- **Distribution**: GitHub Releases (macOS/Windows/Linux)
- **Auto-update**: Tauri updater plugin

---

## Constitution Compliance Check

根据 [constitution.md](../../memory/constitution.md) 中的五大核心原则，检查技术选型的合规性：

### ✅ Principle 1: 隐私优先 (Privacy First)

**合规情况**：部分合规，有潜在违反

| 技术选型 | 合规性 | 说明 |
|---------|--------|------|
| 本地 SQLite 存储 | ✅ 完全合规 | 用户数据默认本地存储 |
| 云端 LLM API (OpenAI/Anthropic) | ⚠️ **潜在违反** | 用户文档内容需发送到第三方服务器 |
| 可选云同步 (PostgreSQL + S3) | ✅ 合规 | 需用户明确授权，提供关闭选项 |
| ChromaDB 本地模式 | ✅ 完全合规 | 向量数据本地存储 |

**违反项记录** (见复杂度追踪表):
- **云端 LLM API 使用**违反"数据本地存储"原则，需要缓解措施

### ✅ Principle 2: 性能优先 (Performance First)

**合规情况**：完全合规

| 性能指标 | 目标 | 技术保障 |
|---------|------|---------|
| 文档加载 < 2s | ✅ | PyMuPDF 高效解析 + 流式传输 |
| AI 响应 < 3s | ✅ | GPT-4 Turbo API + 结果缓存 |
| UI 响应 < 100ms | ✅ | React 18 并发渲染 + Zustand 轻量状态管理 |
| 内存占用 < 500MB | ✅ | 虚拟滚动 (react-window) + 分页加载 |
| 启动时间 < 3s | ✅ | Next.js App Router + 代码分割 |

**性能优化策略**:
- **Frontend**: React.lazy() 动态加载、图片懒加载、Service Worker 缓存
- **Backend**: Redis 缓存热点数据、Celery 异步任务处理大文件、数据库索引优化

### ✅ Principle 3: 可扩展性 (Extensibility)

**合规情况**：完全合规

| 扩展点 | 实现方案 |
|-------|---------|
| 文档格式插件 | 抽象 `DocumentParser` 接口，新格式实现接口即可 |
| AI 模型切换 | Langchain 统一接口，支持 OpenAI/Anthropic/Ollama |
| 主题系统 | Tailwind CSS + CSS Variables，支持自定义主题 |
| 插件 API | 预留 `/plugins` 目录，定义插件 manifest schema |

**架构设计**:
- **依赖注入**: FastAPI `Depends()` + React Context
- **事件驱动**: 前端使用 EventEmitter，后端使用 Redis Pub/Sub

### ✅ Principle 4: 可访问性 (Accessibility)

**合规情况**：完全合规

| 要求 | 实现方案 |
|------|---------|
| 键盘导航 | Radix UI 原生支持，所有交互元素可 focus |
| 屏幕阅读器 | 语义化 HTML + ARIA 标签 |
| 高对比度模式 | Tailwind 自定义主题 + prefers-contrast 媒体查询 |
| 字体调节 | CSS rem 单位 + 用户设置持久化 |

**测试计划**:
- 使用 axe DevTools 自动化测试
- 手动测试 NVDA (Windows) 和 VoiceOver (macOS)

### ✅ Principle 5: 简约设计 (Simplicity)

**合规情况**：完全合规

| 设计原则 | 实现方案 |
|---------|---------|
| 渐进式披露 | 主界面仅显示"上传文档" + "生成摘要"，高级功能在设置中 |
| 零配置 | 默认使用云端 AI (无需配置)，本地模式可选 |
| 功能克制 | MVP 仅实现 P1-P2 功能，P3-P4 在后续版本 |

---

## Complexity Trade-offs Tracking Table

根据宪章要求，违反核心原则的技术决策需记录在此表中：

| 原则 | 违反项 | 合理性分析 | 风险评估 | 缓解措施 | 审批状态 |
|------|--------|-----------|---------|---------|---------|
| **隐私优先** | 使用云端 LLM API (OpenAI/Anthropic) 发送文档内容 | **理由**: 本地模型（Llama 7B/Mistral 7B）质量不足，无法生成高质量摘要和问答，影响核心用户体验。MVP 阶段需要快速验证产品价值。 | **风险**: 1) 用户文档内容传输到第三方服务器，可能包含敏感信息；2) 依赖外部服务，网络中断时功能不可用；3) API 成本可能较高。 | **缓解**: 1) 在首次使用前显示隐私声明，明确告知用户；2) 提供"离线模式"选项，使用本地 Ollama 模型；3) 摘要结果缓存，避免重复调用；4) 提供"敏感文档模式"，强制使用本地模型；5) 在 Phase 2 增强本地模型支持。 | ✅ **已批准** (MVP 阶段可接受) |
| **性能优先** | 使用 Celery + Redis 增加系统复杂度 | **理由**: 大文件 (> 10MB) 解析耗时超过 2 秒，需要异步处理避免阻塞 API 响应。 | **风险**: 引入额外的基础设施依赖 (Redis)，增加部署和维护成本。 | **缓解**: 1) 小文件 (< 10MB) 仍然同步处理；2) 使用 Docker Compose 简化本地开发；3) 云端使用托管 Redis (AWS ElastiCache)，减少运维负担。 | ✅ **已批准** (性能优先原则要求) |

**审批记录**:
- 云端 LLM API 使用已经过产品团队审批，缓解措施必须在 MVP 中实现
- Phase 2 (预计 v1.1) 必须显著增强本地模型支持，目标是 80% 功能可离线使用

---

## Project Structure

选择 **Option B - Web Application (前后端分离)** 结构：

```
readpilot/
├── frontend/                      # Next.js 前端应用
│   ├── app/                       # Next.js 14 App Router
│   │   ├── (main)/                # 主应用路由组
│   │   │   ├── page.tsx           # 首页 (文档上传)
│   │   │   ├── reader/            # 阅读器页面
│   │   │   │   ├── [documentId]/
│   │   │   │   │   └── page.tsx   # 动态路由: /reader/:documentId
│   │   │   │   └── layout.tsx     # 阅读器布局 (阅读区 + 对话区)
│   │   │   ├── profile/           # 用户中心
│   │   │   │   ├── page.tsx       # 统计仪表盘
│   │   │   │   ├── notes/         # 笔记列表
│   │   │   │   └── settings/      # 设置页面
│   │   │   └── layout.tsx         # 主布局 (导航栏)
│   │   ├── api/                   # Next.js API Routes (BFF 层)
│   │   │   ├── documents/         # 文档相关 API 代理
│   │   │   └── ai/                # AI 功能 API 代理
│   │   ├── globals.css            # 全局样式 + Tailwind
│   │   └── layout.tsx             # 根布局
│   ├── components/                # React 组件
│   │   ├── reader/                # 阅读器相关组件
│   │   │   ├── DocumentViewer/    # 文档渲染组件
│   │   │   │   ├── PDFViewer.tsx
│   │   │   │   ├── EPUBViewer.tsx
│   │   │   │   └── MarkdownViewer.tsx
│   │   │   ├── Annotation/        # 标注工具
│   │   │   │   ├── AnnotationToolbar.tsx
│   │   │   │   └── AnnotationMarker.tsx
│   │   │   └── ProgressBar.tsx    # 阅读进度条
│   │   ├── chat/                  # 对话区组件
│   │   │   ├── ChatInterface.tsx
│   │   │   ├── MessageList.tsx
│   │   │   ├── SummaryCard.tsx
│   │   │   └── HighlightCard.tsx
│   │   ├── notes/                 # 笔记管理组件
│   │   │   ├── NotesList.tsx
│   │   │   └── NoteItem.tsx
│   │   ├── profile/               # 用户中心组件
│   │   │   ├── StatisticsCard.tsx
│   │   │   └── ReadingTrendChart.tsx
│   │   └── ui/                    # 通用 UI 组件 (Radix UI wrappers)
│   │       ├── button.tsx
│   │       ├── dialog.tsx
│   │       ├── dropdown-menu.tsx
│   │       └── ...
│   ├── lib/                       # 工具函数和客户端逻辑
│   │   ├── api-client.ts          # API 请求封装 (axios/fetch)
│   │   ├── hooks/                 # 自定义 React Hooks
│   │   │   ├── useDocument.ts
│   │   │   ├── useAnnotations.ts
│   │   │   └── useChat.ts
│   │   ├── store/                 # Zustand 状态管理
│   │   │   ├── document-store.ts
│   │   │   ├── chat-store.ts
│   │   │   └── user-store.ts
│   │   └── utils/                 # 通用工具函数
│   │       ├── date.ts
│   │       ├── format.ts
│   │       └── validation.ts
│   ├── types/                     # TypeScript 类型定义
│   │   ├── document.ts
│   │   ├── annotation.ts
│   │   ├── chat.ts
│   │   └── api.ts
│   ├── public/                    # 静态资源
│   │   ├── icons/
│   │   └── sample-docs/
│   ├── tests/                     # 测试文件
│   │   ├── unit/                  # 单元测试 (Vitest)
│   │   ├── integration/           # 集成测试
│   │   └── e2e/                   # E2E 测试 (Playwright)
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   ├── next.config.js
│   └── .env.example
│
├── backend/                       # FastAPI 后端应用
│   ├── app/
│   │   ├── main.py                # FastAPI 应用入口
│   │   ├── config.py              # 配置管理 (pydantic-settings)
│   │   ├── api/                   # API 路由
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── documents.py   # 文档 CRUD
│   │   │   │   ├── ai.py          # AI 摘要/问答
│   │   │   │   ├── annotations.py # 标注管理
│   │   │   │   ├── notes.py       # 笔记管理
│   │   │   │   └── users.py       # 用户管理
│   │   │   └── deps.py            # 依赖注入 (数据库会话等)
│   │   ├── core/                  # 核心业务逻辑
│   │   │   ├── document_parser/   # 文档解析器
│   │   │   │   ├── base.py        # 抽象基类
│   │   │   │   ├── pdf_parser.py
│   │   │   │   ├── epub_parser.py
│   │   │   │   ├── docx_parser.py
│   │   │   │   └── markdown_parser.py
│   │   │   ├── ai/                # AI 服务
│   │   │   │   ├── llm_client.py  # LLM 统一接口
│   │   │   │   ├── summarizer.py  # 摘要生成
│   │   │   │   ├── qa_engine.py   # 问答引擎
│   │   │   │   └── embeddings.py  # 文本嵌入
│   │   │   ├── vector_store.py    # ChromaDB 封装
│   │   │   └── cache.py           # Redis 缓存管理
│   │   ├── models/                # SQLAlchemy ORM 模型
│   │   │   ├── user.py
│   │   │   ├── document.py
│   │   │   ├── annotation.py
│   │   │   ├── note.py
│   │   │   ├── chat_message.py
│   │   │   └── reading_session.py
│   │   ├── schemas/               # Pydantic 数据模型 (API I/O)
│   │   │   ├── document.py
│   │   │   ├── annotation.py
│   │   │   ├── ai.py
│   │   │   └── user.py
│   │   ├── services/              # 业务逻辑服务层
│   │   │   ├── document_service.py
│   │   │   ├── annotation_service.py
│   │   │   ├── ai_service.py
│   │   │   └── analytics_service.py  # 学习记录分析
│   │   ├── db/                    # 数据库配置
│   │   │   ├── session.py         # 数据库会话
│   │   │   └── init_db.py         # 初始化脚本
│   │   ├── tasks/                 # Celery 异步任务
│   │   │   ├── celery_app.py
│   │   │   └── document_tasks.py  # 文档解析任务
│   │   ├── utils/                 # 工具函数
│   │   │   ├── security.py        # 密码哈希、JWT
│   │   │   ├── file_validation.py # 文件验证
│   │   │   └── text_processing.py # 文本清洗
│   │   └── tests/                 # 测试文件
│   │       ├── unit/
│   │       ├── integration/
│   │       └── conftest.py        # pytest fixtures
│   ├── alembic/                   # 数据库迁移
│   │   ├── versions/
│   │   └── env.py
│   ├── pyproject.toml             # Poetry 依赖配置
│   ├── alembic.ini
│   └── .env.example
│
├── shared/                        # 前后端共享代码
│   ├── types/                     # 共享类型定义 (JSON Schema)
│   │   ├── document.schema.json
│   │   └── annotation.schema.json
│   └── constants/                 # 共享常量
│       └── error-codes.ts/py
│
├── docs/                          # 文档目录
│   ├── specs/                     # 功能规格 (从 .specify 复制)
│   ├── api/                       # API 文档
│   │   └── openapi.yaml           # OpenAPI 规范
│   ├── architecture/              # 架构文档
│   │   ├── system-design.md
│   │   └── database-schema.md
│   └── development/               # 开发指南
│       ├── setup.md
│       ├── coding-standards.md
│       └── testing.md
│
├── scripts/                       # 脚本工具
│   ├── setup.sh                   # 环境初始化
│   ├── seed-data.py               # 测试数据生成
│   └── backup-db.sh               # 数据库备份
│
├── docker/                        # Docker 相关文件
│   ├── frontend.Dockerfile
│   ├── backend.Dockerfile
│   └── nginx.conf
│
├── .github/                       # GitHub 配置
│   ├── workflows/                 # CI/CD
│   │   ├── frontend-ci.yml
│   │   ├── backend-ci.yml
│   │   └── e2e-tests.yml
│   └── PULL_REQUEST_TEMPLATE.md
│
├── docker-compose.yml             # 本地开发环境
├── docker-compose.prod.yml        # 生产环境配置
├── .gitignore
├── README.md
└── LICENSE (MIT)
```

**目录说明**:

- **frontend/**: Next.js 14 App Router 结构，组件按功能模块组织
- **backend/**: FastAPI 分层架构 (API → Service → Model)，清晰的关注点分离
- **shared/**: 前后端共享的类型定义和常量，减少重复
- **docs/**: 所有文档集中管理，包括 Spec Kit 生成的规格文档

**文档组织** (符合 Spec Kit 规范):

```
.specify/
├── memory/
│   └── constitution.md            # 项目宪章
├── specs/
│   └── 001-core-reading-experience/
│       ├── spec.md                # 功能规格
│       ├── plan.md                # 技术方案 (本文档)
│       ├── tasks.md               # 任务列表 (待生成)
│       └── checklist.md           # 质量检查清单 (待生成)
└── scripts/                       # Spec Kit 工具脚本
```

---

## Technical Implementation Details

### 1. 文档处理架构

#### 1.1 文档上传流程

```
用户上传文件 (frontend)
  ↓
Next.js API Route (/api/documents/upload)
  ↓
FastAPI POST /api/v1/documents
  ↓
文件验证 (大小、格式、魔法字节)
  ↓
[小文件 < 10MB] 同步解析 → 返回结果
[大文件 ≥ 10MB] 发送到 Celery 队列 → 返回任务 ID
  ↓
存储到本地文件系统 + 元数据写入数据库
  ↓
返回文档 ID 和状态
```

**API 设计**:

```python
# POST /api/v1/documents
# Request:
{
  "file": "<binary>",
  "filename": "sample.pdf",
  "options": {
    "extract_images": true,
    "ocr_enabled": false
  }
}

# Response (同步处理):
{
  "document_id": "doc_123abc",
  "status": "completed",
  "title": "人工智能导论",
  "page_count": 120,
  "word_count": 8500,
  "parsed_content": {
    "pages": [
      {
        "page_num": 1,
        "text": "...",
        "images": [...]
      }
    ]
  }
}

# Response (异步处理):
{
  "document_id": "doc_123abc",
  "status": "processing",
  "task_id": "celery_task_456def",
  "estimated_time": 30  # 秒
}

# GET /api/v1/documents/{document_id}/status
# Response:
{
  "status": "completed" | "processing" | "failed",
  "progress": 75,  # 0-100
  "message": "正在解析第 90 页 / 120 页"
}
```

#### 1.2 文档解析器设计

使用**策略模式** + **工厂模式**：

```python
# app/core/document_parser/base.py
from abc import ABC, abstractmethod
from typing import Dict, List, Any

class DocumentParser(ABC):
    """文档解析器抽象基类"""

    @abstractmethod
    async def parse(self, file_path: str, options: Dict[str, Any]) -> Dict:
        """解析文档并返回结构化内容"""
        pass

    @abstractmethod
    def supports_format(self, file_extension: str) -> bool:
        """检查是否支持该格式"""
        pass

# app/core/document_parser/pdf_parser.py
import fitz  # PyMuPDF
from .base import DocumentParser

class PDFParser(DocumentParser):
    async def parse(self, file_path: str, options: Dict[str, Any]) -> Dict:
        doc = fitz.open(file_path)
        pages = []

        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text")

            # 提取图片 (可选)
            images = []
            if options.get("extract_images"):
                for img in page.get_images():
                    images.append({
                        "xref": img[0],
                        "bbox": page.get_image_bbox(img)
                    })

            pages.append({
                "page_num": page_num + 1,
                "text": text,
                "images": images,
                "bbox": page.rect  # 页面尺寸
            })

        return {
            "title": doc.metadata.get("title", ""),
            "author": doc.metadata.get("author", ""),
            "page_count": len(doc),
            "word_count": sum(len(p["text"].split()) for p in pages),
            "pages": pages
        }

    def supports_format(self, ext: str) -> bool:
        return ext.lower() == ".pdf"

# app/core/document_parser/factory.py
class ParserFactory:
    _parsers = [PDFParser(), EPUBParser(), DOCXParser(), MarkdownParser()]

    @classmethod
    def get_parser(cls, filename: str) -> DocumentParser:
        ext = Path(filename).suffix
        for parser in cls._parsers:
            if parser.supports_format(ext):
                return parser
        raise ValueError(f"Unsupported file format: {ext}")
```

#### 1.3 性能优化

**流式处理大文件**:
```python
# 分块读取 PDF，避免一次性加载到内存
async def parse_large_pdf(file_path: str, chunk_size: int = 10):
    doc = fitz.open(file_path)
    total_pages = len(doc)

    for start in range(0, total_pages, chunk_size):
        end = min(start + chunk_size, total_pages)
        chunk_pages = []

        for page_num in range(start, end):
            page = doc[page_num]
            chunk_pages.append(parse_page(page))

        yield {
            "pages": chunk_pages,
            "progress": (end / total_pages) * 100
        }
```

**缓存机制**:
```python
# Redis 缓存文档解析结果
cache_key = f"document:parsed:{file_hash}"
cached = await redis.get(cache_key)
if cached:
    return json.loads(cached)

parsed_content = await parser.parse(file_path)
await redis.setex(cache_key, 3600, json.dumps(parsed_content))  # 1小时过期
return parsed_content
```

---

### 2. AI 服务架构

#### 2.1 LLM 客户端统一接口

使用 **Langchain** 统一不同 LLM 提供商：

```python
# app/core/ai/llm_client.py
from langchain.llms import OpenAI, Anthropic
from langchain.chat_models import ChatOpenAI, ChatAnthropic
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

class LLMClient:
    def __init__(self, provider: str = "openai", model: str = "gpt-4-turbo"):
        self.provider = provider
        self.model = model
        self.client = self._init_client()

    def _init_client(self):
        if self.provider == "openai":
            return ChatOpenAI(
                model_name=self.model,
                temperature=0.3,  # 降低随机性，提高一致性
                max_tokens=1500,
                streaming=True,
                callbacks=[StreamingStdOutCallbackHandler()]
            )
        elif self.provider == "anthropic":
            return ChatAnthropic(
                model=self.model,
                temperature=0.3,
                max_tokens_to_sample=1500
            )
        elif self.provider == "ollama":
            # 本地模型
            from langchain.llms import Ollama
            return Ollama(model=self.model, base_url="http://localhost:11434")
        else:
            raise ValueError(f"Unknown provider: {self.provider}")

    async def generate(self, prompt: str) -> str:
        response = await self.client.agenerate([prompt])
        return response.generations[0][0].text
```

#### 2.2 文档摘要生成

**Prompt 工程**:

```python
# app/core/ai/summarizer.py
class DocumentSummarizer:
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    async def generate_summary(self, document_content: str, language: str = "zh") -> Dict:
        # 截断过长文本 (保留前 8000 tokens)
        truncated_content = self._truncate_content(document_content, max_tokens=8000)

        prompt = f"""你是一个专业的文档分析助手。请阅读以下文档并生成摘要。

文档内容:
{truncated_content}

请按以下格式输出摘要：

## 文档主题
(用一句话概括，不超过 50 字)

## 核心论点
1. (第一个核心论点，不超过 100 字)
2. (第二个核心论点，不超过 100 字)
3. (第三个核心论点，不超过 100 字)

## 关键结论
1. (第一个结论，不超过 80 字)
2. (第二个结论，不超过 80 字)

## 重点提炼
1. (第一个重点，不超过 50 字)
2. (第二个重点，不超过 50 字)
3. (第三个重点，不超过 50 字)

请确保摘要客观、准确，忠于原文。"""

        response = await self.llm.generate(prompt)
        return self._parse_summary(response)

    def _parse_summary(self, raw_text: str) -> Dict:
        """解析 LLM 输出为结构化数据"""
        # 使用正则表达式提取各部分
        import re

        topic = re.search(r"## 文档主题\n(.+)", raw_text)
        points = re.findall(r"\d+\. (.+)", raw_text)

        return {
            "topic": topic.group(1) if topic else "",
            "core_points": points[:3] if len(points) >= 3 else points,
            "conclusions": points[3:5] if len(points) >= 5 else [],
            "highlights": points[5:8] if len(points) >= 8 else []
        }
```

**缓存策略**:
```python
# 摘要结果缓存 (基于文档内容哈希)
content_hash = hashlib.sha256(document_content.encode()).hexdigest()
cache_key = f"summary:{content_hash}"

cached_summary = await redis.get(cache_key)
if cached_summary:
    return json.loads(cached_summary)

summary = await summarizer.generate_summary(document_content)
await redis.setex(cache_key, 86400, json.dumps(summary))  # 24小时
return summary
```

#### 2.3 智能问答引擎

**RAG (Retrieval-Augmented Generation) 架构**:

```python
# app/core/ai/qa_engine.py
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings

class QAEngine:
    def __init__(self, llm_client: LLMClient, vector_store: Chroma):
        self.llm = llm_client
        self.vector_store = vector_store

    async def answer_question(
        self,
        question: str,
        document_id: str,
        chat_history: List[Dict] = []
    ) -> Dict:
        # 1. 从向量数据库检索相关段落
        relevant_chunks = await self.vector_store.asimilarity_search(
            query=question,
            filter={"document_id": document_id},
            k=3  # 返回 top 3 相关段落
        )

        context = "\n\n".join([chunk.page_content for chunk in relevant_chunks])

        # 2. 构建 Prompt (包含上下文和历史对话)
        history_text = self._format_chat_history(chat_history[-10:])  # 最近 10 轮

        prompt = f"""你是一个智能阅读助手。请基于以下文档内容回答用户问题。

文档相关段落：
{context}

历史对话：
{history_text}

用户问题：{question}

回答要求：
1. 如果文档中包含答案，请基于原文回答，并引用相关段落
2. 如果文档中未提及，请明确说明"文档中未找到相关内容"
3. 回答简洁明了，不超过 200 字

请回答："""

        response = await self.llm.generate(prompt)

        return {
            "answer": response,
            "sources": [
                {
                    "page_num": chunk.metadata["page_num"],
                    "snippet": chunk.page_content[:100],
                    "relevance_score": chunk.metadata.get("score", 0)
                }
                for chunk in relevant_chunks
            ]
        }

    def _format_chat_history(self, history: List[Dict]) -> str:
        lines = []
        for msg in history:
            role = "用户" if msg["role"] == "user" else "助手"
            lines.append(f"{role}: {msg['content']}")
        return "\n".join(lines)
```

**向量数据库初始化**:
```python
# 文档上传后，异步生成 embeddings
@celery_app.task
async def generate_embeddings(document_id: str):
    document = await get_document(document_id)

    # 分块文本 (每块 500 字，重叠 50 字)
    chunks = split_text(document.content, chunk_size=500, overlap=50)

    # 生成 embeddings
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    # 存入 ChromaDB
    vector_store = Chroma(
        collection_name="documents",
        embedding_function=embeddings,
        persist_directory="./data/chroma"
    )

    vector_store.add_texts(
        texts=chunks,
        metadatas=[
            {
                "document_id": document_id,
                "page_num": chunk.page_num,
                "chunk_index": i
            }
            for i, chunk in enumerate(chunks)
        ]
    )
```

---

### 3. 前端架构设计

#### 3.1 状态管理 (Zustand)

```typescript
// lib/store/document-store.ts
import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

interface Document {
  id: string;
  title: string;
  pageCount: number;
  currentPage: number;
  scrollPosition: number;
}

interface DocumentStore {
  currentDocument: Document | null;
  documents: Document[];

  // Actions
  setCurrentDocument: (doc: Document) => void;
  updateScrollPosition: (position: number) => void;
  addDocument: (doc: Document) => void;
}

export const useDocumentStore = create<DocumentStore>()(
  devtools(
    persist(
      (set) => ({
        currentDocument: null,
        documents: [],

        setCurrentDocument: (doc) => set({ currentDocument: doc }),

        updateScrollPosition: (position) =>
          set((state) => ({
            currentDocument: state.currentDocument
              ? { ...state.currentDocument, scrollPosition: position }
              : null,
          })),

        addDocument: (doc) =>
          set((state) => ({ documents: [...state.documents, doc] })),
      }),
      {
        name: 'document-storage', // LocalStorage key
        partialize: (state) => ({
          documents: state.documents,
          currentDocument: state.currentDocument,
        }),
      }
    )
  )
);
```

#### 3.2 数据获取 (TanStack Query)

```typescript
// lib/hooks/useDocument.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';

export function useDocument(documentId: string) {
  return useQuery({
    queryKey: ['document', documentId],
    queryFn: () => apiClient.get(`/documents/${documentId}`),
    staleTime: 5 * 60 * 1000, // 5分钟内不重新请求
  });
}

export function useUploadDocument() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (file: File) => {
      const formData = new FormData();
      formData.append('file', file);
      return apiClient.post('/documents', formData);
    },
    onSuccess: (data) => {
      // 上传成功后，将新文档添加到缓存
      queryClient.setQueryData(['document', data.document_id], data);

      // 如果是异步处理，启动轮询检查状态
      if (data.status === 'processing') {
        startPolling(data.document_id);
      }
    },
  });
}

function startPolling(documentId: string) {
  const interval = setInterval(async () => {
    const status = await apiClient.get(`/documents/${documentId}/status`);

    if (status.status === 'completed' || status.status === 'failed') {
      clearInterval(interval);
      queryClient.invalidateQueries(['document', documentId]);
    }
  }, 2000); // 每2秒轮询一次
}
```

#### 3.3 文档渲染组件

```typescript
// components/reader/DocumentViewer/PDFViewer.tsx
import { Document, Page, pdfjs } from 'react-pdf';
import { useVirtualizer } from '@tanstack/react-virtual';
import 'react-pdf/dist/esm/Page/AnnotationLayer.css';
import 'react-pdf/dist/esm/Page/TextLayer.css';

pdfjs.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.min.js`;

interface PDFViewerProps {
  fileUrl: string;
  onPageChange: (pageNum: number) => void;
  initialPage?: number;
}

export function PDFViewer({ fileUrl, onPageChange, initialPage = 1 }: PDFViewerProps) {
  const [numPages, setNumPages] = useState(0);
  const [scale, setScale] = useState(1.0);

  const parentRef = useRef<HTMLDivElement>(null);

  // 虚拟滚动优化 (仅渲染可见页面)
  const rowVirtualizer = useVirtualizer({
    count: numPages,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 800, // 估计每页高度
    overscan: 2, // 预渲染前后2页
  });

  function onDocumentLoadSuccess({ numPages }: { numPages: number }) {
    setNumPages(numPages);
  }

  useEffect(() => {
    // 滚动到初始页
    if (initialPage && parentRef.current) {
      rowVirtualizer.scrollToIndex(initialPage - 1);
    }
  }, [initialPage]);

  return (
    <div className="pdf-viewer relative h-full overflow-auto" ref={parentRef}>
      {/* 缩放控制 */}
      <div className="fixed top-4 right-4 z-10 flex gap-2">
        <Button onClick={() => setScale(s => Math.max(0.5, s - 0.1))}>-</Button>
        <span>{Math.round(scale * 100)}%</span>
        <Button onClick={() => setScale(s => Math.min(2.0, s + 0.1))}>+</Button>
      </div>

      <Document
        file={fileUrl}
        onLoadSuccess={onDocumentLoadSuccess}
        loading={<LoadingSpinner />}
      >
        <div
          style={{
            height: `${rowVirtualizer.getTotalSize()}px`,
            width: '100%',
            position: 'relative',
          }}
        >
          {rowVirtualizer.getVirtualItems().map((virtualRow) => (
            <div
              key={virtualRow.index}
              style={{
                position: 'absolute',
                top: 0,
                left: 0,
                width: '100%',
                height: `${virtualRow.size}px`,
                transform: `translateY(${virtualRow.start}px)`,
              }}
            >
              <Page
                pageNumber={virtualRow.index + 1}
                scale={scale}
                onLoadSuccess={() => onPageChange(virtualRow.index + 1)}
                renderTextLayer={true}
                renderAnnotationLayer={true}
              />
            </div>
          ))}
        </div>
      </Document>
    </div>
  );
}
```

---

### 4. 标注系统实现

#### 4.1 文本选择与标注工具栏

```typescript
// components/reader/Annotation/AnnotationToolbar.tsx
import { useEffect, useState } from 'react';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';

interface AnnotationToolbarProps {
  onHighlight: (color: 'yellow' | 'red') => void;
  onAnnotate: (text: string) => void;
  onCancel: () => void;
}

export function AnnotationToolbar({ onHighlight, onAnnotate, onCancel }: AnnotationToolbarProps) {
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [selection, setSelection] = useState<Selection | null>(null);
  const [annotationText, setAnnotationText] = useState('');
  const [showAnnotationInput, setShowAnnotationInput] = useState(false);

  useEffect(() => {
    function handleSelectionChange() {
      const sel = window.getSelection();

      if (sel && sel.toString().trim().length > 0) {
        const range = sel.getRangeAt(0);
        const rect = range.getBoundingClientRect();

        // 工具栏显示在选中文本下方
        setPosition({
          x: rect.left + rect.width / 2,
          y: rect.bottom + 10,
        });
        setSelection(sel);
      } else {
        setSelection(null);
        setShowAnnotationInput(false);
      }
    }

    document.addEventListener('selectionchange', handleSelectionChange);
    return () => document.removeEventListener('selectionchange', handleSelectionChange);
  }, []);

  if (!selection) return null;

  return (
    <div
      className="fixed z-50 flex gap-2 bg-white shadow-lg rounded-lg p-2 border"
      style={{ left: position.x, top: position.y, transform: 'translateX(-50%)' }}
    >
      {!showAnnotationInput ? (
        <>
          <Button
            size="sm"
            variant="ghost"
            onClick={() => {
              onHighlight('yellow');
              setSelection(null);
            }}
          >
            🟡 高亮
          </Button>

          <Button
            size="sm"
            variant="ghost"
            onClick={() => {
              onHighlight('red');
              setSelection(null);
            }}
          >
            🔴 重点
          </Button>

          <Button
            size="sm"
            variant="ghost"
            onClick={() => setShowAnnotationInput(true)}
          >
            📝 批注
          </Button>

          <Button size="sm" variant="ghost" onClick={onCancel}>
            ❌
          </Button>
        </>
      ) : (
        <div className="flex gap-2 items-center">
          <Input
            placeholder="输入批注内容..."
            value={annotationText}
            onChange={(e) => setAnnotationText(e.target.value)}
            autoFocus
            className="w-64"
          />
          <Button
            size="sm"
            onClick={() => {
              onAnnotate(annotationText);
              setAnnotationText('');
              setShowAnnotationInput(false);
              setSelection(null);
            }}
          >
            保存
          </Button>
          <Button
            size="sm"
            variant="ghost"
            onClick={() => {
              setShowAnnotationInput(false);
              setAnnotationText('');
            }}
          >
            取消
          </Button>
        </div>
      )}
    </div>
  );
}
```

#### 4.2 标注数据模型

```python
# backend/app/models/annotation.py
from sqlalchemy import Column, String, Integer, Text, Enum, DateTime, ForeignKey
from sqlalchemy.orm import relationship
import enum

class AnnotationType(str, enum.Enum):
    HIGHLIGHT = "highlight"
    IMPORTANT = "important"
    NOTE = "note"

class Annotation(Base):
    __tablename__ = "annotations"

    id = Column(String, primary_key=True, default=lambda: f"ann_{uuid4().hex[:12]}")
    document_id = Column(String, ForeignKey("documents.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)

    # 标注类型
    type = Column(Enum(AnnotationType), nullable=False)

    # 标注位置 (存储为 JSON)
    position = Column(JSON, nullable=False)
    # 示例: {"page": 5, "start": 120, "end": 350, "rects": [[x1, y1, x2, y2]]}

    # 选中的文本
    selected_text = Column(Text, nullable=False)

    # 批注内容 (仅 type=note 时有值)
    note_content = Column(Text, nullable=True)

    # 高亮颜色
    color = Column(String, default="yellow")  # yellow | red

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    document = relationship("Document", back_populates="annotations")
    user = relationship("User", back_populates="annotations")
```

**API 设计**:
```python
# POST /api/v1/annotations
{
  "document_id": "doc_123abc",
  "type": "note",
  "position": {
    "page": 5,
    "start": 120,
    "end": 350,
    "rects": [[100, 200, 300, 220]]
  },
  "selected_text": "深度学习是机器学习的一个子集",
  "note_content": "这段话需要进一步验证",
  "color": "yellow"
}

# GET /api/v1/annotations?document_id=doc_123abc
[
  {
    "id": "ann_xyz789",
    "type": "note",
    "position": {...},
    "selected_text": "...",
    "note_content": "...",
    "created_at": "2025-10-21T10:30:00Z"
  }
]
```

---

### 5. 数据库设计

#### 5.1 核心表结构

```sql
-- 用户表
CREATE TABLE users (
    id VARCHAR(50) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    display_name VARCHAR(100),
    avatar_url VARCHAR(500),
    settings JSON,  -- 用户设置 (字体大小、主题等)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 文档表
CREATE TABLE documents (
    id VARCHAR(50) PRIMARY KEY,
    user_id VARCHAR(50) REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    filename VARCHAR(500) NOT NULL,
    file_path VARCHAR(1000) NOT NULL,  -- 本地文件系统路径
    file_hash VARCHAR(64) NOT NULL,    -- SHA256 哈希 (用于去重)
    file_size BIGINT NOT NULL,
    file_format VARCHAR(20) NOT NULL,  -- pdf | epub | docx | md | txt

    -- 解析后的内容
    page_count INT,
    word_count INT,
    parsed_content JSON,  -- 存储解析后的结构化内容

    -- 元数据
    author VARCHAR(255),
    language VARCHAR(10),
    tags JSON,

    -- 阅读进度
    current_page INT DEFAULT 1,
    scroll_position FLOAT DEFAULT 0.0,
    reading_progress FLOAT DEFAULT 0.0,  -- 0-100%

    -- 时间戳
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_read_at TIMESTAMP,

    INDEX idx_user_id (user_id),
    INDEX idx_file_hash (file_hash)
);

-- 标注表 (已在上文定义)
CREATE TABLE annotations (
    id VARCHAR(50) PRIMARY KEY,
    document_id VARCHAR(50) REFERENCES documents(id) ON DELETE CASCADE,
    user_id VARCHAR(50) REFERENCES users(id) ON DELETE CASCADE,
    type ENUM('highlight', 'important', 'note') NOT NULL,
    position JSON NOT NULL,
    selected_text TEXT NOT NULL,
    note_content TEXT,
    color VARCHAR(20) DEFAULT 'yellow',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_document_id (document_id),
    INDEX idx_user_id (user_id)
);

-- 聊天消息表
CREATE TABLE chat_messages (
    id VARCHAR(50) PRIMARY KEY,
    document_id VARCHAR(50) REFERENCES documents(id) ON DELETE CASCADE,
    user_id VARCHAR(50) REFERENCES users(id) ON DELETE CASCADE,
    role ENUM('user', 'assistant') NOT NULL,
    content TEXT NOT NULL,

    -- AI 回答的元数据
    sources JSON,  -- 引用的原文位置
    model VARCHAR(50),  -- 使用的模型名称
    tokens_used INT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_document_id (document_id),
    INDEX idx_user_id (user_id)
);

-- 阅读会话表
CREATE TABLE reading_sessions (
    id VARCHAR(50) PRIMARY KEY,
    document_id VARCHAR(50) REFERENCES documents(id) ON DELETE CASCADE,
    user_id VARCHAR(50) REFERENCES users(id) ON DELETE CASCADE,

    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    duration_seconds INT,  -- 阅读时长 (秒)
    pages_read JSON,  -- 阅读的页码列表

    INDEX idx_document_id (document_id),
    INDEX idx_user_id (user_id),
    INDEX idx_start_time (start_time)
);

-- AI 摘要缓存表
CREATE TABLE ai_summaries (
    id VARCHAR(50) PRIMARY KEY,
    document_id VARCHAR(50) REFERENCES documents(id) ON DELETE CASCADE,
    content_hash VARCHAR(64) NOT NULL,  -- 文档内容哈希

    summary JSON NOT NULL,  -- 摘要结构化数据
    model VARCHAR(50) NOT NULL,
    tokens_used INT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE INDEX idx_content_hash (content_hash)
);
```

#### 5.2 索引优化

```sql
-- 复合索引 (加速常见查询)
CREATE INDEX idx_user_document ON documents(user_id, last_read_at DESC);
CREATE INDEX idx_document_annotations ON annotations(document_id, created_at DESC);
CREATE INDEX idx_user_sessions ON reading_sessions(user_id, start_time DESC);

-- 全文搜索索引 (MySQL 5.7+)
ALTER TABLE documents ADD FULLTEXT INDEX ft_title_content (title, parsed_content);
```

---

### 6. 部署架构

#### 6.1 Docker Compose (本地开发)

```yaml
# docker-compose.yml
version: '3.9'

services:
  # 前端开发服务器
  frontend:
    build:
      context: ./frontend
      dockerfile: ../docker/frontend.Dockerfile
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
    depends_on:
      - backend

  # 后端 API 服务器
  backend:
    build:
      context: ./backend
      dockerfile: ../docker/backend.Dockerfile
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
      - ./data/documents:/app/data/documents
      - ./data/chroma:/app/data/chroma
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/readpilot
      - REDIS_URL=redis://redis:6379/0
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    depends_on:
      - db
      - redis

  # Celery Worker (异步任务)
  celery_worker:
    build:
      context: ./backend
      dockerfile: ../docker/backend.Dockerfile
    command: celery -A app.tasks.celery_app worker --loglevel=info
    volumes:
      - ./backend:/app
      - ./data/documents:/app/data/documents
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/readpilot
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis

  # PostgreSQL 数据库
  db:
    image: postgres:16-alpine
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=readpilot
    volumes:
      - postgres_data:/var/lib/postgresql/data

  # Redis (缓存 + Celery 消息队列)
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

#### 6.2 生产环境部署 (AWS)

**架构图**:
```
用户浏览器
    ↓
Cloudflare CDN (静态资源 + DDoS 防护)
    ↓
AWS ALB (Application Load Balancer)
    ↓
┌─────────────────┬─────────────────┐
│ ECS Fargate     │ ECS Fargate     │
│ (Frontend)      │ (Backend)       │
│ Next.js SSR     │ FastAPI         │
└─────────────────┴─────────────────┘
         ↓                  ↓
    Vercel Edge        AWS RDS PostgreSQL
    (可选)             AWS ElastiCache Redis
                       AWS S3 (文档存储)
```

**Terraform 配置示例**:
```hcl
# terraform/main.tf
resource "aws_ecs_cluster" "readpilot" {
  name = "readpilot-cluster"
}

resource "aws_ecs_task_definition" "backend" {
  family                   = "readpilot-backend"
  requires_compatibilities = ["FARGATE"]
  network_mode            = "awsvpc"
  cpu                     = "1024"
  memory                  = "2048"

  container_definitions = jsonencode([{
    name  = "backend"
    image = "${aws_ecr_repository.backend.repository_url}:latest"
    portMappings = [{
      containerPort = 8000
      protocol      = "tcp"
    }]
    environment = [
      { name = "DATABASE_URL", value = "postgresql://..." },
      { name = "REDIS_URL", value = "redis://..." }
    ]
  }])
}

resource "aws_rds_cluster" "main" {
  cluster_identifier = "readpilot-db"
  engine             = "aurora-postgresql"
  engine_version     = "16.1"
  master_username    = "admin"
  master_password    = random_password.db_password.result

  serverlessv2_scaling_configuration {
    min_capacity = 0.5
    max_capacity = 2.0
  }
}
```

---

### 7. 性能优化策略

#### 7.1 前端性能

| 优化项 | 实现方案 |
|-------|---------|
| **代码分割** | Next.js 自动分割 + `next/dynamic` 动态加载 |
| **图片优化** | `next/image` 自动优化 + WebP 格式 |
| **虚拟滚动** | `@tanstack/react-virtual` (大文档) |
| **Service Worker** | 缓存已读文档和静态资源 |
| **预加载** | `<link rel="preload">` 关键资源 |
| **CSS 优化** | Tailwind CSS JIT + PurgeCSS |

**Bundle 分析**:
```bash
# 分析打包体积
ANALYZE=true pnpm build

# 目标: Total Size < 500KB (gzipped)
```

#### 7.2 后端性能

| 优化项 | 实现方案 |
|-------|---------|
| **数据库连接池** | SQLAlchemy async pool (pool_size=20) |
| **查询优化** | 使用 `joinedload()` 避免 N+1 查询 |
| **Redis 缓存** | 热点数据缓存 (摘要、用户设置) |
| **异步 I/O** | FastAPI async endpoints + asyncio |
| **响应压缩** | Gzip/Brotli middleware |
| **API 限流** | `slowapi` (100 req/min per user) |

**基准测试**:
```bash
# 使用 Locust 进行负载测试
locust -f tests/load/locustfile.py --host=http://localhost:8000

# 目标: 95th percentile < 500ms
```

---

## Testing Strategy

### 单元测试

**Frontend**:
```typescript
// tests/unit/components/DocumentViewer.test.tsx
import { render, screen } from '@testing-library/react';
import { PDFViewer } from '@/components/reader/DocumentViewer/PDFViewer';

describe('PDFViewer', () => {
  it('renders PDF document', async () => {
    render(<PDFViewer fileUrl="/sample.pdf" onPageChange={vi.fn()} />);

    expect(await screen.findByText('Loading PDF...')).toBeInTheDocument();
    // ... more assertions
  });
});
```

**Backend**:
```python
# tests/unit/test_pdf_parser.py
import pytest
from app.core.document_parser import PDFParser

@pytest.mark.asyncio
async def test_pdf_parser():
    parser = PDFParser()
    result = await parser.parse("tests/fixtures/sample.pdf", {})

    assert result["page_count"] > 0
    assert len(result["pages"]) == result["page_count"]
```

### 集成测试

```python
# tests/integration/test_document_upload.py
@pytest.mark.asyncio
async def test_upload_document(client: AsyncClient, auth_headers):
    with open("tests/fixtures/sample.pdf", "rb") as f:
        response = await client.post(
            "/api/v1/documents",
            files={"file": ("sample.pdf", f, "application/pdf")},
            headers=auth_headers
        )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["completed", "processing"]
```

### E2E 测试 (Playwright)

```typescript
// tests/e2e/reading-flow.spec.ts
import { test, expect } from '@playwright/test';

test('complete reading flow', async ({ page }) => {
  // 1. 上传文档
  await page.goto('http://localhost:3000');
  await page.setInputFiles('input[type="file"]', 'tests/fixtures/sample.pdf');
  await page.click('button:has-text("上传文档")');

  // 2. 等待文档加载
  await expect(page.locator('.pdf-viewer')).toBeVisible({ timeout: 5000 });

  // 3. 生成摘要
  await page.click('button:has-text("生成摘要")');
  await expect(page.locator('.summary-card')).toBeVisible({ timeout: 5000 });

  // 4. 提问
  await page.fill('textarea[placeholder*="输入问题"]', '这篇文档的主题是什么？');
  await page.press('textarea', 'Control+Enter');
  await expect(page.locator('.ai-response')).toBeVisible({ timeout: 3000 });

  // 5. 添加标注
  await page.selectText('.document-content', { start: 100, end: 200 });
  await page.click('button:has-text("高亮")');
  await expect(page.locator('.highlight-yellow')).toBeVisible();
});
```

---

## Security Considerations

### 1. 输入验证

```python
# backend/app/utils/file_validation.py
import magic

ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/epub+zip",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
    "text/markdown"
}

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

def validate_upload_file(file: UploadFile) -> None:
    # 1. 检查文件大小
    file.file.seek(0, 2)
    size = file.file.tell()
    file.file.seek(0)

    if size > MAX_FILE_SIZE:
        raise HTTPException(400, "文件大小超过 50MB 限制")

    # 2. 验证 MIME 类型 (基于魔法字节)
    file_bytes = file.file.read(2048)
    file.file.seek(0)

    mime = magic.from_buffer(file_bytes, mime=True)
    if mime not in ALLOWED_MIME_TYPES:
        raise HTTPException(400, f"不支持的文件类型: {mime}")

    # 3. 文件名清洗 (防止路径遍历)
    safe_filename = secure_filename(file.filename)
    return safe_filename
```

### 2. API 认证

```python
# backend/app/api/deps.py
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.utils.security import decode_jwt

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    token = credentials.credentials
    payload = decode_jwt(token)

    if not payload:
        raise HTTPException(401, "无效的认证令牌")

    user = await get_user_by_id(payload["user_id"])
    if not user:
        raise HTTPException(401, "用户不存在")

    return user
```

### 3. XSS 防护

```typescript
// frontend/lib/utils/sanitize.ts
import DOMPurify from 'isomorphic-dompurify';

export function sanitizeHTML(html: string): string {
  return DOMPurify.sanitize(html, {
    ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'a', 'p', 'br'],
    ALLOWED_ATTR: ['href'],
  });
}

// 使用示例
<div dangerouslySetInnerHTML={{ __html: sanitizeHTML(userInput) }} />
```

---

## Monitoring & Observability

### 1. 错误追踪 (Sentry)

```typescript
// frontend/app/layout.tsx
import * as Sentry from '@sentry/nextjs';

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  environment: process.env.NODE_ENV,
  tracesSampleRate: 0.1,
});
```

```python
# backend/app/main.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    integrations=[FastApiIntegration()],
    traces_sample_rate=0.1,
)
```

### 2. 性能监控 (Prometheus)

```python
# backend/app/middleware/metrics.py
from prometheus_client import Counter, Histogram

request_count = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
request_duration = Histogram('http_request_duration_seconds', 'HTTP request duration')

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()

    response = await call_next(request)

    duration = time.time() - start_time
    request_duration.observe(duration)
    request_count.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()

    return response
```

### 3. 日志记录

```python
# backend/app/config.py
import logging
from logging.handlers import RotatingFileHandler

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        RotatingFileHandler('logs/app.log', maxBytes=10*1024*1024, backupCount=5),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
```

---

## Open Questions & Next Steps

### 待解决问题

1. **AI 模型最终选择**:
   - [ ] 对比 GPT-4 Turbo vs Claude 3 Sonnet 的摘要质量
   - [ ] 测试 Ollama Llama 3.1 8B 的离线性能
   - [ ] 制定模型切换策略 (基于成本和质量)

2. **OCR 功能优先级**:
   - [ ] 评估扫描版 PDF 的用户需求 (通过用户调研)
   - [ ] 对比 Tesseract vs Google Cloud Vision API 的准确率
   - [ ] 决定是否在 MVP 中包含 OCR

3. **桌面应用方案**:
   - [ ] 对比 Tauri vs Electron 的性能和打包体积
   - [ ] 评估 Web 版本是否能满足 80% 用户需求
   - [ ] 决定桌面应用的开发优先级 (v1.0 或 v1.1)

### 技术债务预警

- **云端 LLM API 依赖**: 需在 v1.1 前增强本地模型支持
- **缺少离线模式**: MVP 仅支持在线使用，需尽快实现离线能力
- **缺少数据备份**: 需实现自动备份功能，防止数据丢失

---

## Approval & Sign-off

**Technical Review**:
- [ ] Frontend Lead: 确认 Next.js 架构设计
- [ ] Backend Lead: 确认 FastAPI 和数据库设计
- [ ] DevOps: 确认部署架构和 CI/CD 流程
- [ ] Security: 确认安全措施充分

**Constitution Compliance**:
- [x] 隐私优先原则: 部分合规，已记录违反项和缓解措施
- [x] 性能优先原则: 完全合规
- [x] 可扩展性原则: 完全合规
- [x] 可访问性原则: 完全合规
- [x] 简约设计原则: 完全合规

**Status**: ✅ 技术方案已完成，待团队审查批准

**Next Step**: 使用 `/speckit.tasks` 命令生成详细任务列表
