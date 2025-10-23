# 实施计划：核心阅读体验

**分支**: `001-core-reading-experience` | **日期**: 2025-10-22 | **规格说明**: [spec.md](./spec.md)
**输入**: 来自 `/specs/001-core-reading-experience/spec.md` 的功能规格说明

**注意**: 此模板由 `/speckit.plan` 命令填充。请参阅 `.specify/templates/commands/plan.md` 了解执行工作流。

## 概述

ReadPilot MVP 实现核心阅读体验，包括文档处理管道（Document Processing Pipeline：上传、提取、分块、向量化）和基础 AI 交互（摘要生成和问答）。系统采用 FastAPI 后端 + Next.js 前端架构，使用 PostgreSQL 作为主数据库，ChromaDB 作为向量数据库（Vector Database），OpenAI/Anthropic 提供 AI 能力。功能按优先级分为三个用户故事：P1-文档上传处理（MVP）、P2-智能摘要、P3-上下文问答。

## 技术背景

**语言/版本**:
- 后端: Python 3.12
- 前端: TypeScript 5.7 + Node.js 22 LTS

**主要依赖**:
- 后端: FastAPI 0.115, SQLAlchemy 2.0, ChromaDB 0.5, Celery 5.4, OpenAI SDK, Anthropic SDK
- 前端: Next.js 15, React 19, Tailwind CSS 4.0, Zustand 5.0, Axios

**存储**:
- 主数据库: PostgreSQL 17 (生产环境), SQLite 3.47 (开发环境)
- 向量数据库（Vector Database）: ChromaDB 0.5
- 缓存（Cache）: Redis 7.4
- 文件存储（File Storage）: 本地文件系统 (开发), S3 兼容对象存储 (生产)

**测试**:
- 后端: pytest, pytest-asyncio, pytest-cov
- 前端: Vitest, React Testing Library, Playwright (E2E)
- 测试覆盖率目标: ≥80% (核心功能)

**目标平台**:
- 后端: Linux 服务器 (Docker 容器)
- 前端: 现代 Web 浏览器 (Chrome, Firefox, Safari, Edge - 最新 2 个版本)
- 部署方式: Docker Compose (开发), Kubernetes (生产)

**项目类型**: Web 应用 (前后端分离架构)

**性能目标**:
- API 响应时间: p95 < 3s, p99 < 5s
- 文档上传: 10MB 文件 < 5s
- 文本提取: 100 页 PDF < 30s
- 摘要生成: 10 页文档 < 10s
- 向量搜索（Vector Search）: < 2s
- 支持 1000 并发用户

**约束条件**:
- 文档大小限制: 50MB
- 最大文档页数: 1000 页
- 会话超时（Session Timeout）: 24 小时
- 速率限制（Rate Limiting）: 100 请求/分钟/用户
- AI API 成本: 需要实施缓存和速率限制以控制成本

**规模/范围**:
- 目标用户: 首月 1000 用户
- 每用户文档数: 最多 10,000 篇
- 对话历史保留: 90 天
- 预期存储增长: 需要监控和扩容策略

## 宪章检查

*门控（GATE）: 必须在 Phase 0 研究前通过。在 Phase 1 设计后重新检查。*

**状态**: ⚠️ 部分违规 - 需要记录在复杂度追踪表

### 原则 1: 隐私优先 (Privacy First) - ✅ 通过

- ✅ 数据存储: 使用 PostgreSQL/SQLite，支持本地部署
- ✅ AI 服务调用: 通过用户显式操作触发（摘要、问答）
- ✅ 用户数据: 文档和对话历史存储在用户控制的数据库中
- ⚠️ **需要实施**: 配置选项允许用户选择本地 AI 模型（Ollama）vs 云端 API

**行动项**:
- 在 Phase 0 研究中探索本地 AI 模型集成方案
- 确保 AI 服务调用前有用户授权机制

### 原则 2: 性能优先 (Performance First) - ✅ 通过

性能目标与宪章要求对齐：

- ✅ 文档处理: < 2s (50MB) - 规格要求 < 5s (10MB)
- ✅ AI 功能响应: < 3s - 规格要求摘要 < 10s, 问答 < 5s
- ✅ UI 交互: 设计目标 < 100ms
- ✅ 内存占用: 通过 Docker 容器资源限制控制
- ✅ 启动时间: Web 应用首次加载目标 < 3s

