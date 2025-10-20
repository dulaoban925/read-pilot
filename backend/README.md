# ReadPilot Backend

AI-powered reading companion built with **FastAPI** and **Parlant multi-agent architecture**.

## 🏗️ Architecture Overview

```
backend/
├── main.py                          # FastAPI application entry point
├── config.py                        # Configuration management
├── requirements.txt                 # Python dependencies
│
├── agents/                          # Parlant Agents (5 specialized agents)
│   ├── coordinator.py               # Routes requests to specialized agents
│   ├── summarizer.py                # Document analysis and summarization
│   ├── qa.py                        # Context-aware question answering
│   ├── note_builder.py              # Structured notes and flashcards
│   └── quiz_generator.py            # Personalized quiz generation
│
├── tools/                           # Parlant Tools
│   ├── document_tools.py            # Document processing
│   ├── vector_tools.py              # Semantic search
│   ├── context_tools.py             # Context and state management
│   └── llm_tools.py                 # LLM API calls
│
├── models/                          # Data models (SQLAlchemy + Pydantic)
│   ├── user.py
│   ├── document.py
│   └── session.py
│
├── services/                        # Business logic layer
│   ├── database_service.py          # Database operations
│   ├── vector_service.py            # Vector database
│   └── agent_service.py             # Parlant agent management
│
└── api/                             # API routes
    ├── chat.py                      # Chat endpoints
    ├── documents.py                 # Document management
    └── users.py                     # User authentication
```

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.13+ installed
- PostgreSQL 15+ (optional, for production)
- Qdrant (optional, for vector search)

### 2. Create Virtual Environment

```bash
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows
```

### 3. Install Dependencies

```bash
# Upgrade pip (optional)
pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt
```

**Note**: If you encounter SSL certificate errors, try:

```bash
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
```

### 4. Configure Environment

Create a `.env` file in the backend directory:

```env
# Database (optional for development, uses SQLite by default)
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/readpilot

# Vector Database (Qdrant - recommended)
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION_NAME=documents

# LLM Provider (OpenAI as primary)
OPENAI_API_KEY=sk-your-openai-api-key-here
DEFAULT_LLM_PROVIDER=openai
DEFAULT_MODEL=gpt-3.5-turbo  # or gpt-4 for better quality
EMBEDDING_MODEL=text-embedding-3-small

# Optional: Anthropic as backup provider
# ANTHROPIC_API_KEY=your-anthropic-key

# Redis Cache (optional)
REDIS_URL=redis://localhost:6379

# Application
SECRET_KEY=your-secret-key-change-in-production
DEBUG=True
```

### 5. Start Required Services (Optional)

#### Option A: Using Docker (Recommended)

```bash
# Start Qdrant vector database
docker run -d -p 6333:6333 -v qdrant_storage:/qdrant/storage qdrant/qdrant

# Start PostgreSQL (if not using SQLite)
docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=readpilot postgres:15

# Start Redis (if using cache)
docker run -d -p 6379:6379 redis:7-alpine
```

#### Option B: Skip Services (Development)

You can start the backend without external services by:

- Using SQLite instead of PostgreSQL (default)
- Disabling vector search temporarily
- Disabling Redis cache

### 6. Initialize Database

```bash
# Run database migrations (if using PostgreSQL)
alembic upgrade head

# Or skip for development (uses in-memory SQLite)
```

