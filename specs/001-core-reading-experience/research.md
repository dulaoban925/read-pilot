# 研究报告：核心阅读体验 (Core Reading Experience)

**功能特性 (Feature)**: 001-core-reading-experience
**日期 (Date)**: 2025-10-22
**状态 (Status)**: 已完成 (Completed)

本文档记录了核心阅读体验功能的技术调研结果，包括技术选型、最佳实践和架构决策。

---

## 1. 文档处理库选型

### 决策：PDF 处理

**选择**: PyMuPDF (fitz) 作为主要 PDF 解析库

**理由**:
- **性能优异**: 比 PyPDF2 快 5-10 倍
- **准确性高**: 更好的文本提取质量，支持复杂布局
- **功能全面**: 支持图像提取、元数据读取、页面渲染
- **维护活跃**: 持续更新，社区支持良好
- **许可证**: AGPL/商业双许可（对开源项目免费）

**替代方案评估**:
- **PyPDF2**: 性能较慢，对复杂 PDF 支持不佳（已弃用）
- **pdfplumber**: 适合表格提取，但文本提取速度较慢
- **pdf2image + Tesseract OCR**: 仅作为扫描 PDF 的后备方案

**实施细节**:
```python
import fitz  # PyMuPDF

def extract_text_from_pdf(file_path: str) -> str:
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text
```

### 决策：EPUB 处理

**选择**: ebooklib + BeautifulSoup4

**理由**:
- **标准兼容**: 完全支持 EPUB 2/3 标准
- **易于使用**: 简洁的 API
- **HTML 解析**: 配合 BeautifulSoup4 清理格式
- **许可证**: AGPL（开源友好）

**实施细节**:
```python
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup

def extract_text_from_epub(file_path: str) -> str:
    book = epub.read_epub(file_path)
    text = ""
    for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
        soup = BeautifulSoup(item.get_content(), 'html.parser')
        text += soup.get_text()
    return text
```

### 决策：DOCX 处理

**选择**: python-docx

**理由**:
- **官方推荐**: Microsoft Office 文档的标准 Python 库
- **稳定可靠**: 成熟的项目，广泛使用
- **许可证**: MIT

**实施细节**:
```python
import docx

def extract_text_from_docx(file_path: str) -> str:
    doc = docx.Document(file_path)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text
```

### 决策：Markdown 处理

**选择**: Python-Markdown + markdownify

**理由**:
- **原生支持**: Markdown 是纯文本格式，直接读取即可
- **扩展性**: Python-Markdown 支持插件（如代码高亮、表格）
- **许可证**: BSD

**实施细节**:
```python
def extract_text_from_markdown(file_path: str) -> str:
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()
```

---

## 2. 文本分块策略 (Text Chunking Strategy)

### 决策：固定 Token 数分块 + 重叠窗口 (Overlapping Window)

**选择**: LangChain TextSplitter (RecursiveCharacterTextSplitter)

**参数配置**:
- **chunk_size**: 800 tokens (约 600 个英文单词或 400 个中文字符)
- **chunk_overlap**: 100 tokens (保留上下文连贯性)
- **分隔符优先级**: `\n\n` → `\n` → `.` → ` ` (按段落、句子、单词分割)

**理由**:
- **上下文完整性**: 重叠窗口避免语义被切断
- **向量搜索友好**: chunk 大小适合 OpenAI text-embedding-3-small (8191 tokens 限制)
- **性能平衡**: 800 tokens 既保证上下文，又控制向量数量

**替代方案评估**:
- **固定字符数分块**: 忽略语义边界，可能切断句子
- **语义分块 (Semantic Chunking)**: 更准确但计算成本高，暂不采用

**实施细节**:
```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=100,
    separators=["\n\n", "\n", "。", ".", " ", ""],
    length_function=lambda text: len(tiktoken.encode(text))
)

chunks = splitter.split_text(document_text)
```

---

## 3. 向量数据库选型 (Vector Database Selection)

### 决策：ChromaDB

**理由**:
- **轻量级**: 嵌入式数据库 (Embedded Database)，无需独立部署
- **易于集成**: Python 原生支持，API 简洁
- **开发友好**: 本地持久化，便于开发和测试
- **性能足够**: 支持 10 万级别向量（满足 MVP 需求）
- **许可证**: Apache 2.0

