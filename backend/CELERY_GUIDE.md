# Celery 任务队列配置指南

本指南说明如何配置和运行 Celery 任务队列,用于处理文档上传后的异步处理任务。

---

## 📋 目录

- [为什么需要 Celery](#为什么需要-celery)
- [快速开始](#快速开始)
- [详细配置](#详细配置)
- [常见问题](#常见问题)
- [监控和调试](#监控和调试)

---

## 为什么需要 Celery

ReadPilot 使用 Celery 处理以下**耗时的异步任务**:

1. **文档处理** (`process_document_task`)
   - 解析文档 (PDF/EPUB/DOCX/Markdown)
   - 文本分块 (500-1000 tokens)
   - 提取元数据 (页数、字数、作者等)

2. **向量化索引** (`generate_embeddings_task`)
   - 调用 OpenAI API 生成 embeddings
   - 存储到 ChromaDB 向量数据库
   - 更新文档索引状态

3. **摘要生成** (`generate_summary_task`)
   - 调用 AI 服务生成文档摘要
   - 缓存摘要结果

**如果不启动 Celery Worker,文档会一直停留在 `pending` 状态!**

---

## 快速开始

### 1️⃣ 启动 Redis

Celery 依赖 Redis 作为消息队列。

**macOS** (使用 Homebrew):
```bash
# 安装 Redis (如果未安装)
brew install redis

# 启动 Redis 服务
brew services start redis

# 或临时启动 (终端关闭后停止)
redis-server
```

**Linux**:
```bash
# Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis

# CentOS/RHEL
sudo yum install redis
sudo systemctl start redis
```

**Docker**:
```bash
# 使用 docker-compose 启动
docker-compose up -d redis

# 或单独启动 Redis 容器
docker run -d -p 6379:6379 redis:7-alpine
```

**验证 Redis 是否运行**:
```bash
redis-cli ping
# 应该返回: PONG
```

---

### 2️⃣ 配置环境变量

确保 `.env` 文件中配置了正确的 Redis 连接:

```bash
# backend/.env
REDIS_URL=redis://localhost:6379/0
```

---

### 3️⃣ 启动 Celery Worker

**方式 1: 使用 Makefile (推荐)**
```bash
cd backend
make celery
```

**方式 2: 使用启动脚本**
```bash
cd backend
./start_celery.sh
```

**方式 3: 直接运行命令**
```bash
cd backend
poetry run celery -A app.tasks.celery_app worker --loglevel=info
```

**成功启动后,你会看到类似输出**:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀 启动 ReadPilot Celery Worker
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Redis 连接正常

[tasks]
  . process_document
  . generate_embeddings
  . generate_summary

[2025-10-23 15:30:00,000: INFO/MainProcess] Connected to redis://localhost:6379/0
[2025-10-23 15:30:00,000: INFO/MainProcess] celery@hostname ready.
```

---

## 详细配置

### Celery 配置参数

配置文件位置: [`app/tasks/celery_app.py`](app/tasks/celery_app.py)

```python
celery_app.conf.update(
    task_serializer="json",           # 使用 JSON 序列化
    accept_content=["json"],          # 只接受 JSON
    result_serializer="json",
    timezone="Asia/Shanghai",         # 时区
    enable_utc=True,
    task_track_started=True,          # 跟踪任务启动状态
    task_time_limit=30 * 60,          # 30分钟硬超时
    task_soft_time_limit=25 * 60,     # 25分钟软超时
    worker_prefetch_multiplier=1,     # 每次预取1个任务
    worker_max_tasks_per_child=1000,  # 每个worker处理1000任务后重启
)
```

### 任务定义

#### 1. 文档处理任务

**位置**: [`app/tasks/document_processing.py`](app/tasks/document_processing.py)

```python
@celery_app.task(name="process_document", bind=True)
def process_document_task(self, document_id: str):
    """
    处理文档: 解析、分块、保存
    触发时机: 文档上传成功后立即触发
    """
```

**处理流程**:
```
pending → processing → completed → [触发 embedding]
             ↓
           failed
```

#### 2. Embedding 生成任务

**位置**: [`app/tasks/embedding_tasks.py`](app/tasks/embedding_tasks.py)

```python
@celery_app.task(name="generate_embeddings", bind=True)
def generate_embeddings_task(self, document_id: str):
    """
    生成向量嵌入并存入 ChromaDB
    触发时机: 文档处理完成后自动触发
    """
```

#### 3. 摘要生成任务

**位置**: [`app/tasks/document_processing.py`](app/tasks/document_processing.py)

```python
@celery_app.task(name="generate_summary", bind=True)
def generate_summary_task(self, document_id: str, depth: str = "detailed"):
    """
    生成文档摘要
    触发时机: 用户点击"生成摘要"按钮
    """
```

---

## 监控和调试

### 查看任务状态

**1. 使用 Flower 监控面板** (推荐)

Flower 提供 Web UI 监控 Celery 任务:

```bash
# 启动 Flower
make celery-flower

# 访问 http://localhost:5555
```

**2. 使用命令行工具**

```bash
# 查看活跃任务
make celery-inspect

# 查看 worker 统计
make celery-stats

# 清空任务队列
make celery-purge
```

### 查看日志

Celery Worker 日志会显示任务执行情况:

```
[2025-10-23 15:35:10,123: INFO/MainProcess] Task process_document[abc-123] received
[2025-10-23 15:35:15,456: INFO/ForkPoolWorker-1] Task process_document[abc-123] succeeded in 5.3s
[2025-10-23 15:35:16,789: INFO/MainProcess] Task generate_embeddings[def-456] received
```

### Redis 监控

```bash
# 连接 Redis CLI
redis-cli

# 查看队列长度
LLEN celery

# 查看所有 key
KEYS *

# 查看任务结果
GET celery-task-meta-<task_id>
```

---

## 常见问题

### ❓ 文档状态一直是 `pending`

**原因**: Celery Worker 未启动

**解决**:
```bash
# 1. 检查 Redis 是否运行
redis-cli ping

# 2. 启动 Celery Worker
cd backend
make celery
```

---

### ❓ 任务失败,提示 Redis 连接错误

**错误信息**:
```
[ERROR] Error connecting to Redis: Connection refused
```

**解决**:
```bash
# 1. 检查 Redis 是否运行
brew services list | grep redis
# 或
sudo systemctl status redis

# 2. 检查 .env 配置
cat .env | grep REDIS_URL

# 3. 启动 Redis
brew services start redis  # macOS
sudo systemctl start redis  # Linux
```

---

### ❓ 任务超时

**错误信息**:
```
TimeLimitExceeded: Task exceeded time limit (30m)
```

**原因**: 文档太大或网络延迟导致处理超时

**解决**:
1. 增加超时限制 (修改 `celery_app.py`):
   ```python
   task_time_limit=60 * 60,  # 改为 60 分钟
   ```

2. 分割大文档或优化处理逻辑

---

### ❓ OpenAI API 调用失败

**错误信息**:
```
OpenAIError: Invalid API key
```

**解决**:
```bash
# 检查 .env 配置
cat backend/.env | grep OPENAI_API_KEY

# 确保设置了有效的 API Key
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
```

---

### ❓ ChromaDB 存储错误

**错误信息**:
```
RuntimeError: ChromaDB path not writable
```

**解决**:
```bash
# 创建 ChromaDB 数据目录
mkdir -p backend/data/chromadb

# 检查权限
ls -la backend/data/
```

---

## 生产环境部署

### 使用 Supervisor 管理 Celery

**安装 Supervisor**:
```bash
# Ubuntu/Debian
sudo apt-get install supervisor

# macOS
brew install supervisor
```

**配置文件** (`/etc/supervisor/conf.d/celery.conf`):
```ini
[program:readpilot-celery]
command=/path/to/backend/.venv/bin/celery -A app.tasks.celery_app worker --loglevel=info
directory=/path/to/backend
user=youruser
numprocs=1
autostart=true
autorestart=true
startsecs=10
stopwaitsecs=600
stderr_logfile=/var/log/celery/worker.err.log
stdout_logfile=/var/log/celery/worker.out.log
```

**启动**:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start readpilot-celery
```

---

### 使用 Systemd 管理 Celery

**配置文件** (`/etc/systemd/system/celery.service`):
```ini
[Unit]
Description=ReadPilot Celery Worker
After=network.target redis.service

[Service]
Type=forking
User=youruser
Group=yourgroup
WorkingDirectory=/path/to/backend
Environment="PATH=/path/to/backend/.venv/bin"
ExecStart=/path/to/backend/.venv/bin/celery -A app.tasks.celery_app worker --loglevel=info --logfile=/var/log/celery/worker.log --pidfile=/var/run/celery/worker.pid
ExecStop=/bin/kill -s TERM $MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
```

**启动**:
```bash
sudo systemctl daemon-reload
sudo systemctl start celery
sudo systemctl enable celery
```

---

## 性能优化

### 并发策略

**1. 多进程 (prefork)** - 默认,适合 CPU 密集型任务
```bash
celery -A app.tasks.celery_app worker --concurrency=4
```

**2. 协程 (gevent)** - 适合 I/O 密集型任务
```bash
pip install gevent
celery -A app.tasks.celery_app worker --pool=gevent --concurrency=100
```

**3. 线程 (threads)** - 中等并发
```bash
celery -A app.tasks.celery_app worker --pool=threads --concurrency=10
```

### 任务优先级

```python
# 高优先级任务
process_document_task.apply_async(
    args=[document_id],
    priority=9  # 0-9, 9 最高
)
```

### 任务重试

```python
@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def process_document_task(self, document_id: str):
    try:
        # 处理逻辑
        pass
    except Exception as exc:
        # 60 秒后重试
        raise self.retry(exc=exc)
```

---

## 相关文档

- [Celery 官方文档](https://docs.celeryq.dev/)
- [Redis 配置指南](https://redis.io/docs/getting-started/)
- [Flower 监控面板](https://flower.readthedocs.io/)

---

## 总结

✅ **启动检查清单**:

- [ ] Redis 已启动 (`redis-cli ping`)
- [ ] 环境变量已配置 (`.env` 文件)
- [ ] Celery Worker 已启动 (`make celery`)
- [ ] FastAPI 后端已启动 (`make dev`)
- [ ] 上传文档测试处理流程

📊 **监控清单**:

- [ ] Flower 监控面板运行中
- [ ] 查看 Celery 日志
- [ ] Redis 连接正常
- [ ] 文档处理状态正确更新

需要帮助? 查看项目 README 或提交 Issue。
