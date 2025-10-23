# API 契约：核心阅读体验 (API Contracts: Core Reading Experience)

**功能特性 (Feature)**: 001-core-reading-experience
**日期 (Date)**: 2025-10-22
**OpenAPI 规范 (Spec)**: [openapi.yaml](./openapi.yaml)

本目录包含核心阅读体验功能的 API 契约定义。

---

## 文件说明 (File Description)

- **openapi.yaml**: OpenAPI 3.1 规范文件，定义所有 REST API 端点
- **README.md**: 本文件，提供 API 设计说明和使用指南

---

## API 设计原则 (API Design Principles)

### 1. RESTful 风格

- 使用标准 HTTP 方法：GET (查询), POST (创建), PUT (更新), DELETE (删除)
- 资源命名使用复数形式：`/documents`, `/chat/sessions`
- 使用 HTTP 状态码表达语义：
  - `2xx`: 成功
  - `4xx`: 客户端错误
  - `5xx`: 服务器错误

### 2. 版本管理 (Version Management)

- API 路径包含版本号：`/api/v1/...`
- 支持多版本并存，向后兼容
- 废弃的 API 通过响应头 `X-API-Deprecated: true` 提示

### 3. 认证和授权 (Authentication & Authorization)

- 使用 JWT Bearer Token 认证
- Token 有效期：
  - access_token: 15 分钟
  - refresh_token: 7 天
- 所有端点（除登录/注册）都需要认证

### 4. 错误处理 (Error Handling)

统一错误响应格式：

```json
{
  "code": "ERROR_CODE",
  "message": "人类可读的错误描述",
  "details": {
    "field": "具体字段",
    "error": "详细错误信息"
  }
}
```

常见错误码 (Common Error Codes)：
- `VALIDATION_ERROR`: 请求参数验证失败
- `UNAUTHORIZED`: 未授权或 Token 无效
- `NOT_FOUND`: 资源不存在
- `RATE_LIMITED`: 请求频率超限
- `DOCUMENT_TOO_LARGE`: 文档文件超过大小限制
- `PROCESSING_FAILED`: 文档处理失败

### 5. 分页策略 (Pagination Strategy)

列表接口统一使用游标分页 (Cursor Pagination)：

**查询参数 (Query Parameters)**:
- `page`: 页码（从 1 开始）
- `page_size`: 每页数量（默认 20，最大 100）

**响应格式 (Response Format)**:
```json
{
  "items": [...],
  "total": 150,
  "page": 1,
  "page_size": 20,
  "has_next": true
}
```

### 6. 速率限制 (Rate Limiting)

**限制规则 (Limit Rules)**:
- 认证端点：10 次/分钟/IP
- 文档上传：5 次/分钟/用户
- AI 相关端点（摘要、问答）：10 次/分钟/用户
- 其他端点：100 次/分钟/用户

**响应头 (Response Headers)**:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 85
X-RateLimit-Reset: 1730022000
```

超限时返回 `429 Too Many Requests`。

---

## API 端点概览 (API Endpoints Overview)

### Authentication（认证）

| 端点 | 方法 | 描述 | 认证 |
|------|------|------|------|
| `/api/v1/auth/register` | POST | 用户注册 | ❌ |
| `/api/v1/auth/login` | POST | 用户登录 | ❌ |
| `/api/v1/auth/refresh` | POST | 刷新 Token | ❌ |
| `/api/v1/auth/logout` | POST | 用户登出 | ✅ |

### Documents（文档管理）

| 端点 | 方法 | 描述 | 认证 |
|------|------|------|------|
| `/api/v1/documents` | POST | 上传文档 | ✅ |
| `/api/v1/documents` | GET | 获取文档列表 | ✅ |
| `/api/v1/documents/{id}` | GET | 获取文档详情 | ✅ |
| `/api/v1/documents/{id}` | DELETE | 删除文档 | ✅ |
| `/api/v1/documents/{id}/summary` | GET | 获取文档摘要 | ✅ |
| `/api/v1/documents/{id}/summary` | POST | 生成文档摘要 | ✅ |
| `/api/v1/documents/{id}/download` | GET | 下载原始文档 | ✅ |

### Chat（对话交互）

| 端点 | 方法 | 描述 | 认证 |
|------|------|------|------|
| `/api/v1/chat/sessions` | POST | 创建对话会话 | ✅ |
| `/api/v1/chat/sessions` | GET | 获取会话列表 | ✅ |
| `/api/v1/chat/sessions/{id}` | GET | 获取会话详情 | ✅ |
| `/api/v1/chat/sessions/{id}` | DELETE | 删除会话 | ✅ |
| `/api/v1/chat/sessions/{id}/messages` | POST | 发送消息 | ✅ |
| `/api/v1/chat/sessions/{id}/messages` | GET | 获取消息历史 | ✅ |

### Users（用户管理）

| 端点 | 方法 | 描述 | 认证 |
|------|------|------|------|
| `/api/v1/users/me` | GET | 获取当前用户信息 | ✅ |
| `/api/v1/users/me` | PUT | 更新用户信息 | ✅ |
| `/api/v1/users/me/stats` | GET | 获取阅读统计 | ✅ |

---

## 核心流程示例 (Core Flow Examples)

### 1. 用户注册和登录 (User Registration & Login)

```bash
# 注册
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!",
    "display_name": "张三"
  }'