**行动项**:
- 实施流式处理（Streaming）处理大文档
- 使用 Redis 缓存摘要和向量搜索结果
- 异步任务队列（Async Task Queue） (Celery) 处理文档处理

### 原则 3: 可扩展性 (Extensibility) - ✅ 已解决

**原违规点** (已修复):
- ~~当前架构紧密耦合 OpenAI/Anthropic API~~
- ~~文档处理库硬编码（PyPDF2, python-docx, ebooklib）~~

**已实施的缓解措施**:
- ✅ **多 AI 提供商架构** (2025-10-23 完成):
  - 实现了 `BaseLLMService` 和 `BaseEmbeddingService` 抽象基类
  - 支持三种 AI 提供商: OpenAI, Anthropic, 阿里云千问 (Qwen)
  - LLM 服务:通过环境变量 `PRIMARY_AI_PROVIDER` 和 `FALLBACK_AI_PROVIDER` 配置主/备提供商
  - Embedding 服务: 跟随 `PRIMARY_AI_PROVIDER` 配置,确保与 LLM 提供商一致 (Anthropic 除外,会降级到 OpenAI/Qwen)
  - 配置文件: `backend/.env` 统一管理 API Keys
  - 代码位置: `backend/app/core/ai/{base.py, openai_service.py, anthropic_service.py, qwen_service.py}`

- ✅ **文档处理器插件化** (已完成):
  - 采用策略模式 `BaseDocumentParser` 抽象类
  - 支持 PDF (PyMuPDF), EPUB, DOCX, TXT, Markdown
  - 工厂模式 `DocumentParserFactory` 自动选择解析器
  - 代码位置: `backend/app/core/document_parser/`

- ✅ **依赖注入**:
  - AI 服务通过 `get_embedding_service()` 和 `get_llm_service()` 工厂函数获取
  - 文档解析器通过 `document_parser_factory` 全局实例管理

**环境变量配置**:
```bash
# 至少配置一个 API Key
OPENAI_API_KEY=sk-xxx          # 可选
ANTHROPIC_API_KEY=sk-xxx       # 可选
QWEN_API_KEY=sk-xxx            # 推荐

# LLM 提供商配置
PRIMARY_AI_PROVIDER=qwen       # openai, anthropic, qwen
FALLBACK_AI_PROVIDER=openai   # 备用提供商
LLM_PROVIDER=qwen
LLM_MODEL=qwen-max

# Embedding 自动选择 (优先 Qwen → 降级 OpenAI)
EMBEDDING_MODEL=text-embedding-v3
```

**记录位置**: 见下方复杂度追踪表 (已标记为已解决)

### 原则 4: 可访问性 (Accessibility) - ✅ 通过

- ✅ 键盘导航: Next.js + Radix UI 组件库原生支持
- ✅ 屏幕阅读器（Screen Reader）: 使用语义化 HTML 和 ARIA 标签
- ✅ 视觉辅助: Tailwind CSS 支持高对比度和响应式字体
- ✅ 认知友好: 清晰的错误提示和加载状态

**行动项**:
- Phase 1 设计中包含可访问性测试检查点
- 使用 axe-core 进行自动化可访问性测试

### 原则 5: 简约设计 (Simplicity) - ✅ 通过

MVP 范围符合简约原则：

- ✅ 核心功能明确: 上传 → 处理 → 摘要 → 问答
- ✅ 功能渐进披露: P1 (MVP) → P2 (摘要) → P3 (问答)
- ✅ 零配置理念: 默认设置覆盖基本用户需求
- ✅ 超出范围定义清晰: 避免功能蔓延

### 技术栈约束 - ✅ 通过

- ✅ 前端: React + TypeScript + Vite (符合宪章)
- ✅ 状态管理（State Management）: Zustand (符合宪章推荐)
- ✅ UI 库: 计划使用 Radix UI (无障碍友好)
- ✅ 后端: Python 3.12 + FastAPI (符合宪章)
- ✅ 数据库: SQLite (本地) + PostgreSQL (可选云)
- ✅ 文档处理: PyMuPDF (fitz) 优于 PyPDF2 (更快更准确)

