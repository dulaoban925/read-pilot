# 快速启动指南：核心阅读体验 (Quickstart: Core Reading Experience)

**功能特性 (Feature)**: 001-core-reading-experience
**日期 (Date)**: 2025-10-22
**目标受众 (Target Audience)**: 开发者、测试人员

本文档提供核心阅读体验功能的快速启动指南，包括环境搭建、运行步骤和测试场景。

---

## 目标

完成本指南后，你将能够：

✅ 在本地运行完整的 ReadPilot 系统（前端 + 后端）
✅ 注册用户并上传文档
✅ 生成文档摘要
✅ 与 AI 进行文档问答
✅ 执行自动化测试验证功能

---

## 前置要求 (Prerequisites)

### 系统要求 (System Requirements)

- **操作系统 (Operating System)**: macOS, Linux, Windows (WSL2)
- **内存 (Memory)**: 至少 8GB RAM
- **磁盘空间 (Disk Space)**: 至少 5GB 可用空间

### 软件依赖 (Software Dependencies)

| 软件 | 版本 | 安装命令 |
|------|------|---------|
| Python | 3.12+ | `brew install python@3.12` (macOS) |
| Node.js | 22 LTS | `nvm install 22` |
| Docker | 24+ | [下载 Docker Desktop](https://www.docker.com/products/docker-desktop/) |
| pnpm | 9+ | `npm install -g pnpm` |
| Poetry | 1.8+ | `curl -sSL https://install.python-poetry.org \| python3 -` |

### API 密钥 (API Keys)

本项目需要以下 API 密钥（至少一个）：

- **OpenAI API Key**: [获取地址](https://platform.openai.com/api-keys)
- **Anthropic API Key** (可选): [获取地址](https://console.anthropic.com/)

---

## 快速启动（Docker Compose）

### 1. 克隆仓库 (Clone Repository)

```bash
git clone https://github.com/readpilot/readpilot.git
cd readpilot
git checkout 001-core-reading-experience
```

### 2. 配置环境变量 (Configure Environment Variables)

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的 API 密钥：

```bash
# AI Provider
OPENAI_API_KEY=sk-xxxxx
# ANTHROPIC_API_KEY=sk-ant-xxxxx  # 可选

# Database
DATABASE_URL=postgresql://readpilot:password@localhost:5432/readpilot

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT Secret
SECRET_KEY=your-super-secret-key-change-me-in-production

# Application
DEBUG=true
ENVIRONMENT=development
```

### 3. 启动所有服务 (Start All Services)

```bash
docker-compose up -d
```

这将启动：
- PostgreSQL (端口 5432)
- Redis (端口 6379)
- ChromaDB (端口 8001)
- 后端 API (端口 8000)
- 前端应用 (端口 3000)
- Celery Worker
- Flower (Celery 监控，端口 5555)

### 4. 验证服务状态 (Verify Service Status)

```bash
# 检查所有容器运行状态
docker-compose ps

# 查看后端日志
docker-compose logs -f backend

# 查看前端日志
docker-compose logs -f frontend
```

### 5. 访问应用 (Access Application)

- **前端应用**: http://localhost:3000
- **后端 API 文档**: http://localhost:8000/docs
- **Flower 监控**: http://localhost:5555

---

## 手动启动（适合开发）

### 后端设置 (Backend Setup)

#### 1. 安装 Python 依赖

```bash
cd backend
poetry install
```

#### 2. 启动依赖服务

```bash
# 仅启动数据库和缓存
docker-compose up -d postgres redis chromadb
```

#### 3. 初始化数据库 (Initialize Database)

```bash
# 运行迁移
poetry run alembic upgrade head

# 创建测试用户（可选）
poetry run python scripts/create_test_user.py
```

#### 4. 启动后端服务 (Start Backend Service)

```bash
# 开发模式（热重载）
poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# 生产模式
poetry run gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

#### 5. 启动 Celery Worker

```bash
# 新终端
cd backend
poetry run celery -A src.tasks.celery_app worker --loglevel=info
```

### 前端设置 (Frontend Setup)

#### 1. 安装 Node.js 依赖

```bash
cd frontend
pnpm install
```

#### 2. 配置环境变量

```bash
cp .env.local.example .env.local
```

编辑 `.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_ENVIRONMENT=development
```

#### 3. 启动前端服务 (Start Frontend Service)

```bash
# 开发模式
pnpm dev

# 生产构建
pnpm build
pnpm start
```

---

## 核心功能测试场景 (Core Feature Test Scenarios)

### 场景 1：用户注册和登录 (User Registration & Login)

**目标**: 验证用户认证功能

#### 步骤 1: 注册新用户 (Register New User)

1. 访问 http://localhost:3000/auth/register
2. 填写表单：
   - 邮箱: `test@example.com`
   - 密码: `SecurePass123!`
   - 显示名称: `测试用户`
3. 点击"注册"按钮
4. **预期结果 (Expected Result)**: 自动跳转到首页，显示用户名

#### 步骤 2: 登出并重新登录 (Logout & Re-login)

1. 点击右上角用户头像，选择"登出"
2. 访问 http://localhost:3000/auth/login
3. 输入邮箱和密码
4. **预期结果**: 成功登录并跳转到首页

**通过标准 (Pass Criteria)**:
- ✅ 注册后自动登录
- ✅ 登出后无法访问受保护页面
- ✅ 使用错误密码登录时显示错误提示

---

### 场景 2：文档上传和处理 (Document Upload & Processing)

**目标**: 验证文档上传和文本提取功能

#### 准备测试文件 (Prepare Test Files)

下载测试文档（或使用你自己的文档）：

```bash
# 下载示例 PDF
curl -o test-document.pdf https://example.com/sample.pdf
```

#### 步骤 1: 上传文档 (Upload Document)

1. 登录后访问首页
2. 点击"上传文档"按钮
3. 选择 `test-document.pdf`（确保 < 50MB, < 1000 页）
4. **预期结果 (Expected Result)**:
   - 显示上传进度条
   - 上传完成后文档出现在文档列表中
   - 状态显示为"处理中"（processing）

#### 步骤 2: 监控处理进度 (Monitor Processing Progress)

1. 刷新页面或等待自动更新
2. **预期结果**:
   - 30 秒内（100 页 PDF）状态变为"已完成"（completed）
   - 文档元数据正确显示（页数、字数）

#### 步骤 3: 查看文档详情 (View Document Details)

1. 点击文档标题进入详情页
2. **预期结果**:
   - 显示文档元数据
   - 可以预览文档内容
   - 显示"生成摘要"和"开始问答"按钮

**通过标准 (Pass Criteria)**:
- ✅ 文档上传成功率 > 95%
- ✅ 100 页 PDF 处理时间 < 30 秒
- ✅ 文档列表正确显示处理状态
- ✅ 上传大文件（> 50MB）时显示错误提示

---

### 场景 3：生成文档摘要 (Generate Document Summary)

**目标**: 验证 AI 摘要生成功能

#### 步骤 1: 请求生成摘要 (Request Summary Generation)

1. 在文档详情页点击"生成摘要"按钮
2. 选择摘要深度：
   - Brief（简要）
   - Detailed（详细）
3. **预期结果**:
   - 显示加载动画
   - 10 页文档约 10 秒后生成完成

#### 步骤 2: 查看摘要结果 (View Summary Results)

1. 摘要生成完成后自动显示
2. **预期结果**:
   - 显示三个部分：
     - 摘要概述（Abstract）
     - 关键见解（Key Insights）：3-10 条
     - 主要概念（Main Concepts）：3-15 条
   - 文字流畅，符合文档类型
   - 包含来源信息（使用的 AI 模型）

#### 步骤 3: 缓存验证 (Cache Verification)

1. 再次点击"生成摘要"按钮
2. **预期结果**:
   - 立即显示之前生成的摘要（缓存命中 Cache Hit）
   - 不消耗额外的 AI API 调用

**通过标准 (Pass Criteria)**:
- ✅ 10 页文档摘要生成时间 < 10 秒
- ✅ 摘要质量：包含关键信息，无明显错误
- ✅ 缓存命中率 > 90%（相同文档重复请求）
- ✅ AI 服务不可用时显示友好错误提示

---

### 场景 4：文档问答 (Document Q&A)

**目标**: 验证上下文感知的 AI 问答功能

#### 步骤 1: 创建对话会话 (Create Chat Session)

1. 在文档详情页点击"开始问答"按钮
2. **预期结果**:
   - 跳转到对话界面
   - 显示对话输入框和空白的消息历史

#### 步骤 2: 提问并获取回答 (Ask Question & Get Answer)

1. 在输入框输入问题：`这篇文档的主要内容是什么？`
2. 点击发送按钮
3. **预期结果**:
   - 用户消息立即显示
   - AI 回复在 5 秒内出现
   - 回复包含来源引用（页码和摘录）

#### 步骤 3: 后续提问 (Follow-up Questions)

1. 输入后续问题：`能详细解释一下第三章的内容吗？`
2. **预期结果**:
   - AI 理解上下文 (Context-aware)，不需要重复说明
   - 回复针对第三章内容
   - 包含准确的来源引用

#### 步骤 4: 查看对话历史 (View Chat History)

1. 刷新页面
2. **预期结果**:
   - 对话历史完整保留
   - 消息顺序正确
   - 来源引用链接有效

**通过标准 (Pass Criteria)**:
- ✅ 回答生成时间 < 5 秒
- ✅ 85% 的回答包含准确的来源引用
- ✅ AI 能理解上下文，支持多轮对话
- ✅ 对话历史持久化，刷新页面后不丢失
- ✅ 当文档内容不包含答案时，AI 诚实回应"无法找到相关信息"

---

### 场景 5：阅读历史跟踪 (Reading History Tracking)

**目标**: 验证阅读进度和统计功能

#### 步骤 1: 阅读文档 (Read Document)

1. 在文档详情页浏览文档内容
2. 滚动页面，模拟阅读
3. 停留至少 1 分钟

#### 步骤 2: 查看统计 (View Statistics)

1. 点击用户头像，选择"阅读统计"
2. **预期结果**:
   - 显示总文档数
   - 显示已完成文档数
   - 显示总阅读时长
   - 显示最近阅读的文档列表

**通过标准 (Pass Criteria)**:
- ✅ 阅读时长准确记录（误差 < 5%）
- ✅ 阅读进度正确计算
- ✅ 统计数据实时更新

---

## 自动化测试 (Automated Testing)

### 运行单元测试 (Run Unit Tests)

```bash
# 后端单元测试
cd backend
poetry run pytest tests/unit -v --cov=src

# 前端单元测试
cd frontend
pnpm test
```

### 运行集成测试 (Run Integration Tests)

```bash
# 后端集成测试
cd backend
poetry run pytest tests/integration -v

# 前端集成测试
cd frontend
pnpm test:integration
```

### 运行 E2E 测试 (Run E2E Tests)

```bash
# 确保前后端都在运行
cd frontend
pnpm test:e2e

# 查看测试报告
pnpm playwright show-report
```

**E2E 测试覆盖 (E2E Test Coverage)**:
- ✅ 用户注册和登录流程
- ✅ 文档上传和处理流程
- ✅ 摘要生成流程
- ✅ 对话问答流程

---

## 性能基准测试 (Performance Benchmarking)

### 文档处理性能 (Document Processing Performance)

```bash
cd backend
poetry run python scripts/benchmark_document_processing.py
```

**目标指标 (Target Metrics)**:
- 10MB PDF 上传: < 5 秒
- 100 页 PDF 文本提取: < 30 秒
- 1000 个 chunk 向量化: < 60 秒

### API 响应时间 (API Response Time)

```bash
# 使用 Apache Bench 测试
ab -n 1000 -c 10 http://localhost:8000/api/v1/documents
```

**目标指标**:
- p95 < 3 秒
- p99 < 5 秒
- 1000 并发用户时响应时间不显著增加

---

## 故障排查 (Troubleshooting)

### 问题 1: 数据库连接失败 (Database Connection Failed)

**错误信息**: `Could not connect to PostgreSQL`

**解决方法**:
```bash
# 检查 PostgreSQL 是否运行
docker-compose ps postgres

# 重启 PostgreSQL
docker-compose restart postgres

# 检查连接
psql -h localhost -U readpilot -d readpilot
```

### 问题 2: 文档处理失败 (Document Processing Failed)

**错误信息**: `Document processing failed`

**解决方法**:
```bash
# 查看 Celery 日志
docker-compose logs celery

# 检查 Celery worker 状态
docker-compose ps celery

# 重启 worker
docker-compose restart celery
```

### 问题 3: AI API 调用失败 (AI API Call Failed)

**错误信息**: `OpenAI API key invalid`

**解决方法**:
1. 验证 API 密钥是否正确
2. 检查 API 额度是否用尽
3. 确认网络可以访问 OpenAI API

```bash
# 测试 API 连接
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

### 问题 4: 前端无法连接后端 (Frontend Cannot Connect to Backend)

**错误信息**: `Network Error` 或 `CORS Error`

**解决方法**:
1. 检查后端是否运行：`curl http://localhost:8000/health`
2. 确认 `.env.local` 中 API URL 正确
3. 检查浏览器控制台是否有 CORS 错误

---

## 清理和重置 (Cleanup & Reset)

### 清理所有数据 (Clean All Data)

```bash
# 停止所有服务
docker-compose down

# 删除数据卷（警告：会删除所有数据）
docker-compose down -v

# 重新启动
docker-compose up -d
```

### 重置数据库 (Reset Database)

```bash
cd backend
poetry run alembic downgrade base
poetry run alembic upgrade head
```

---

## 下一步 (Next Steps)

完成 Quickstart 后，你可以：

1. **查看详细文档 (View Detailed Documentation)**:
   - [data-model.md](./data-model.md) - 数据模型设计
   - [contracts/README.md](./contracts/README.md) - API 文档
   - [research.md](./research.md) - 技术选型说明

2. **开始实现 (Start Implementation)**:
   - 运行 `/speckit.tasks` 生成任务列表
   - 按优先级实现用户故事（P1 → P2 → P3）

3. **贡献代码 (Contribute Code)**:
   - 阅读 [CONTRIBUTING.md](../../CONTRIBUTING.md)
   - 提交 Pull Request

---

## 反馈 (Feedback)

遇到问题或有改进建议？

- GitHub Issues: https://github.com/readpilot/readpilot/issues
- 技术支持: dev@readpilot.com