# 响应
{
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "display_name": "张三"
  },
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "...",
  "token_type": "bearer"
}

# 登录
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!"
  }'
```

### 2. 上传文档 (Upload Document)

```bash
curl -X POST http://localhost:8000/api/v1/documents \
  -H "Authorization: Bearer {access_token}" \
  -F "file=@document.pdf" \
  -F "title=深入理解计算机系统"

# 响应
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "title": "深入理解计算机系统",
  "file_type": "pdf",
  "processing_status": "processing",
  "uploaded_at": "2025-10-22T10:30:00Z"
}
```

### 3. 生成文档摘要 (Generate Document Summary)

```bash
# 请求生成摘要
curl -X POST http://localhost:8000/api/v1/documents/{document_id}/summary \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "depth": "detailed"
  }'

# 响应（异步任务）
{
  "task_id": "abc123",
  "status": "processing",
  "estimated_time": 10
}

# 10秒后获取摘要
curl -X GET http://localhost:8000/api/v1/documents/{document_id}/summary?depth=detailed \
  -H "Authorization: Bearer {access_token}"

# 响应
{
  "id": "880e8400-e29b-41d4-a716-446655440003",
  "document_id": "660e8400-e29b-41d4-a716-446655440001",
  "abstract": "本书从程序员的视角详细阐述了计算机系统的本质概念...",
  "key_insights": [...],
  "main_concepts": [...]
}
```

### 4. 创建对话并提问 (Create Chat Session & Ask Questions)

```bash
# 创建会话
curl -X POST http://localhost:8000/api/v1/chat/sessions \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": "660e8400-e29b-41d4-a716-446655440001",
    "title": "关于流水线的讨论"
  }'

# 响应
{
  "id": "990e8400-e29b-41d4-a716-446655440004",
  "title": "关于流水线的讨论",
  "created_at": "2025-10-22T11:00:00Z"
}

# 发送消息
curl -X POST http://localhost:8000/api/v1/chat/sessions/{session_id}/messages \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "请解释一下流水线的概念"
  }'

# 响应
{
  "user_message": {
    "id": "aa0e8400-e29b-41d4-a716-446655440005",
    "role": "user",
    "content": "请解释一下流水线的概念",
    "created_at": "2025-10-22T11:00:00Z"
  },
  "assistant_message": {
    "id": "bb0e8400-e29b-41d4-a716-446655440006",
    "role": "assistant",
    "content": "流水线（Pipelining）是一种提高处理器性能的重要技术...",
    "sources": [
      {
        "chunk_id": "770e8400-e29b-41d4-a716-446655440002",
        "page": 256,
        "excerpt": "流水线技术通过重叠执行多条指令的不同阶段..."
      }
    ],
    "created_at": "2025-10-22T11:00:05Z"
  }
}
```

### 5. 查看阅读统计 (View Reading Statistics)

```bash
curl -X GET http://localhost:8000/api/v1/users/me/stats \
  -H "Authorization: Bearer {access_token}"

# 响应
{
  "total_documents": 42,
  "completed_documents": 15,
  "total_reading_time": 86400,
  "total_questions": 128,
  "recent_documents": [...]
}
```

---

## 开发工具 (Development Tools)

### 1. 使用 Swagger UI 查看 API 文档

```bash
# 安装 swagger-ui-watcher
npm install -g swagger-ui-watcher

# 启动文档服务器
swagger-ui-watcher openapi.yaml
```

访问 http://localhost:8080 查看交互式 API 文档。

### 2. 生成 API 客户端代码 (Generate API Client Code)

使用 OpenAPI Generator 生成客户端 SDK：

```bash
# 生成 TypeScript Axios 客户端
openapi-generator-cli generate \
  -i openapi.yaml \
  -g typescript-axios \
  -o ./frontend/src/generated/api

# 生成 Python 客户端
openapi-generator-cli generate \
  -i openapi.yaml \
  -g python \
  -o ./sdk/python
```

### 3. API 测试 (API Testing)

使用 Postman 或 Insomnia 导入 `openapi.yaml` 进行测试。

---

## 变更日志 (Changelog)

### v1.0.0 (2025-10-22)

- ✅ 初始版本
- ✅ 认证端点（注册、登录、刷新、登出）
- ✅ 文档管理端点（上传、列表、详情、删除、下载）
- ✅ 摘要生成端点（生成、获取）
- ✅ 对话交互端点（创建会话、发送消息、获取历史）
- ✅ 用户信息端点（获取、更新、统计）

---

## 后续计划 (Future Plans)

### v1.1.0（计划中）

- 流式响应支持 (SSE - Server-Sent Events)
- WebSocket 实时对话
- 文档批量操作 (Batch Operations)
- 高级搜索和过滤 (Advanced Search & Filtering)

### v2.0.0（未来）

- GraphQL API 支持
- 文档协作功能 (Document Collaboration)
- 第三方集成 (Third-party Integration)（Notion, Evernote）

---

## 联系方式 (Contact)

- 问题反馈 (Issue Tracking)：提交 GitHub Issue
- API 支持 (API Support)：support@readpilot.com
