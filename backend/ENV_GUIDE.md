# 环境配置指南

## 📁 配置文件结构（MVP 阶段）

ReadPilot MVP 阶段只使用**单一开发环境**，配置文件已精简为：

```
backend/
  ├── .env           # 实际使用的配置（不提交到 Git）
  └── .env.example   # 配置模板（提交到 Git）
```

> **为什么只有一个配置文件？**
>
> MVP 阶段专注于核心功能开发，不需要区分开发/测试/生产环境。
> 等产品成熟后再考虑多环境配置。

---

## 🚀 快速开始

### 1. 复制配置模板

```bash
cd backend
cp .env.example .env
```

### 2. 修改必要配置

编辑 `.env` 文件，填入实际值：

```bash
# 数据库配置（替换 YOUR_USERNAME）
DATABASE_URL=postgresql+asyncpg://YOUR_USERNAME@localhost:5432/readpilot

# OpenAI API Key（必填）
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 3. 启动应用

```bash
source venv/bin/activate
python main.py
```

---

## 📝 配置项说明

### 应用配置

| 配置项 | 说明 | 默认值 | 是否必填 |
|--------|------|--------|----------|
| `APP_NAME` | 应用名称 | ReadPilot | 否 |
| `APP_VERSION` | 应用版本 | 0.1.0 | 否 |
| `DEBUG` | 调试模式 | True | 否 |

### API 配置

| 配置项 | 说明 | 默认值 | 是否必填 |
|--------|------|--------|----------|
| `API_V1_PREFIX` | API 前缀 | /api/v1 | 否 |
| `CORS_ORIGINS` | 允许的跨域源 | 见下方 | 否 |

**CORS_ORIGINS 说明：**
```python
# 默认允许的前端地址
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173","http://localhost:8000"]

# 3000: Next.js 默认端口
# 5173: Vite 默认端口
# 8000: FastAPI 自身（用于 Swagger UI）
```

### 数据库配置

| 配置项 | 说明 | 是否必填 |
|--------|------|----------|
| `DATABASE_URL` | 数据库连接字符串 | **是** |

**PostgreSQL（推荐）：**
```bash
DATABASE_URL=postgresql+asyncpg://username@localhost:5432/readpilot
```

**SQLite（仅用于快速测试）：**
```bash
DATABASE_URL=sqlite+aiosqlite:///./readpilot.db
```

> ⚠️ **注意：** SQLite 不支持 pgvector 向量搜索，功能受限。

### LLM 配置

| 配置项 | 说明 | 默认值 | 是否必填 |
|--------|------|--------|----------|
| `OPENAI_API_KEY` | OpenAI API 密钥 | - | **是** |
| `DEFAULT_MODEL` | 默认对话模型 | gpt-4o-mini | 否 |
| `EMBEDDING_MODEL` | 向量化模型 | text-embedding-3-small | 否 |

**模型选择建议：**
- **开发/测试**: `gpt-4o-mini` (快速、便宜)
- **生产环境**: `gpt-4o` (更强大、更准确)
- **嵌入模型**: `text-embedding-3-small` (性价比高)

### 文档处理配置

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `MAX_UPLOAD_SIZE` | 最大上传大小（字节） | 10485760 (10MB) |
| `ALLOWED_FILE_TYPES` | 允许的文件类型 | [".pdf",".txt",".md",".docx"] |
| `CHUNK_SIZE` | 文档分块大小 | 1000 字符 |
| `CHUNK_OVERLAP` | 分块重叠大小 | 200 字符 |

### 对话配置

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `MAX_CONVERSATION_HISTORY` | 最大对话历史条数 | 10 |
| `MAX_CONTEXT_LENGTH` | 最大上下文长度 | 8000 字符 |

### JWT 认证配置

| 配置项 | 说明 | 默认值 | 是否必填 |
|--------|------|--------|----------|
| `SECRET_KEY` | JWT 签名密钥 | - | **是** |
| `ALGORITHM` | 加密算法 | HS256 | 否 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token 过期时间（分钟） | 10080 (7天) | 否 |

> ⚠️ **安全提示：** 生产环境必须使用强随机密钥！

生成安全的 SECRET_KEY：
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## 🔒 安全最佳实践

### 1. .env 文件不要提交到 Git

`.env` 文件包含敏感信息，已在 `.gitignore` 中排除：

```gitignore
# Environment variables
.env
.env.local
.env.*.local
```

### 2. 使用强密钥

```bash
# ❌ 不安全
SECRET_KEY=123456

# ✅ 安全
SECRET_KEY=xK8_h9mP2nR7vT4wY3qZ6jL1cV5bN0aS9dF8gH7iJ6k
```

### 3. 定期轮换 API 密钥

定期更新 OpenAI API Key，特别是在以下情况：
- 密钥可能泄露
- 团队成员离职
- 定期安全审计

### 4. 环境隔离

如果需要测试，可以临时修改 `.env` 中的数据库连接：

```bash
# 开发数据库
DATABASE_URL=postgresql+asyncpg://user@localhost:5432/readpilot

# 测试数据库（临时）
DATABASE_URL=postgresql+asyncpg://user@localhost:5432/readpilot_test
```

---

## 🐛 常见问题

### Q1: 启动时提示缺少环境变量

**错误信息：**
```
ValueError: OPENAI_API_KEY environment variable not set
```

**解决方案：**
1. 确认 `.env` 文件存在于 `backend/` 目录
2. 检查是否正确设置了 `OPENAI_API_KEY`
3. 重启应用使配置生效

### Q2: 数据库连接失败

**错误信息：**
```
asyncpg.exceptions.ConnectionDoesNotExistError
```

**解决方案：**
1. 检查 PostgreSQL 是否运行：
   ```bash
   brew services list | grep postgresql
   ```
2. 确认数据库 `readpilot` 已创建：
   ```bash
   psql -l | grep readpilot
   ```
3. 检查 `DATABASE_URL` 中的用户名是否正确

### Q3: CORS 错误

**错误信息：**
```
Access to fetch at 'http://localhost:8000/api/v1/...' from origin
'http://localhost:3001' has been blocked by CORS policy
```

**解决方案：**

添加前端地址到 `CORS_ORIGINS`：
```bash
CORS_ORIGINS=["http://localhost:3000","http://localhost:3001","http://localhost:5173","http://localhost:8000"]
```

### Q4: 文件上传失败

**错误信息：**
```
413 Request Entity Too Large
```

**解决方案：**

增加 `MAX_UPLOAD_SIZE`（单位：字节）：
```bash
MAX_UPLOAD_SIZE=20971520  # 20MB
```

---

## 📊 配置验证

启动应用后，访问以下端点验证配置：

### 健康检查
```bash
curl http://localhost:8000/health
```

预期响应：
```json
{
  "status": "ok",
  "version": "0.1.0",
  "database": "connected"
}
```

### API 文档
```bash
open http://localhost:8000/docs
```

应该看到完整的 Swagger UI 文档。

---

## 🔄 配置更新

如果 `.env.example` 有更新（新增配置项），按以下步骤同步：

```bash
# 1. 查看差异
diff .env.example .env

# 2. 手动添加新配置项到 .env

# 3. 重启应用
python main.py
```

---

## 📚 相关文档

- [PostgreSQL 安装指南](../POSTGRESQL_SETUP_GUIDE.md)
- [快速开始](../POSTGRESQL_QUICKSTART.md)
- [项目 README](../README.md)

---

**最后更新:** 2025-10-20
**版本:** 0.1.0 (MVP)
