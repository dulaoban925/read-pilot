# Backend Setup Guide

## Prerequisites

- Python 3.12+
- Poetry
- PostgreSQL 15+ or SQLite
- Redis 7+

## Installation Steps

### 1. Install Dependencies

```bash
cd backend

# Install core dependencies
poetry add fastapi uvicorn[standard] sqlalchemy alembic asyncpg aiosqlite

# Install Redis support
poetry add redis[hiredis]

# Install utilities
poetry add pydantic pydantic-settings python-dotenv python-multipart

# Install AI/LLM dependencies (optional for now)
# poetry add openai anthropic langchain chromadb

# Install file processing (will be needed for Phase 2)
# poetry add PyMuPDF ebooklib markdown python-magic-bin

# Install development dependencies
poetry add --group dev pytest pytest-asyncio httpx ruff mypy black
```

### 2. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env and update the following:
# - DATABASE_URL (PostgreSQL or SQLite)
# - REDIS_URL
# - SECRET_KEY (generate a secure key)
# - OPENAI_API_KEY (if using OpenAI)
```

### 3. Start Required Services

#### Using Docker Compose (Recommended)

```bash
# From project root
docker-compose up -d postgres redis qdrant
```

#### Manual Setup

**PostgreSQL:**
```bash
# macOS
brew install postgresql@15
brew services start postgresql@15

# Create database
createdb readpilot
```

**Redis:**
```bash
# macOS
brew install redis
brew services start redis

# Linux
sudo apt-get install redis-server
sudo systemctl start redis
```

### 4. Initialize Database

```bash
# Create initial migration
poetry run alembic revision --autogenerate -m "Initial schema"

# Apply migrations
poetry run alembic upgrade head
```

### 5. Run Tests

```bash
# Test infrastructure setup
poetry run python scripts/test_setup.py

# Run unit tests (when available)
poetry run pytest
```

### 6. Start Development Server

```bash
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Visit:
- API: http://localhost:8000
- Swagger Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Troubleshooting

### Database Connection Issues

**SQLite (Default):**
- No setup needed
- Database file created automatically at `./readpilot.db`

**PostgreSQL:**
```bash
# Check if PostgreSQL is running
pg_isready

# Check connection
psql -U postgres -d readpilot -c "SELECT version();"
```

### Redis Connection Issues

```bash
# Check if Redis is running
redis-cli ping
# Should return: PONG

# Test connection
redis-cli
> SET test "hello"
> GET test
> DEL test
> EXIT
```

### Import Errors

If you get import errors:
```bash
# Make sure you're in the poetry shell
poetry shell

# Or prefix commands with poetry run
poetry run python scripts/test_setup.py
```

### Alembic Issues

If Alembic can't find models:
```bash
# Make sure all models are imported in alembic/env.py
# Check that app.models.__init__.py exports all models
```

## Development Workflow

### Creating a New Migration

```bash
# After changing models
poetry run alembic revision --autogenerate -m "add new field to document"

# Review the generated migration file in alembic/versions/

# Apply the migration
poetry run alembic upgrade head
```

### Rolling Back Migrations

```bash
# Rollback one migration
poetry run alembic downgrade -1

# Rollback to specific version
poetry run alembic downgrade <revision_id>

# Rollback all migrations
poetry run alembic downgrade base
```

### Code Quality

```bash
# Format code
poetry run ruff format .

# Lint code
poetry run ruff check .

# Type check
poetry run mypy app/
```

## Next Steps

Once Phase 1 infrastructure is verified:
1. Start implementing Phase 2 (P1 features)
2. Create document parsers
3. Implement file upload API
4. Add AI summarization

See [tasks.md](../.specify/specs/001-core-reading-experience/tasks.md) for detailed implementation tasks.