**替代方案评估**:
- **Pinecone**: 云托管，成本高，依赖外部服务（违反隐私优先原则）
- **Weaviate**: 功能强大但部署复杂，对 MVP 过重
- **Milvus**: 适合大规模部署，但 MVP 阶段不需要

**扩展性考虑**:
- MVP 使用 ChromaDB
- 生产环境可迁移到 Qdrant 或 Weaviate（接口相似，迁移成本低）

**实施细节**:
```python
import chromadb
from chromadb.config import Settings

client = chromadb.Client(Settings(
    chroma_db_impl="duckdb+parquet",
    persist_directory="./chroma_data"
))

collection = client.create_collection(
    name="documents",
    metadata={"hnsw:space": "cosine"}
)

# 添加文档
collection.add(
    embeddings=embeddings,
    documents=chunks,
    ids=[f"doc_{i}" for i in range(len(chunks))],
    metadatas=[{"doc_id": doc_id, "chunk_idx": i} for i in range(len(chunks))]
)

# 搜索
results = collection.query(
    query_embeddings=query_embedding,
    n_results=5
)
```

---

## 4. AI 服务集成 (AI Service Integration)

### 决策：OpenAI 作为主要提供商，Anthropic 作为备选

**主要提供商 (Primary Provider)：OpenAI**

**选择的模型**:
- **文本嵌入 (Text Embedding)**: `text-embedding-3-small` (成本低，性能好)
- **摘要和问答 (Summary & Q&A)**: `gpt-4o-mini` (成本可控，质量高)
- **复杂任务（可选）**: `gpt-4o` (仅在用户主动选择时使用)

**理由**:
- **性价比**: text-embedding-3-small 比 ada-002 便宜 5 倍
- **速度**: gpt-4o-mini 响应速度快（< 5s）
- **质量**: GPT-4 系列摘要质量优于 GPT-3.5
- **API 稳定性**: OpenAI API 成熟度高

**备选提供商 (Fallback Provider)：Anthropic Claude**

**选择的模型**:
- **摘要和问答**: `claude-3-haiku` (快速且成本低)
- **复杂任务（可选）**: `claude-3.5-sonnet` (质量更高)

**理由**:
- **降低单点依赖**: OpenAI API 限流时自动切换
- **隐私友好**: Claude 承诺不使用用户数据训练模型
- **长文本处理**: Claude 支持 200k tokens 上下文（适合大文档）

**成本控制策略**:
1. **缓存优先 (Cache First)**: 摘要结果缓存在 Redis，相同文档不重复生成
2. **速率限制 (Rate Limiting)**: 每用户每分钟最多 10 次 AI 请求
3. **模型降级**: 默认使用 mini 版本，用户可选升级
4. **批量处理 (Batch Processing)**: 多个 chunk 的嵌入请求合并为一个 API 调用

**实施细节**:
```python
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic

class AIProvider:
    async def generate_summary(self, text: str) -> dict:
        raise NotImplementedError

class OpenAIProvider(AIProvider):
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)

    async def generate_summary(self, text: str) -> dict:
        response = await self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "生成文档摘要..."},
                {"role": "user", "content": text}
            ]
        )
        return response.choices[0].message.content

class AnthropicProvider(AIProvider):
    def __init__(self, api_key: str):
        self.client = AsyncAnthropic(api_key=api_key)

    async def generate_summary(self, text: str) -> dict:
        response = await self.client.messages.create(
            model="claude-3-haiku-20240307",
            messages=[{"role": "user", "content": text}]
        )
        return response.content[0].text
```

---

## 5. 异步任务队列 (Async Task Queue)

### 决策：Celery + Redis

**理由**:
- **成熟稳定**: 事实标准的 Python 异步任务框架
- **功能丰富**: 支持任务优先级、重试、定时任务
- **监控便利**: Flower 提供 Web 监控界面
- **可扩展性**: 支持水平扩展 worker

**替代方案评估**:
- **FastAPI Background Tasks**: 仅适合轻量任务，无法持久化
- **RQ (Redis Queue)**: 简单但功能有限，不支持任务链
- **Dramatiq**: 现代化但社区不如 Celery 成熟