### 依赖管理策略 - ✅ 通过

- ✅ 所有依赖均为成熟开源库
- ✅ 许可证: MIT/Apache 2.0 兼容
- ✅ 安全: 使用 Dependabot 自动扫描

### 测试策略 - ✅ 通过

- ✅ 测试金字塔（Test Pyramid）: 70% 单元测试, 20% 集成测试, 10% E2E
- ✅ 覆盖率目标: ≥80%
- ✅ 工具选择: pytest (后端), Vitest (前端), Playwright (E2E)

**总结**: 宪章检查基本通过，主要问题在于可扩展性原则的部分违规（AI 提供商耦合），已计划通过架构设计缓解。

## 项目结构

### 文档 (本功能)

```text
specs/[###-feature]/
├── plan.md              # 本文件 (/speckit.plan 命令输出)
├── research.md          # Phase 0 输出 (/speckit.plan 命令)
├── data-model.md        # Phase 1 输出 (/speckit.plan 命令)
├── quickstart.md        # Phase 1 输出 (/speckit.plan 命令)
├── contracts/           # Phase 1 输出 (/speckit.plan 命令)
└── tasks.md             # Phase 2 输出 (/speckit.tasks 命令 - 不由 /speckit.plan 创建)
```

### 源代码 (仓库根目录)

```text
backend/
├── src/
│   ├── main.py                 # FastAPI 应用入口
│   ├── config/                 # 配置管理（Configuration）
│   │   ├── settings.py         # 环境配置
│   │   └── database.py         # 数据库连接
│   ├── models/                 # SQLAlchemy 数据模型（Data Models）
│   │   ├── user.py
│   │   ├── document.py
│   │   ├── chat_session.py
│   │   ├── message.py
│   │   └── reading_history.py
│   ├── schemas/                # Pydantic 请求/响应模型（Request/Response Schemas）
│   │   ├── auth.py
│   │   ├── document.py
│   │   ├── chat.py
│   │   └── user.py
│   ├── api/                    # API 路由（Routes）
│   │   ├── v1/
│   │   │   ├── auth.py         # 认证端点（Authentication Endpoints）
│   │   │   ├── documents.py    # 文档管理
│   │   │   ├── chat.py         # 对话交互
│   │   │   └── users.py        # 用户管理
│   │   └── deps.py             # 依赖注入（Dependency Injection）
│   ├── services/               # 业务逻辑层（Business Logic Layer）
│   │   ├── auth_service.py     # 认证服务
│   │   ├── document_service.py # 文档处理
│   │   ├── ai_service.py       # AI 集成（抽象层）
│   │   ├── vector_service.py   # 向量数据库
│   │   └── cache_service.py    # 缓存管理
│   ├── core/                   # 核心功能模块
│   │   ├── document_parser/    # 文档解析器（Document Parsers）
│   │   │   ├── base.py         # 抽象基类（Abstract Base Class）
│   │   │   ├── pdf_parser.py
│   │   │   ├── epub_parser.py
│   │   │   ├── docx_parser.py
│   │   │   └── markdown_parser.py
│   │   ├── text_chunker.py     # 文本分块（Text Chunking）
│   │   ├── embedding_generator.py  # 向量生成（Embedding Generation）
│   │   └── ai_providers/       # AI 提供商适配器（AI Provider Adapters）
│   │       ├── base.py         # 抽象接口（Abstract Interface）
│   │       ├── openai_provider.py
│   │       └── anthropic_provider.py
│   ├── tasks/                  # Celery 异步任务（Async Tasks）
│   │   ├── document_processing.py
│   │   └── embedding_tasks.py
│   └── utils/                  # 工具函数（Utilities）
│       ├── security.py         # 加密和验证
│       ├── file_handler.py     # 文件操作
│       └── logger.py           # 日志配置
├── tests/
│   ├── unit/                   # 单元测试（Unit Tests）
│   │   ├── test_parsers.py
│   │   ├── test_chunker.py
│   │   └── test_ai_service.py
│   ├── integration/            # 集成测试（Integration Tests）
│   │   ├── test_document_flow.py
│   │   └── test_chat_flow.py
│   └── e2e/                    # E2E 测试（End-to-End Tests）
│       └── test_user_journey.py
├── alembic/                    # 数据库迁移（Database Migrations）
├── pyproject.toml              # Poetry 依赖管理
└── docker-compose.yml          # 开发环境

frontend/
├── src/
│   ├── app/                    # Next.js 15 App Router
│   │   ├── layout.tsx          # 根布局（Root Layout）
│   │   ├── page.tsx            # 首页
│   │   ├── auth/               # 认证页面
│   │   │   ├── login/
│   │   │   └── register/
│   │   ├── documents/          # 文档管理
│   │   │   ├── page.tsx        # 文档库
│   │   │   └── [id]/           # 文档详情
│   │   │       ├── page.tsx
│   │   │       └── reader/     # 文档阅读器
│   │   └── chat/               # 对话界面
│   │       └── [sessionId]/
│   ├── components/             # React 组件（Components）
│   │   ├── ui/                 # 基础 UI 组件 (Radix UI)
│   │   ├── document/
│   │   │   ├── DocumentUploader.tsx
│   │   │   ├── DocumentList.tsx
│   │   │   └── DocumentViewer.tsx
│   │   ├── chat/
│   │   │   ├── ChatInterface.tsx
│   │   │   ├── MessageList.tsx
│   │   │   └── MessageInput.tsx
│   │   └── layout/
│   │       ├── Header.tsx
│   │       ├── Sidebar.tsx
│   │       └── Footer.tsx
│   ├── lib/                    # 工具库（Libraries）
│   │   ├── api.ts              # API 客户端（API Client） (Axios)
│   │   ├── auth.ts             # 认证工具
│   │   └── utils.ts            # 通用工具
│   ├── stores/                 # Zustand 状态管理（State Management）
│   │   ├── authStore.ts
│   │   ├── documentStore.ts
│   │   └── chatStore.ts
│   ├── types/                  # TypeScript 类型定义（Type Definitions）
│   │   ├── api.ts
│   │   ├── document.ts
│   │   └── chat.ts
│   └── styles/                 # 全局样式（Global Styles）
│       └── globals.css
├── tests/
│   ├── unit/
│   │   └── components/
│   ├── integration/
│   └── e2e/
│       └── playwright/
├── package.json
└── next.config.js

shared/                         # 共享资源
├── docs/                       # 项目文档
├── docker/                     # Docker 配置文件
└── scripts/                    # 部署脚本
```

