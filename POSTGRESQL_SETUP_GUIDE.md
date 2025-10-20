# PostgreSQL 完整初始化指南

本文档详细记录了ReadPilot项目从零开始安装和配置PostgreSQL数据库的完整流程。

## 目录

1. [环境要求](#环境要求)
2. [PostgreSQL安装](#postgresql安装)
3. [数据库初始化](#数据库初始化)
4. [pgvector扩展安装](#pgvector扩展安装)
5. [后端配置](#后端配置)
6. [验证安装](#验证安装)
7. [常见问题](#常见问题)

---

## 环境要求

- macOS (使用Homebrew) 或 Linux
- Python 3.9+
- pip/virtualenv

---

## PostgreSQL安装

### macOS (Homebrew)

```bash
# 1. 安装PostgreSQL 15
brew install postgresql@15

# 2. 将PostgreSQL添加到PATH (可选但推荐)
echo 'export PATH="/opt/homebrew/opt/postgresql@15/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# 3. 启动PostgreSQL服务
brew services start postgresql@15

# 或者手动启动 (不作为后台服务)
# LC_ALL="en_US.UTF-8" /opt/homebrew/opt/postgresql@15/bin/postgres -D /opt/homebrew/var/postgresql@15
```

### Linux (Ubuntu/Debian)

```bash
# 1. 添加PostgreSQL APT仓库
sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -

# 2. 安装PostgreSQL 15
sudo apt update
sudo apt install -y postgresql-15 postgresql-contrib-15

# 3. 启动服务
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### 验证安装

```bash
# 检查PostgreSQL版本
/opt/homebrew/opt/postgresql@15/bin/postgres --version
# 或 (如果已添加到PATH)
postgres --version

# 检查服务状态
brew services list | grep postgresql  # macOS
# 或
sudo systemctl status postgresql      # Linux
```

---

## 数据库初始化

### 自动化脚本

使用项目提供的自动化脚本（推荐）：

```bash
# 在项目根目录执行
chmod +x setup_postgresql.sh
./setup_postgresql.sh
```

### 手动初始化步骤

如果自动化脚本失败，可以手动执行以下步骤：

#### 1. 创建数据库

```bash
# macOS
/opt/homebrew/opt/postgresql@15/bin/createdb readpilot

# Linux
sudo -u postgres createdb readpilot
```

#### 2. 安装Python依赖

```bash
cd backend
source venv/bin/activate
pip install asyncpg pgvector
```

#### 3. 配置环境变量

编辑 `backend/.env` 文件：

```env
# PostgreSQL连接字符串
DATABASE_URL=postgresql+asyncpg://anker@localhost:5432/readpilot

# 如果是Linux，可能需要指定密码
# DATABASE_URL=postgresql+asyncpg://postgres:yourpassword@localhost:5432/readpilot
```

#### 4. 初始化数据表

**方法1：使用Python脚本（推荐）**

```bash
cd backend
source venv/bin/activate
python scripts/init_db_simple.py
```

**方法2：使用SQL文件**

```bash
# 执行SQL初始化脚本
/opt/homebrew/opt/postgresql@15/bin/psql readpilot < backend/scripts/init_schema.sql
```

---

## pgvector扩展安装

pgvector用于向量相似度搜索，是AI应用的关键组件。

### macOS

```bash
# 1. 安装pgvector
brew install pgvector

# 2. 在数据库中启用扩展
/opt/homebrew/opt/postgresql@15/bin/psql readpilot -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

### Linux

```bash
# 1. 安装pgvector
sudo apt install -y postgresql-15-pgvector

# 2. 在数据库中启用扩展
sudo -u postgres psql readpilot -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

### 验证pgvector

```bash
/opt/homebrew/opt/postgresql@15/bin/psql readpilot -c "SELECT * FROM pg_extension WHERE extname = 'vector';"
```

---

## 后端配置

### 1. 更新requirements.txt

确保以下依赖已添加到 `backend/requirements.txt`：

```txt
# Database
sqlalchemy>=2.0.25
asyncpg>=0.29.0  # PostgreSQL async driver
aiosqlite>=0.19.0  # SQLite async driver (fallback)
alembic>=1.13.1
pgvector>=0.2.5  # Vector similarity search
greenlet>=3.0.0  # Required by SQLAlchemy async
```

### 2. 安装依赖

```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### 3. 启动后端

```bash
cd backend
source venv/bin/activate
python main.py
```

或直接使用：

```bash
backend/venv/bin/python backend/main.py
```

---

## 验证安装

### 1. 检查数据库连接

```bash
# Python快速测试
backend/venv/bin/python -c "
import asyncio
import asyncpg

async def test():
    conn = await asyncpg.connect(
        host='localhost',
        port=5432,
        user='anker',  # 根据实际用户名修改
        database='readpilot'
    )
    print('✅ 数据库连接成功!')
    await conn.close()

asyncio.run(test())
"
```

### 2. 检查数据表

```bash
/opt/homebrew/opt/postgresql@15/bin/psql readpilot -c "\dt"
```

应该看到以下表：
- users
- documents
- document_chunks
- sessions
- messages

### 3. 测试API

启动后端后，访问：

- API文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/health

```bash
curl http://localhost:8000/health
# 预期输出: {"status":"ok"}
```

---

## 常见问题

### Q1: psql命令找不到

**问题**: `command not found: psql`

**解决方案**:

```bash
# 使用完整路径
/opt/homebrew/opt/postgresql@15/bin/psql

# 或添加到PATH
echo 'export PATH="/opt/homebrew/opt/postgresql@15/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### Q2: 数据库连接被拒绝

**问题**: `connection refused` 或 `could not connect to server`

**解决方案**:

```bash
# 检查PostgreSQL是否运行
brew services list | grep postgresql

# 如果未运行，启动服务
brew services start postgresql@15

# 检查端口是否被占用
lsof -i :5432
```

### Q3: 权限错误

**问题**: `permission denied` 或 `role does not exist`

**解决方案**:

```bash
# 创建当前用户为PostgreSQL用户
/opt/homebrew/opt/postgresql@15/bin/createuser -s $(whoami)

# 或使用postgres超级用户
sudo -u postgres createdb readpilot
sudo -u postgres psql readpilot
```

### Q4: pgvector扩展不可用

**问题**: `extension "vector" is not available`

**解决方案**:

```bash
# 确保已安装pgvector
brew install pgvector  # macOS
# 或
sudo apt install postgresql-15-pgvector  # Linux

# 重启PostgreSQL
brew services restart postgresql@15
```

### Q5: Foreign Key约束错误

**问题**: 表创建时出现外键引用错误

**解决方案**:

确保按正确顺序创建表：
1. users (无外键依赖)
2. documents (依赖users)
3. document_chunks (依赖documents)
4. sessions (依赖users)
5. messages (依赖sessions)

使用提供的 `init_db_simple.py` 脚本会自动处理这个顺序。

### Q6: SQLAlchemy metadata错误

**问题**: `Attribute name 'metadata' is reserved`

**解决方案**:

在模型中将 `metadata` 字段重命名为 `chunk_metadata` 或 `message_metadata`。
已在项目中修复。

---

## 数据库维护

### 备份数据库

```bash
# 备份整个数据库
/opt/homebrew/opt/postgresql@15/bin/pg_dump readpilot > backup_$(date +%Y%m%d).sql

# 仅备份schema
/opt/homebrew/opt/postgresql@15/bin/pg_dump --schema-only readpilot > schema.sql

# 仅备份数据
/opt/homebrew/opt/postgresql@15/bin/pg_dump --data-only readpilot > data.sql
```

### 恢复数据库

```bash
# 从备份恢复
/opt/homebrew/opt/postgresql@15/bin/psql readpilot < backup_20251020.sql
```

### 重置数据库

```bash
# 删除所有表并重新初始化
/opt/homebrew/opt/postgresql@15/bin/psql readpilot -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"

# 重新运行初始化脚本
cd backend
source venv/bin/activate
python scripts/init_db_simple.py
```

---

## Docker部署 (可选)

如果希望使用Docker部署PostgreSQL：

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: pgvector/pgvector:pg15
    container_name: readpilot-postgres
    environment:
      POSTGRES_DB: readpilot
      POSTGRES_USER: readpilot
      POSTGRES_PASSWORD: your_secure_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backend/scripts/init_schema.sql:/docker-entrypoint-initdb.d/init.sql

volumes:
  postgres_data:
```

启动Docker PostgreSQL：

```bash
docker-compose up -d postgres
```

更新 `backend/.env`：

```env
DATABASE_URL=postgresql+asyncpg://readpilot:your_secure_password@localhost:5432/readpilot
```

---

## 性能优化建议

### 1. 连接池配置

在 `backend/database.py` 中调整连接池参数：

```python
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    pool_size=10,          # 连接池大小
    max_overflow=20,       # 最大溢出连接数
    pool_pre_ping=True,    # 连接前ping测试
    pool_recycle=3600      # 连接回收时间(秒)
)
```

### 2. 索引优化

```sql
-- 为常用查询字段添加索引
CREATE INDEX idx_documents_user_id ON documents(user_id);
CREATE INDEX idx_document_chunks_document_id ON document_chunks(document_id);
CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_messages_session_id ON messages(session_id);

-- 向量搜索索引 (需要pgvector)
CREATE INDEX idx_document_chunks_embedding ON document_chunks
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

### 3. 查询优化

```sql
-- 分析表统计信息
ANALYZE users;
ANALYZE documents;
ANALYZE document_chunks;
ANALYZE sessions;
ANALYZE messages;

-- 查看查询计划
EXPLAIN ANALYZE SELECT * FROM documents WHERE user_id = 'xxx';
```

---

## 总结

PostgreSQL已完全配置完成，支持：

✅ PostgreSQL 15.14
✅ 异步连接 (asyncpg)
✅ pgvector向量搜索扩展
✅ 完整的数据库schema
✅ 自动化初始化脚本
✅ Docker部署选项

如需进一步帮助，请参考：
- [PostgreSQL官方文档](https://www.postgresql.org/docs/15/)
- [pgvector文档](https://github.com/pgvector/pgvector)
- [SQLAlchemy异步文档](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