**实施细节**:
```python
from celery import Celery

celery_app = Celery(
    "readpilot",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1"
)

@celery_app.task(bind=True, max_retries=3)
def process_document(self, document_id: str):
    try:
        # 文档处理逻辑
        doc = extract_text(document_id)
        chunks = split_text(doc)
        embeddings = generate_embeddings(chunks)
        store_in_vector_db(embeddings)
    except Exception as exc:
        self.retry(exc=exc, countdown=60)  # 1 分钟后重试
```

---

## 6. 缓存策略 (Caching Strategy)

### 决策：Redis + 多层缓存 (Multi-tier Cache)

**缓存层级**:
1. **L1 - 应用内存缓存**: LRU Cache (最近使用的摘要)
2. **L2 - Redis 缓存**: 持久化摘要和向量搜索结果
3. **L3 - 数据库**: PostgreSQL 存储所有历史数据

**缓存键设计**:
```python
# 摘要缓存
summary_key = f"summary:{doc_id}:{depth}"  # depth: brief/detailed
ttl = 7 * 24 * 3600  # 7 天

# 向量搜索缓存
search_key = f"search:{doc_id}:{query_hash}"
ttl = 1 * 24 * 3600  # 1 天
```

**缓存失效策略 (Cache Invalidation)**:
- **文档更新**: 删除该文档的所有缓存
- **用户删除文档**: 级联删除缓存
- **TTL 过期**: Redis 自动清理

**实施细节**:
```python
import redis.asyncio as redis

class CacheService:
    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url)

    async def get_summary(self, doc_id: str, depth: str) -> Optional[dict]:
        key = f"summary:{doc_id}:{depth}"
        data = await self.redis.get(key)
        return json.loads(data) if data else None

    async def set_summary(self, doc_id: str, depth: str, summary: dict):
        key = f"summary:{doc_id}:{depth}"
        await self.redis.setex(key, 7 * 24 * 3600, json.dumps(summary))
```

---

## 7. 认证和授权 (Authentication & Authorization)

### 决策：JWT + OAuth2 密码流 (Password Flow)

**认证流程 (Authentication Flow)**:
1. 用户登录 → 返回 access_token (15 分钟) + refresh_token (7 天)
2. 请求 API 时携带 access_token
3. access_token 过期 → 使用 refresh_token 获取新 token
4. refresh_token 过期 → 重新登录

**密码加密**: bcrypt (work factor = 12)

**实施细节**:
```python
from passlib.context import CryptContext
from jose import jwt
from datetime import timedelta

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(user_id: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=15)
    payload = {"sub": user_id, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")
```

---

## 8. 文件存储 (File Storage)

### 决策：本地文件系统 (开发) + S3 兼容存储 (生产)

**本地存储结构**:
```
uploads/
├── {user_id}/
│   ├── {document_id}.pdf
│   ├── {document_id}.epub
│   └── ...
```

**S3 兼容存储** (MinIO / AWS S3 / 阿里云 OSS):
- **Bucket**: `readpilot-documents`
- **Key**: `{user_id}/{document_id}.{ext}`
- **访问控制**: 私有，通过预签名 URL 访问

**实施细节**:
```python
from abc import ABC, abstractmethod
import boto3

class FileStorage(ABC):
    @abstractmethod
    async def save(self, file_path: str, content: bytes):
        pass

class LocalFileStorage(FileStorage):
    def __init__(self, base_dir: str):
        self.base_dir = base_dir

    async def save(self, file_path: str, content: bytes):
        full_path = os.path.join(self.base_dir, file_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'wb') as f:
            f.write(content)

class S3FileStorage(FileStorage):
    def __init__(self, bucket: str, endpoint: str):
        self.s3 = boto3.client('s3', endpoint_url=endpoint)
        self.bucket = bucket

    async def save(self, file_path: str, content: bytes):
        self.s3.put_object(Bucket=self.bucket, Key=file_path, Body=content)
```

---

## 9. 数据库迁移 (Database Migration)

### 决策：Alembic

**理由**:
- **SQLAlchemy 官方工具**: 与 ORM 无缝集成
- **版本控制**: 自动生成迁移脚本
- **回滚支持**: 安全的数据库变更管理

**实施细节**:
```bash
# 初始化 Alembic
alembic init alembic

# 生成迁移脚本
alembic revision --autogenerate -m "Create initial tables"

# 执行迁移
alembic upgrade head

# 回滚
alembic downgrade -1
```

