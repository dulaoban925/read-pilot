# PostgreSQL 安装和配置指南

## 方案选择

ReadPilot 项目需要 PostgreSQL 作为主数据库。您有以下安装方式：

---

## ✅ 方案 A: Homebrew 安装（推荐 - 最简单）

### 1. 安装 PostgreSQL

```bash
# 安装 PostgreSQL 15
brew install postgresql@15

# 等待安装完成（约 2-5 分钟）
```

### 2. 启动 PostgreSQL 服务

```bash
# 启动服务
brew services start postgresql@15

# 验证服务状态
brew services list | grep postgresql
```

### 3. 创建数据库

```bash
# 创建 readpilot 数据库
createdb readpilot

# 测试连接
psql readpilot
```

### 4. 配置连接字符串

```bash
# .env 文件中的配置
DATABASE_URL=postgresql+asyncpg://$(whoami)@localhost:5432/readpilot
```

---

## 🐳 方案 B: Docker 安装（推荐 - 最干净）

### 1. 安装 Docker Desktop

1. 下载 Docker Desktop for Mac: https://www.docker.com/products/docker-desktop
2. 安装并启动 Docker Desktop
3. 等待 Docker 完全启动

### 2. 使用 Docker Compose 启动

```bash
# 在项目根目录
docker-compose up -d postgres

# 查看容器状态
docker-compose ps

# 查看日志
docker-compose logs postgres
```

### 3. 数据库自动创建

Docker Compose 已配置自动创建 `readpilot` 数据库。

### 4. 配置连接字符串

```bash
# .env 文件中的配置（已配置）
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/readpilot
```

---

## 📋 方案 C: 手动安装（不推荐）

如果您不想用 Homebrew 或 Docker，可以：

1. 访问 https://www.postgresql.org/download/macosx/
2. 下载 PostgreSQL 安装包
3. 手动安装和配置

---

## ⚡ 快速开始（当前正在执行）

### 当前状态
✅ 正在通过 Homebrew 安装 PostgreSQL@15...

### 完成后的步骤

1. **启动服务**
   ```bash
   brew services start postgresql@15
   ```

2. **创建数据库**
   ```bash
   createdb readpilot
   ```

3. **安装 Python 依赖**
   ```bash
   cd backend
   source venv/bin/activate
   pip install asyncpg pgvector
   ```

4. **更新 requirements.txt**
   ```bash
   # 已添加到 requirements.txt:
   asyncpg>=0.29.0
   ```

5. **配置环境变量**
   ```bash
   # backend/.env
   DATABASE_URL=postgresql+asyncpg://$(whoami)@localhost:5432/readpilot
   ```

6. **创建数据库表**
   ```bash
   # 方式1: 使用 Alembic 迁移（推荐）
   alembic upgrade head

   # 方式2: 使用 Python 脚本
   python scripts/init_db.py
   ```

7. **重启 Backend**
   ```bash
   cd backend
   python main.py
   ```

---

## 🔍 验证安装

### 检查 PostgreSQL 是否运行

```bash
# 方式 1: 使用 psql
psql -U $(whoami) -d postgres -c "SELECT version();"

# 方式 2: 检查端口
lsof -i :5432

# 方式 3: 检查服务
brew services list | grep postgresql
```

### 测试数据库连接

```bash
# 连接到数据库
psql readpilot

# 在 psql 中执行
\l          -- 列出所有数据库
\dt         -- 列出所有表
\q          -- 退出
```

### 使用 Python 测试连接

```python
# test_connection.py
import asyncio
import asyncpg

async def test_connection():
    conn = await asyncpg.connect(
        host='localhost',
        port=5432,
        user='anker',  # 替换为您的用户名
        database='readpilot'
    )
    version = await conn.fetchval('SELECT version()')
    print(f"Connected to: {version}")
    await conn.close()

asyncio.run(test_connection())
```

---

## 🚨 常见问题

### 1. 端口 5432 已被占用

```bash
# 查找占用端口的进程
lsof -i :5432

# 停止旧的 PostgreSQL 进程
brew services stop postgresql@14  # 如果有旧版本
```

### 2. 无法连接到数据库

```bash
# 检查服务状态
brew services list

# 查看日志
tail -f /usr/local/var/log/postgresql@15.log

# 重启服务
brew services restart postgresql@15
```

### 3. 数据库不存在

```bash
# 创建数据库
createdb readpilot

# 或使用 psql
psql postgres
CREATE DATABASE readpilot;
\q
```

### 4. 权限问题

```bash
# 确保您的用户有权限
psql postgres
ALTER USER $(whoami) CREATEDB;
\q
```

---

## 🎯 下一步

安装完成后：

1. ✅ PostgreSQL 安装
2. ✅ 数据库创建
3. ⏳ 安装 Python 依赖（asyncpg, pgvector）
4. ⏳ 配置环境变量
5. ⏳ 创建数据库表结构
6. ⏳ 启动 Backend 服务

---

## 📚 相关文档

- [PostgreSQL 官方文档](https://www.postgresql.org/docs/)
- [asyncpg 文档](https://magicstack.github.io/asyncpg/)
- [pgvector 文档](https://github.com/pgvector/pgvector)
- [DATABASE_COMPARISON.md](backend/DATABASE_COMPARISON.md) - PostgreSQL vs MySQL 对比