**结构决策**:

采用 **Web 应用架构（前后端分离）**，理由：

1. **明确的关注点分离**: 后端专注于 API 和业务逻辑，前端专注于 UI/UX
2. **独立部署**: 前后端可以独立扩展和部署
3. **团队协作**: 前后端开发者可以并行工作
4. **技术栈优化**: 后端 Python 更适合 AI/ML 集成，前端 TypeScript 更适合 UI 开发
5. **符合宪章**: 支持插件化扩展（文档解析器、AI 提供商）

## 复杂度追踪

| 违规项 | 为何需要 | 更简单的替代方案被拒绝的原因 |
|--------|---------|---------------------------|
| AI 提供商紧密耦合 | MVP 阶段需要快速集成 OpenAI/Anthropic API 以验证功能 | 虽然理想情况是完全抽象的插件系统，但 MVP 阶段需要快速迭代。已通过引入抽象层（AIProvider 基类）作为过渡方案，后续版本可以扩展。 |
| 文档解析器硬编码 | 支持 4 种文档格式（PDF/EPUB/DOCX/Markdown）需要专用库 | 每种格式都有独特的结构和复杂性，通用解析器无法满足质量要求。已采用策略模式（Strategy Pattern）设计，每个解析器实现统一接口，便于扩展。 |

**缓解措施**:
- ✅ 引入 `AIProvider` 抽象基类，所有提供商实现统一接口
- ✅ 文档解析器使用工厂模式（Factory Pattern） + 策略模式，支持运行时注册新格式
- ✅ 使用依赖注入（Dependency Injection），便于单元测试时 mock 外部服务
- ✅ Phase 2 研究本地 AI 模型集成（Ollama, llama.cpp）作为云 API 的替代

**审批状态**: ✅ 已批准 - 权衡后认为架构设计的可扩展性已达到可接受水平