### 7. Run the Application

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Development mode with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Or use Python directly
python main.py
```

The API will be available at:
- **API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📚 API Endpoints

### Chat

- `POST /api/v1/chat/` - Send message to AI assistant
- `GET /api/v1/chat/sessions/{session_id}/messages` - Get session messages

### Documents

- `POST /api/v1/documents/upload` - Upload document
- `GET /api/v1/documents/{document_id}` - Get document
- `GET /api/v1/documents/user/{user_id}` - Get user documents
- `GET /api/v1/documents/{document_id}/summary` - Get document summary
- `POST /api/v1/documents/{document_id}/process` - Process document
- `DELETE /api/v1/documents/{document_id}` - Delete document

### Users

- `POST /api/v1/users/register` - Register new user
- `POST /api/v1/users/login` - User login
- `GET /api/v1/users/me` - Get current user
- `PUT /api/v1/users/me` - Update user
- `PUT /api/v1/users/me/preferences` - Update preferences
- `GET /api/v1/users/me/stats` - Get learning statistics

## 🤖 Parlant Agents

### 1. Coordinator Agent
- Routes user requests to specialized agents
- Maintains session state
- Tracks user behavior

### 2. Summarizer Agent
- Multi-level document summarization
- Document type detection
- User preference adaptation

### 3. QA Agent
- Context-aware question answering
- Multi-turn conversation
- Semantic search integration
- Source citation

### 4. Note Builder Agent
- Structured note generation
- Anki-style flashcards
- Concept mapping
- Auto-tagging

### 5. Quiz Generator Agent
- Multiple question types (MCQ, fill-blank, short answer)
- Adaptive difficulty
- Weak point targeting
- Bloom's taxonomy alignment

## 🔧 Configuration

### LLM Provider

Switch between OpenAI and Anthropic in `config.py`:

```python
DEFAULT_LLM_PROVIDER = "openai"  # or "anthropic"
DEFAULT_MODEL = "gpt-4"          # or "claude-3-sonnet-20240229"
```

### Vector Database

**Qdrant** is the recommended vector database (open-source, self-hosted):

```python
# Primary: Qdrant (recommended)
QDRANT_URL = "http://localhost:6333"
QDRANT_COLLECTION_NAME = "documents"
USE_QDRANT = True

# Alternative: Pinecone (SaaS, currently disabled)
# PINECONE_API_KEY = "your-key"
# PINECONE_INDEX_NAME = "readpilot-documents"
# USE_PINECONE = False
```

To switch to Pinecone (if needed):

1. Uncomment `pinecone-client` in [requirements.txt](requirements.txt)
2. Set `USE_PINECONE = True` in config
3. Update implementation in `services/vector_service.py`

## 🧪 Testing

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/
```

## 📦 Deployment

### Docker

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/readpilot
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: readpilot
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

## 🔒 Security

### Authentication

JWT-based authentication:

```python
# Login
POST /api/v1/users/login
{
  "email": "user@example.com",
  "password": "password"
}

# Returns
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}

# Use token in subsequent requests
Authorization: Bearer eyJ...
```

### Environment Variables

⚠️ **Never commit `.env` files to version control!**

Use `.env.example` as a template.

## 📖 Development Guide

### Adding a New Agent

1. Create agent file in `agents/`:

```python
# agents/my_agent.py
async def setup_my_agent(server: Server) -> Agent:
    agent = await server.create_agent(
        name="MyAgent",
        description="Agent description"
    )

    await agent.create_guideline(
        condition="When...",
        action="Do...",
        tools=[...]
    )

    return agent
```

2. Register in `agents/__init__.py`

3. Initialize in `services/agent_service.py`

### Adding a New Tool

1. Create tool in `tools/`:

```python
# tools/my_tools.py
@tool
async def my_tool(context: ToolContext, param: str) -> ToolResult:
    # Tool logic
    return ToolResult(success=True, data={"result": "..."})
```

2. Export in `tools/__init__.py`

3. Use in agent guidelines

## 🐛 Troubleshooting

### Parlant Connection Issues

```bash
# Check Parlant server status
curl http://localhost:8080/health
```

### Database Connection Issues

```bash
# Test PostgreSQL connection
psql postgresql://postgres:postgres@localhost:5432/readpilot
```

### Vector Database Issues

```bash
# Pinecone: Check index status via dashboard
# Qdrant: Check status
curl http://localhost:6333/
```

## 📄 License

MIT License

## 🤝 Contributing

See [PARLANT_AGENT_STRUCTURE.md](../PARLANT_AGENT_STRUCTURE.md) for architecture details.

## 📞 Support

- Documentation: [PARLANT_AGENT_STRUCTURE.md](../PARLANT_AGENT_STRUCTURE.md)
- Issues: GitHub Issues
- Email: support@readpilot.com
