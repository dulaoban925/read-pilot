# ReadPilot Backend

AI-powered reading companion backend built with FastAPI.

## Tech Stack

- **Framework**: FastAPI 0.115 + Uvicorn 0.32
- **Language**: Python 3.12
- **Database**: PostgreSQL 17 / SQLite (async)
- **ORM**: SQLAlchemy 2.0 (async)
- **Vector DB**: Qdrant 1.7
- **Cache**: Redis 6.4
- **AI/LLM**: OpenAI / Anthropic / Ollama
- **Testing**: Pytest 8.4 + pytest-asyncio

## Quick Start

### 1. Install Dependencies

```bash
# Using pip
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Or using Poetry (recommended)
poetry install

# Or using Make
make install
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 3. Run Development Server

```bash
# Method 1: Using Make (推荐)
make dev

# Method 2: Using Poetry
poetry run dev

# Method 3: Using pip
source venv/bin/activate
uvicorn app.main:app --reload
```

Server will start at: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc

### 4. Run Tests

```bash
# Using Make
make test

# Using Poetry
poetry run test

# Using pytest directly
pytest
```

## 📝 快捷命令 (类似 package.json scripts)

我们提供了三种方式来运行快捷命令：

### 方式 1: Make 命令 (推荐，跨平台)

```bash
make help          # 显示所有可用命令
make install       # 安装依赖
make dev           # 启动开发服务器 (热重载)
make prod          # 启动生产服务器
make test          # 运行测试
make lint          # 代码检查
make format        # 代码格式化
make clean         # 清理缓存文件
make health        # 健康检查

# 数据库命令
make db-init       # 初始化数据库
make db-migrate    # 创建数据库迁移
make db-upgrade    # 应用数据库迁移
make db-downgrade  # 回滚数据库迁移

# Docker 命令
make docker-build       # 构建 Docker 镜像
make docker-run         # 运行 Docker 容器
make docker-compose-up  # 启动 Docker Compose
```

### 方式 2: Poetry Scripts

```bash
poetry run dev      # 启动开发服务器
poetry run prod     # 启动生产服务器
poetry run test     # 运行测试
poetry run lint     # 代码检查
poetry run format   # 代码格式化
```

### 方式 3: 直接命令

```bash
uvicorn app.main:app --reload    # 开发服务器
pytest app/tests/                # 运行测试
ruff check app/                  # 代码检查
ruff format app/                 # 代码格式化
```

## Project Structure

```
backend/
├── app/
│   ├── api/              # API endpoints
│   │   └── v1/           # API version 1
│   ├── core/             # Core functionality
│   │   ├── ai/           # AI/LLM integration
│   │   ├── document_parser/  # Document processing
│   │   └── config.py     # Configuration
│   ├── models/           # Database models
│   ├── schemas/          # Pydantic schemas
│   ├── services/         # Business logic
│   ├── db/               # Database utilities
│   ├── tasks/            # Background tasks
│   ├── utils/            # Utility functions
│   ├── tests/            # Test files
│   └── main.py           # FastAPI application
├── data/                 # Data directory (gitignored)
│   ├── documents/        # Uploaded documents
│   └── chroma/           # Vector database
├── pytest.ini            # Pytest configuration
├── pyproject.toml        # Poetry configuration
├── requirements.txt      # Pip dependencies
└── .env.example          # Environment template
```

## API Endpoints

### Health Check
- `GET /` - Root endpoint
- `GET /health` - Health check

### Documentation
- `GET /docs` - Swagger UI
- `GET /redoc` - ReDoc UI

## Development

### Running Tests
```bash
pytest app/tests/ -v
```

### Code Quality
```bash
# Format code
black app/

# Lint code
ruff check app/

# Type checking
mypy app/
```

## Environment Variables

See [.env.example](.env.example) for all available configuration options.

Key variables:
- `DATABASE_URL` - Database connection string
- `REDIS_URL` - Redis connection string
- `QDRANT_URL` - Qdrant vector database URL
- `OPENAI_API_KEY` - OpenAI API key
- `LLM_PROVIDER` - LLM provider (openai/anthropic/ollama)

## License

See [LICENSE](../LICENSE) for details.
