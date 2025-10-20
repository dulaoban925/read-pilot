# PostgreSQL 数据库文档索引

本目录包含ReadPilot项目PostgreSQL数据库的完整文档和脚本。

## 📚 文档结构

### 1. 快速开始

**[POSTGRESQL_QUICKSTART.md](../POSTGRESQL_QUICKSTART.md)** - 快速参考指南
- ⚡ 一键初始化命令
- 📝 常用命令速查
- 🔧 快速故障排查
- 适合：已经熟悉PostgreSQL，需要快速参考

### 2. 完整指南

**[POSTGRESQL_SETUP_GUIDE.md](../POSTGRESQL_SETUP_GUIDE.md)** - 完整安装配置指南
- 📖 详细的安装步骤
- 🛠️ macOS 和 Linux 支持
- ⚙️ 配置说明
- 🐛 完整的问题排查
- 📊 性能优化建议
- 🐳 Docker部署方案
- 适合：首次安装或需要深入理解

### 3. 数据库对比

**[DATABASE_COMPARISON.md](../backend/DATABASE_COMPARISON.md)** - PostgreSQL vs MySQL 对比分析
- 📊 详细性能对比
- 💡 功能对比
- 🎯 为什么选择PostgreSQL
- 📈 性能测试数据
- 适合：了解技术选型决策

## 🚀 快速开始

### 一键安装（推荐）

```bash
# 在项目根目录执行
chmod +x setup_postgresql.sh
./setup_postgresql.sh
```

### 查看安装状态

```bash
# 检查服务
brew services list | grep postgresql  # macOS
sudo systemctl status postgresql      # Linux

# 测试连接
psql readpilot -c "SELECT version();"

# 查看表
psql readpilot -c "\dt"
```

### 启动后端

```bash
cd backend
source venv/bin/activate
python main.py
```

访问: http://localhost:8000/docs

## 📁 脚本文件

### 自动化脚本

**[setup_postgresql.sh](../setup_postgresql.sh)** - 完整自动化安装脚本
- 支持 macOS 和 Linux
- 自动检测并安装 PostgreSQL
- 自动配置数据库和表
- 包含完整验证

### 数据库初始化

**SQL方式:**
- [init_schema.sql](../backend/scripts/init_schema.sql) - SQL初始化脚本
- 包含所有表、索引、触发器
- 支持 pgvector 扩展
- 可独立执行

**Python方式:**
- [init_db_simple.py](../backend/scripts/init_db_simple.py) - Python初始化脚本
- 使用 asyncpg 直接创建
- 按正确顺序处理外键依赖
- 包含错误处理

## 🗄️ 数据库结构

### 核心表

| 表名 | 说明 | 关键特性 |
|------|------|----------|
| **users** | 用户账户 | UUID主键, 邮箱唯一 |
| **documents** | 文档存储 | 关联用户, 文件元数据 |
| **document_chunks** | 文档分块 | 向量embeddings, 语义搜索 |
| **sessions** | 对话会话 | 关联用户, 会话历史 |
| **messages** | 聊天消息 | 关联会话, JSONB元数据 |

### 关系图

```
users (用户)
  ├── documents (文档)
  │     └── document_chunks (分块 + 向量)
  └── sessions (会话)
        └── messages (消息)
```

### 核心功能

1. **向量搜索** - pgvector扩展
   - 语义相似度搜索
   - 支持1536维OpenAI embeddings
   - HNSW/IVFFlat索引

2. **JSONB存储** - 灵活的元数据
   - 文档摘要和分析结果
   - Agent执行元数据
   - 可索引和查询

3. **全文搜索** - 内置FTS
   - 中英文分词
   - 相关度排序
   - GIN索引加速

## 🔧 常用命令

### 服务管理

```bash
# 启动/停止/重启
brew services start postgresql@15    # macOS
sudo systemctl start postgresql      # Linux

# 查看状态
brew services list                    # macOS
sudo systemctl status postgresql     # Linux
```

### 数据库操作

```bash
# 连接数据库
psql readpilot

# 备份
pg_dump readpilot > backup.sql

# 恢复
psql readpilot < backup.sql

# 查看表
psql readpilot -c "\dt"

# 查看扩展
psql readpilot -c "\dx"
```

