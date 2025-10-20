# PostgreSQL 快速开始指南

> **ReadPilot 项目数据库完整初始化文档**

## 一键初始化（推荐）

```bash
# 在项目根目录执行
chmod +x setup_postgresql.sh
./setup_postgresql.sh
```

这个脚本会自动完成：
- ✅ 检查/安装 PostgreSQL 15
- ✅ 启动 PostgreSQL 服务
- ✅ 安装 Python 依赖 (asyncpg, pgvector)
- ✅ 创建 readpilot 数据库
- ✅ 安装 pgvector 扩展
- ✅ 配置 .env 文件
- ✅ 初始化数据库表
- ✅ 验证安装

---

## 手动设置步骤（可选）

如果您想手动操作，按以下步骤：

### 1. 启动 PostgreSQL 服务

```bash
# 启动服务
brew services start postgresql@15

# 验证服务状态
brew services list | grep postgresql
```

### 2. 创建数据库

```bash
# 创建 readpilot 数据库
createdb readpilot

# 测试连接
psql readpilot
```

### 3. 安装 pgvector 扩展

```bash
# 在 psql 中执行
psql readpilot
CREATE EXTENSION vector;
\q
```

### 4. 更新 .env 配置

```bash
# 编辑 backend/.env
DATABASE_URL=postgresql+asyncpg://$(whoami)@localhost:5432/readpilot
```

### 5. 初始化数据库表

```bash
cd backend
source venv/bin/activate
python scripts/init_db.py
```

### 6. 启动 Backend

```bash
python main.py
```

---

## 验证安装

### 检查 PostgreSQL 状态

```bash
# 查看服务状态
brew services list | grep postgresql

# 查看版本
psql --version

# 查看运行中的进程
ps aux | grep postgres
```

### 连接到数据库

```bash
# 方式 1: 使用 psql
psql readpilot

# 方式 2: 指定完整参数
psql -h localhost -p 5432 -U $(whoami) -d readpilot
```

### 在 psql 中的有用命令

```sql
-- 查看所有数据库
\l

-- 查看所有表
\dt

-- 查看表结构
\d documents

-- 查看已安装的扩展
\dx

-- 退出
\q
```

---

## 为什么选择 PostgreSQL？

### ✅ ReadPilot 项目的核心需求

1. **向量搜索 (Vector Search)**
   - pgvector 扩展原生支持
   - 语义搜索核心功能
   - 15-50ms 查询速度

2. **JSON 数据存储**
   - JSONB 类型，可索引
   - Agent 元数据存储
   - 复杂查询支持

3. **全文搜索**
   - 内置全文搜索
   - 多语言支持
   - 中英文分词

4. **AI 生态**
   - LangChain 官方推荐
   - Supabase (AI 应用首选)
   - 行业标准

### 📊 性能对比

| 功能 | PostgreSQL | MySQL | SQLite |
|------|-----------|-------|--------|
| 向量搜索 | ✅ 原生支持 | ❌ 不支持 | ❌ 不支持 |
| JSON 查询 | ✅ JSONB | ⚠️ 基础 | ⚠️ 基础 |
| 并发性能 | ✅ MVCC | ⚠️ 行锁 | ❌ 文件锁 |
| 扩展性 | ✅ 丰富 | ⚠️ 有限 | ❌ 无 |

详见：[DATABASE_COMPARISON.md](backend/DATABASE_COMPARISON.md)

---

## 数据库结构

### 主要表

```sql
-- 用户表
CREATE TABLE users (
    id TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    username TEXT,
    password_hash TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 文档表
CREATE TABLE documents (
    id TEXT PRIMARY KEY,
    user_id TEXT REFERENCES users(id),
    title TEXT NOT NULL,
    file_name TEXT,
    file_type TEXT,
    summary JSONB,
    processing_status TEXT,
    created_at TIMESTAMP
);

-- 文档块表 (用于向量搜索)
CREATE TABLE document_chunks (
    id TEXT PRIMARY KEY,
    document_id TEXT REFERENCES documents(id),
    text TEXT NOT NULL,
    chunk_index INTEGER,
    embedding vector(1536),  -- OpenAI embeddings
    chunk_metadata JSONB
);

-- 会话表
CREATE TABLE sessions (
    id TEXT PRIMARY KEY,
    user_id TEXT REFERENCES users(id),
    document_id TEXT REFERENCES documents(id),
    session_type TEXT,
    created_at TIMESTAMP
);

-- 消息表
CREATE TABLE messages (
    id TEXT PRIMARY KEY,
    session_id TEXT REFERENCES sessions(id),
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    agent_name TEXT,
    message_metadata JSONB,
    created_at TIMESTAMP
);
```

### 索引策略

```sql
-- 向量搜索索引 (HNSW)
CREATE INDEX ON document_chunks
USING hnsw (embedding vector_cosine_ops);

-- JSON 索引
CREATE INDEX ON documents USING GIN (summary);
CREATE INDEX ON messages USING GIN (message_metadata);

-- 全文搜索索引
CREATE INDEX ON documents
USING GIN (to_tsvector('english', content));
```

---

## 常用操作

### 查看数据

```sql
-- 查看所有文档
SELECT id, title, processing_status FROM documents;

-- 查看文档摘要
SELECT
    title,
    summary->>'type' as doc_type,
    summary->'key_insights' as insights
FROM documents;

-- 向量搜索示例
SELECT
    text,
    1 - (embedding <=> '[0.1,0.2,...]') as similarity
FROM document_chunks
ORDER BY embedding <=> '[0.1,0.2,...]'
LIMIT 10;
```

### 备份和恢复

```bash
# 备份数据库
pg_dump readpilot > readpilot_backup.sql

# 恢复数据库
psql readpilot < readpilot_backup.sql

# 导出为自定义格式（推荐）
pg_dump -Fc readpilot > readpilot_backup.dump

# 从自定义格式恢复
pg_restore -d readpilot readpilot_backup.dump
```

### 性能监控

```sql
-- 查看表大小
SELECT
    tablename,
    pg_size_pretty(pg_total_relation_size(tablename::text)) as size
FROM pg_tables
WHERE schemaname = 'public';

-- 查看索引使用情况
SELECT
    indexrelname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes;

-- 查看慢查询
SELECT
    query,
    calls,
    mean_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
```

---

## 下一步

1. **等待 PostgreSQL 安装完成**
   ```bash
   # 检查安装状态
   brew list | grep postgresql
   ```

2. **运行一键设置脚本**
   ```bash
   ./setup_postgresql.sh
   ```

3. **启动 Backend**
   ```bash
   cd backend
   python main.py
   ```

4. **测试 API**
   ```bash
   # 访问 Swagger UI
   open http://localhost:8000/docs
   ```

---

## 需要帮助？

- 📖 [SETUP_POSTGRESQL.md](SETUP_POSTGRESQL.md) - 详细安装指南
- 📊 [DATABASE_COMPARISON.md](backend/DATABASE_COMPARISON.md) - PostgreSQL vs MySQL
- 🐘 [PostgreSQL 官方文档](https://www.postgresql.org/docs/)
- 🔍 [pgvector 文档](https://github.com/pgvector/pgvector)