---

## 10. 前端状态管理 (Frontend State Management)

### 决策：Zustand

**理由**:
- **简洁轻量**: API 直观，学习曲线低
- **TypeScript 友好**: 原生 TS 支持
- **性能优异**: 基于 React hooks，最小化重渲染
- **宪章符合**: 符合项目宪章推荐

**实施细节**:
```typescript
import { create } from 'zustand'

interface DocumentStore {
  documents: Document[]
  selectedDocument: Document | null
  setDocuments: (docs: Document[]) => void
  selectDocument: (doc: Document) => void
}

export const useDocumentStore = create<DocumentStore>((set) => ({
  documents: [],
  selectedDocument: null,
  setDocuments: (docs) => set({ documents: docs }),
  selectDocument: (doc) => set({ selectedDocument: doc })
}))
```

---

## 11. API 客户端 (API Client)

### 决策：Axios + React Query (TanStack Query)

**理由**:
- **Axios**: 成熟的 HTTP 客户端，支持拦截器 (Interceptor)、请求取消
- **React Query**: 自动缓存、重试、后台刷新

**实施细节**:
```typescript
import axios from 'axios'
import { useQuery, useMutation } from '@tanstack/react-query'

const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  timeout: 30000
})

// 请求拦截器 - 添加 token
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截器 - 处理 401
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // 尝试刷新 token
      await refreshToken()
      return apiClient.request(error.config)
    }
    return Promise.reject(error)
  }
)

// 使用 React Query
export const useDocuments = () => {
  return useQuery({
    queryKey: ['documents'],
    queryFn: async () => {
      const { data } = await apiClient.get('/api/v1/documents')
      return data
    }
  })
}
```

---

## 12. 错误处理 (Error Handling)

### 决策：分层错误处理 (Layered Error Handling)

**后端错误类型**:
```python
class AppException(Exception):
    def __init__(self, message: str, code: str, status_code: int = 400):
        self.message = message
        self.code = code
        self.status_code = status_code

class DocumentNotFoundError(AppException):
    def __init__(self, doc_id: str):
        super().__init__(
            message=f"Document {doc_id} not found",
            code="DOCUMENT_NOT_FOUND",
            status_code=404
        )

# FastAPI 异常处理器
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.message, "code": exc.code}
    )
```

**前端错误处理**:
```typescript
// 统一错误处理
const handleError = (error: any) => {
  if (error.response?.data?.code) {
    // 显示业务错误
    toast.error(error.response.data.message)
  } else if (error.code === 'ECONNABORTED') {
    toast.error('请求超时，请重试')
  } else {
    toast.error('发生未知错误，请联系管理员')
  }
}
```

---

## 13. 日志和监控 (Logging & Monitoring)

### 决策：结构化日志 (Structured Logging) + Prometheus 指标

**日志方案**:
- **后端**: structlog (结构化日志)
- **前端**: Sentry (错误追踪)

**监控指标 (Metrics)**:
- **API 延迟**: p50, p95, p99
- **错误率**: 4xx / 5xx 占比
- **文档处理时长**: 按文档格式分类
- **AI API 调用次数和成本**: 按模型分类

**实施细节**:
```python
import structlog

logger = structlog.get_logger()

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time

    logger.info(
        "http_request",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration_ms=int(duration * 1000)
    )
    return response
```

---

## 总结

本研究文档确立了 ReadPilot MVP 的技术栈和最佳实践：

**核心决策**:
1. ✅ 文档处理: PyMuPDF (PDF), ebooklib (EPUB), python-docx (DOCX)
2. ✅ 文本分块: LangChain RecursiveCharacterTextSplitter (800 tokens, 100 overlap)
3. ✅ 向量数据库: ChromaDB (MVP 阶段)
4. ✅ AI 服务: OpenAI (主) + Anthropic (备)
5. ✅ 异步任务: Celery + Redis
6. ✅ 缓存: Redis 多层缓存
7. ✅ 认证: JWT + OAuth2
8. ✅ 文件存储: 本地 (dev) + S3 (prod)
9. ✅ 状态管理: Zustand + React Query

**下一步**: 进入 Phase 1 设计阶段，生成数据模型和 API 契约。