### Python测试

```bash
# 测试连接
backend/venv/bin/python -c "
import asyncio
import asyncpg

async def test():
    conn = await asyncpg.connect('postgresql://localhost/readpilot')
    print('✅ 连接成功')
    await conn.close()

asyncio.run(test())
"
```

## 🐛 故障排查

### 常见问题

| 问题 | 解决方案 |
|------|----------|
| psql命令找不到 | 添加到PATH: `export PATH="/opt/homebrew/opt/postgresql@15/bin:$PATH"` |
| 连接被拒绝 | 启动服务: `brew services start postgresql@15` |
| pgvector不可用 | 安装: `brew install pgvector` 然后 `psql -c "CREATE EXTENSION vector;"` |
| 权限错误 | 创建用户: `createuser -s $(whoami)` |

详细排查步骤请参考 [POSTGRESQL_SETUP_GUIDE.md](../POSTGRESQL_SETUP_GUIDE.md#常见问题)

## 📊 性能优化

### 连接池配置

```python
# backend/database.py
engine = create_async_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True
)
```

### 索引策略

```sql
-- 向量搜索索引
CREATE INDEX ON document_chunks
USING hnsw (embedding vector_cosine_ops);

-- JSON索引
CREATE INDEX ON documents USING GIN (summary);

-- 全文搜索
CREATE INDEX ON documents
USING GIN (to_tsvector('english', content));
```

### 查询优化

```sql
-- 分析表
ANALYZE documents;

-- 查看查询计划
EXPLAIN ANALYZE SELECT ...;

-- 监控慢查询
SELECT query, mean_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC;
```

## 🐳 Docker 部署

```yaml
# docker-compose.yml
services:
  postgres:
    image: pgvector/pgvector:pg15
    environment:
      POSTGRES_DB: readpilot
      POSTGRES_USER: readpilot
      POSTGRES_PASSWORD: secure_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
```

```bash
docker-compose up -d postgres
```

## 📈 监控与维护

### 数据库大小

```sql
SELECT pg_size_pretty(pg_database_size('readpilot'));
```

### 表大小

```sql
SELECT
    tablename,
    pg_size_pretty(pg_total_relation_size(tablename::text))
FROM pg_tables
WHERE schemaname = 'public';
```

### 活动连接

```sql
SELECT * FROM pg_stat_activity;
```

### 定期维护

```sql
-- 清理和分析
VACUUM ANALYZE;

-- 重建索引
REINDEX DATABASE readpilot;
```

## 🔗 相关资源

### 官方文档
- [PostgreSQL 15 文档](https://www.postgresql.org/docs/15/)
- [pgvector GitHub](https://github.com/pgvector/pgvector)
- [asyncpg 文档](https://magicstack.github.io/asyncpg/)

### 项目文档
- [完整安装指南](../POSTGRESQL_SETUP_GUIDE.md)
- [快速开始](../POSTGRESQL_QUICKSTART.md)
- [数据库对比](../backend/DATABASE_COMPARISON.md)

### 初始化脚本
- [自动化脚本](../setup_postgresql.sh)
- [SQL脚本](../backend/scripts/init_schema.sql)
- [Python脚本](../backend/scripts/init_db_simple.py)

## ✅ 验证清单

安装完成后，确认以下项目：

- [ ] PostgreSQL服务运行中
- [ ] readpilot数据库已创建
- [ ] pgvector扩展已启用
- [ ] 5个核心表已创建（users, documents, document_chunks, sessions, messages）
- [ ] 索引已创建
- [ ] Python可以连接数据库
- [ ] 后端服务可以启动
- [ ] API文档可以访问 (http://localhost:8000/docs)

## 📞 支持

遇到问题？

1. 查看 [故障排查部分](#-故障排查)
2. 参考 [完整指南](../POSTGRESQL_SETUP_GUIDE.md#常见问题)
3. 检查后端日志: `backend/logs/`
4. 测试数据库连接: `psql readpilot`

---

**最后更新:** 2025-10-20
**PostgreSQL版本:** 15.14
**项目:** ReadPilot AI Reading Companion
