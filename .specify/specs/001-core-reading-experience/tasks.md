# Task Breakdown: ReadPilot 核心阅读体验

## Metadata

- **Feature ID**: 001-core-reading-experience
- **Related Spec**: [spec.md](./spec.md)
- **Related Plan**: [plan.md](./plan.md)
- **Created**: 2025-10-21
- **Status**: Ready for Implementation

---

## Task Organization Principles

本任务列表遵循以下原则：

1. **独立交付**：每个用户故事（P1-P4）可以独立完成和测试
2. **并行开发**：标记 `[P]` 的任务可以同时进行
3. **渐进增强**：优先级低的功能不影响高优先级功能的交付
4. **测试驱动**：每个阶段完成后都有明确的验收标准

**任务格式说明**：
- `[ID]`: 任务唯一标识符
- `[P]`: 可并行执行的任务
- `(file_path)`: 具体实现文件路径
- `✓ 验收标准`: 任务完成的检查点

---

## Phase 0: 项目初始化

**目标**: 搭建开发环境和基础设施

**估时**: 1-2 天

### [SETUP-001] 创建项目仓库和目录结构

```bash
# 创建目录结构
mkdir -p readpilot/{frontend,backend,shared,docs,scripts}

# 初始化 Git
git init
```

**验收标准**:
- ✓ 项目目录结构符合 plan.md 中的定义
- ✓ Git 仓库初始化完成
- ✓ .gitignore 文件配置正确

---

### [SETUP-002] [P] 初始化前端项目

```bash
cd frontend
pnpm create next-app@latest . --typescript --tailwind --app --no-src-dir
```

**实现内容**:
- 安装 Next.js 15 + React 19 + TypeScript 5.7
- 配置 Tailwind CSS 4.0
- 配置 ESLint 9.15 + Prettier 3.3
- 设置 tsconfig.json (strict mode)

**文件**:
- `frontend/package.json`
- `frontend/next.config.js`
- `frontend/tailwind.config.ts`
- `frontend/tsconfig.json`

**验收标准**:
- ✓ `pnpm dev` 可正常启动开发服务器
- ✓ TypeScript 编译无错误
- ✓ Tailwind CSS 样式生效

---

### [SETUP-003] [P] 初始化后端项目

```bash
cd backend
poetry init
poetry add fastapi uvicorn sqlalchemy alembic
```

**实现内容**:
- 创建 Poetry 项目 (Python 3.12)
- 安装核心依赖 (FastAPI 0.115, SQLAlchemy 2.0)
- 配置 Ruff 0.8 + mypy 1.13
- 设置 pyproject.toml

**文件**:
- `backend/pyproject.toml`
- `backend/app/main.py` (FastAPI 入口)
- `backend/app/config.py` (配置管理)

**验收标准**:
- ✓ `poetry run uvicorn app.main:app --reload` 可启动服务器
- ✓ 访问 http://localhost:8000/docs 可看到 Swagger 文档
- ✓ Ruff 和 mypy 检查通过

---

### [SETUP-004] 配置 Docker Compose 开发环境

**文件**: `docker-compose.yml`

```yaml
services:
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/readpilot
      - REDIS_URL=redis://redis:6379/0

  db:
    image: postgres:17-alpine
    environment:
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=readpilot

  redis:
    image: redis:7.4-alpine
```

**验收标准**:
- ✓ `docker-compose up` 可启动所有服务
- ✓ 前端可访问 http://localhost:3000
- ✓ 后端可访问 http://localhost:8000
- ✓ PostgreSQL 和 Redis 正常运行

---

### [SETUP-005] 配置 CI/CD (GitHub Actions)

**文件**: `.github/workflows/ci.yml`

**实现内容**:
- 前端：TypeScript 检查、ESLint、单元测试
- 后端：Ruff、mypy、pytest
- E2E 测试 (Playwright)

**验收标准**:
- ✓ 推送代码后 CI 自动运行
- ✓ 所有检查通过

---

## Phase 1: 基础设施（阻塞性前置任务）

**目标**: 实现核心基础服务，为业务功能奠定基础

**估时**: 3-4 天

### [FOUND-001] 实现数据库模型和迁移

**文件**:
- `backend/app/models/user.py`
- `backend/app/models/document.py`
- `backend/app/models/annotation.py`
- `backend/app/models/chat_message.py`
- `backend/app/models/reading_session.py`
- `backend/alembic/versions/001_initial_schema.py`

**实现内容**:
```python
# models/document.py
from sqlalchemy import Column, String, Integer, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship

class Document(Base):
    __tablename__ = "documents"

    id = Column(String(50), primary_key=True)
    user_id = Column(String(50), ForeignKey("users.id"))
    title = Column(String(500), nullable=False)
    file_path = Column(String(1000), nullable=False)
    file_hash = Column(String(64), nullable=False)
    page_count = Column(Integer)
    parsed_content = Column(JSON)
    current_page = Column(Integer, default=1)
    # ... 其他字段
```

**数据库表**:
- users
- documents
- annotations
- chat_messages
- reading_sessions
- ai_summaries

**验收标准**:
- ✓ `alembic upgrade head` 可创建所有表
- ✓ 所有模型关系定义正确
- ✓ 索引优化完成 (file_hash, user_id 等)

---

### [FOUND-002] 实现数据库会话管理

**文件**: `backend/app/db/session.py`

```python
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session
```

**验收标准**:
- ✓ 异步数据库连接池正常工作
- ✓ 依赖注入可用 (`Depends(get_db)`)

---

### [FOUND-003] 实现 Redis 缓存管理

**文件**: `backend/app/core/cache.py`

```python
import redis.asyncio as redis
from typing import Optional

class CacheManager:
    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url)

    async def get(self, key: str) -> Optional[str]:
        return await self.redis.get(key)

    async def set(self, key: str, value: str, expire: int = 3600):
        await self.redis.setex(key, expire, value)

    async def delete(self, key: str):
        await self.redis.delete(key)
```

**验收标准**:
- ✓ 可读写 Redis
- ✓ 过期时间正确设置
- ✓ 连接池正常工作

---

### [FOUND-004] 实现文件上传和存储

**文件**: `backend/app/utils/file_storage.py`

```python
import hashlib
from pathlib import Path

class FileStorage:
    def __init__(self, base_path: str = "/data/documents"):
        self.base_path = Path(base_path)

    async def save_file(self, file: UploadFile) -> dict:
        # 计算文件哈希
        content = await file.read()
        file_hash = hashlib.sha256(content).hexdigest()

        # 保存到磁盘
        file_path = self.base_path / f"{file_hash[:2]}" / f"{file_hash}.pdf"
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "wb") as f:
            f.write(content)

        return {"file_hash": file_hash, "file_path": str(file_path)}
```

**验收标准**:
- ✓ 文件保存到本地文件系统
- ✓ 使用哈希值去重
- ✓ 目录按哈希前缀分片 (避免单目录文件过多)

---

### [FOUND-005] 实现文件验证和安全检查

**文件**: `backend/app/utils/file_validation.py`

```python
import magic

ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/epub+zip",
    "text/plain",
}

def validate_file(file: UploadFile) -> None:
    # 检查文件大小
    if file.size > 50 * 1024 * 1024:  # 50MB
        raise HTTPException(400, "文件大小超过 50MB 限制")

    # 检查 MIME 类型（魔法字节）
    file_bytes = file.file.read(2048)
    file.file.seek(0)
    mime = magic.from_buffer(file_bytes, mime=True)

    if mime not in ALLOWED_MIME_TYPES:
        raise HTTPException(400, f"不支持的文件类型: {mime}")
```

**验收标准**:
- ✓ 文件大小验证生效
- ✓ 魔法字节验证生效 (防止伪造扩展名)
- ✓ 不支持的格式被拒绝

---

### [FOUND-006] 配置前端 API 客户端

**文件**: `frontend/lib/api-client.ts`

```typescript
import axios from 'axios';

export const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器（添加认证 Token）
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// 响应拦截器（错误处理）
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // 跳转到登录页
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);
```

**验收标准**:
- ✓ 可向后端发送请求
- ✓ 请求拦截器正常工作
- ✓ 错误统一处理

---

### [FOUND-007] 配置 Zustand 状态管理

**文件**: `frontend/lib/store/document-store.ts`

```typescript
import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

interface DocumentStore {
  currentDocument: Document | null;
  documents: Document[];
  setCurrentDocument: (doc: Document) => void;
  addDocument: (doc: Document) => void;
}

export const useDocumentStore = create<DocumentStore>()(
  devtools(
    persist(
      (set) => ({
        currentDocument: null,
        documents: [],
        setCurrentDocument: (doc) => set({ currentDocument: doc }),
        addDocument: (doc) => set((state) => ({
          documents: [...state.documents, doc]
        })),
      }),
      { name: 'document-storage' }
    )
  )
);
```

**验收标准**:
- ✓ 状态可读写
- ✓ LocalStorage 持久化生效
- ✓ Redux DevTools 可调试

---

## Phase 2: P1 用户故事 - 基础文档阅读与 AI 摘要生成

**目标**: 用户能够上传文档、阅读文档、生成摘要

**估时**: 5-7 天

**独立测试**: 在没有对话功能、笔记功能的情况下，此功能应独立工作

---

### [P1-001] 实现文档解析器接口

**文件**: `backend/app/core/document_parser/base.py`

```python
from abc import ABC, abstractmethod
from typing import Dict, Any

class DocumentParser(ABC):
    @abstractmethod
    async def parse(self, file_path: str, options: Dict[str, Any]) -> Dict:
        """解析文档并返回结构化内容"""
        pass

    @abstractmethod
    def supports_format(self, file_extension: str) -> bool:
        """检查是否支持该格式"""
        pass
```

**验收标准**:
- ✓ 抽象接口定义清晰
- ✓ 类型注解完整

---

### [P1-002] [P] 实现 PDF 解析器

**文件**: `backend/app/core/document_parser/pdf_parser.py`

```python
import fitz  # PyMuPDF

class PDFParser(DocumentParser):
    async def parse(self, file_path: str, options: Dict[str, Any]) -> Dict:
        doc = fitz.open(file_path)
        pages = []

        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text")

            pages.append({
                "page_num": page_num + 1,
                "text": text,
                "bbox": page.rect,
            })

        return {
            "title": doc.metadata.get("title", ""),
            "page_count": len(doc),
            "word_count": sum(len(p["text"].split()) for p in pages),
            "pages": pages,
        }

    def supports_format(self, ext: str) -> bool:
        return ext.lower() == ".pdf"
```

**验收标准**:
- ✓ 可正确解析 PDF 文件
- ✓ 提取文本、页码、元数据
- ✓ 处理多页文档

---

### [P1-003] [P] 实现 EPUB 解析器

**文件**: `backend/app/core/document_parser/epub_parser.py`

```python
import ebooklib
from ebooklib import epub

class EPUBParser(DocumentParser):
    async def parse(self, file_path: str, options: Dict[str, Any]) -> Dict:
        book = epub.read_epub(file_path)

        # 提取章节内容
        chapters = []
        for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
            content = item.get_content().decode('utf-8')
            # 移除 HTML 标签
            text = self._strip_html(content)
            chapters.append(text)

        return {
            "title": book.get_metadata('DC', 'title')[0][0],
            "author": book.get_metadata('DC', 'creator')[0][0],
            "chapter_count": len(chapters),
            "chapters": chapters,
        }
```

**验收标准**:
- ✓ 可正确解析 EPUB 文件
- ✓ 提取章节内容
- ✓ 移除 HTML 标签

---

### [P1-004] [P] 实现 Markdown 解析器

**文件**: `backend/app/core/document_parser/markdown_parser.py`

```python
import markdown

class MarkdownParser(DocumentParser):
    async def parse(self, file_path: str, options: Dict[str, Any]) -> Dict:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 解析为 HTML
        html = markdown.markdown(content, extensions=['extra', 'toc'])

        return {
            "title": self._extract_title(content),
            "content": content,
            "html": html,
        }
```

**验收标准**:
- ✓ 可正确解析 Markdown 文件
- ✓ 转换为 HTML

---

### [P1-005] 实现解析器工厂

**文件**: `backend/app/core/document_parser/factory.py`

```python
from pathlib import Path

class ParserFactory:
    _parsers = [PDFParser(), EPUBParser(), MarkdownParser()]

    @classmethod
    def get_parser(cls, filename: str) -> DocumentParser:
        ext = Path(filename).suffix
        for parser in cls._parsers:
            if parser.supports_format(ext):
                return parser
        raise ValueError(f"Unsupported file format: {ext}")
```

**验收标准**:
- ✓ 可根据文件扩展名选择解析器
- ✓ 不支持的格式抛出异常

---

### [P1-006] 实现文档上传 API

**文件**: `backend/app/api/v1/documents.py`

```python
from fastapi import APIRouter, UploadFile, File, Depends

router = APIRouter(prefix="/documents", tags=["documents"])

@router.post("")
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    # 1. 验证文件
    validate_file(file)

    # 2. 保存文件
    storage = FileStorage()
    file_info = await storage.save_file(file)

    # 3. 解析文档（小文件同步，大文件异步）
    if file.size < 10 * 1024 * 1024:  # < 10MB
        parser = ParserFactory.get_parser(file.filename)
        parsed_content = await parser.parse(file_info["file_path"], {})
    else:
        # 发送到 Celery 队列
        task = parse_document_task.delay(file_info["file_path"])
        return {"status": "processing", "task_id": task.id}

    # 4. 保存到数据库
    document = Document(
        id=f"doc_{uuid4().hex[:12]}",
        title=parsed_content["title"],
        file_path=file_info["file_path"],
        file_hash=file_info["file_hash"],
        page_count=parsed_content.get("page_count"),
        parsed_content=parsed_content,
    )
    db.add(document)
    await db.commit()

    return {"status": "completed", "document": document}
```

**API 端点**:
- `POST /api/v1/documents` - 上传文档
- `GET /api/v1/documents/{document_id}` - 获取文档详情
- `GET /api/v1/documents/{document_id}/status` - 查询处理状态

**验收标准**:
- ✓ 可上传文件并返回文档 ID
- ✓ 小文件同步处理
- ✓ 大文件异步处理 (返回 task_id)
- ✓ 错误处理完善

---

### [P1-007] 实现 Celery 异步任务

**文件**: `backend/app/tasks/document_tasks.py`

```python
from celery import Celery

celery_app = Celery("readpilot", broker="redis://redis:6379/0")

@celery_app.task
def parse_document_task(file_path: str) -> dict:
    parser = ParserFactory.get_parser(file_path)
    parsed_content = parser.parse(file_path, {})

    # 更新数据库
    # ...

    return parsed_content
```

**验收标准**:
- ✓ Celery Worker 正常运行
- ✓ 任务可提交和执行
- ✓ 任务状态可查询

---

### [P1-008] 实现前端文档上传组件

**文件**: `frontend/components/DocumentUpload.tsx`

```typescript
'use client';

import { useUploadDocument } from '@/lib/hooks/useDocument';

export function DocumentUpload() {
  const uploadMutation = useUploadDocument();

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // 上传文件
    const result = await uploadMutation.mutateAsync(file);

    if (result.status === 'completed') {
      // 跳转到阅读页面
      router.push(`/reader/${result.document.id}`);
    } else {
      // 轮询检查状态
      startPolling(result.document_id);
    }
  };

  return (
    <div className="upload-container">
      <input
        type="file"
        accept=".pdf,.epub,.txt,.md"
        onChange={handleFileSelect}
      />
      {uploadMutation.isPending && <Spinner />}
    </div>
  );
}
```

**验收标准**:
- ✓ 可选择文件
- ✓ 显示上传进度
- ✓ 上传成功后跳转

---

### [P1-009] 实现 PDF 渲染组件

**文件**: `frontend/components/reader/DocumentViewer/PDFViewer.tsx`

```typescript
import { Document, Page, pdfjs } from 'react-pdf';
import { useVirtualizer } from '@tanstack/react-virtual';

pdfjs.GlobalWorkerOptions.workerSrc = `//unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.js`;

export function PDFViewer({ fileUrl, onPageChange }: PDFViewerProps) {
  const [numPages, setNumPages] = useState(0);
  const [scale, setScale] = useState(1.0);
  const parentRef = useRef<HTMLDivElement>(null);

  // 虚拟滚动优化
  const rowVirtualizer = useVirtualizer({
    count: numPages,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 800,
    overscan: 2,
  });

  return (
    <div ref={parentRef} className="pdf-viewer overflow-auto h-full">
      <Document
        file={fileUrl}
        onLoadSuccess={({ numPages }) => setNumPages(numPages)}
      >
        {rowVirtualizer.getVirtualItems().map((virtualRow) => (
          <Page
            key={virtualRow.index}
            pageNumber={virtualRow.index + 1}
            scale={scale}
          />
        ))}
      </Document>
    </div>
  );
}
```

**验收标准**:
- ✓ 可正确渲染 PDF
- ✓ 支持滚动和缩放
- ✓ 虚拟滚动性能优化生效

---

### [P1-010] [P] 实现 EPUB 渲染组件

**文件**: `frontend/components/reader/DocumentViewer/EPUBViewer.tsx`

```typescript
import ePub from 'epubjs';

export function EPUBViewer({ fileUrl }: EPUBViewerProps) {
  const viewerRef = useRef<HTMLDivElement>(null);
  const bookRef = useRef<any>(null);

  useEffect(() => {
    if (!viewerRef.current) return;

    const book = ePub(fileUrl);
    const rendition = book.renderTo(viewerRef.current, {
      width: '100%',
      height: '100%',
    });

    rendition.display();
    bookRef.current = book;

    return () => book.destroy();
  }, [fileUrl]);

  return <div ref={viewerRef} className="epub-viewer" />;
}
```

**验收标准**:
- ✓ 可正确渲染 EPUB
- ✓ 支持翻页

---

### [P1-011] 实现阅读进度保存

**文件**: `backend/app/api/v1/documents.py`

```python
@router.patch("/{document_id}/progress")
async def update_reading_progress(
    document_id: str,
    progress: ReadingProgressUpdate,
    db: AsyncSession = Depends(get_db)
):
    document = await db.get(Document, document_id)
    document.current_page = progress.current_page
    document.scroll_position = progress.scroll_position
    document.last_read_at = datetime.utcnow()

    await db.commit()
    return {"success": True}
```

**前端**: 每 30 秒自动保存一次进度

**验收标准**:
- ✓ 滚动时自动保存进度
- ✓ 下次打开恢复到上次位置

---

### [P1-012] 实现 LLM 客户端

**文件**: `backend/app/core/ai/llm_client.py`

```python
from langchain.chat_models import ChatOpenAI

class LLMClient:
    def __init__(self, provider: str = "openai"):
        if provider == "openai":
            self.client = ChatOpenAI(
                model_name="gpt-4-turbo",
                temperature=0.3,
                max_tokens=1500,
            )
        elif provider == "ollama":
            from langchain.llms import Ollama
            self.client = Ollama(
                model="llama3.1:8b",
                base_url="http://localhost:11434"
            )

    async def generate(self, prompt: str) -> str:
        response = await self.client.agenerate([prompt])
        return response.generations[0][0].text
```

**验收标准**:
- ✓ 可调用 LLM API
- ✓ 支持 OpenAI 和 Ollama
- ✓ 错误处理完善

---

### [P1-013] 实现文档摘要生成

**文件**: `backend/app/core/ai/summarizer.py`

```python
class DocumentSummarizer:
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    async def generate_summary(self, document_content: str) -> Dict:
        # 截断过长文本
        truncated = self._truncate(document_content, max_tokens=8000)

        prompt = f"""你是专业的文档分析助手。请阅读以下文档并生成摘要。

文档内容:
{truncated}

请按以下格式输出：

## 文档主题
(一句话概括，不超过50字)

## 核心论点
1. (第一个论点，不超过100字)
2. (第二个论点，不超过100字)
3. (第三个论点，不超过100字)

## 关键结论
1. (第一个结论，不超过80字)
2. (第二个结论，不超过80字)

## 重点提炼
1. (第一个重点，不超过50字)
2. (第二个重点，不超过50字)
3. (第三个重点，不超过50字)
"""

        response = await self.llm.generate(prompt)
        return self._parse_summary(response)
```

**API 端点**: `POST /api/v1/documents/{document_id}/summary`

**验收标准**:
- ✓ 可生成摘要 (300-500 字)
- ✓ 包含主题、论点、结论、重点
- ✓ 响应时间 < 3 秒

---

### [P1-014] 实现摘要缓存

**文件**: `backend/app/api/v1/ai.py`

```python
@router.post("/documents/{document_id}/summary")
async def generate_summary(
    document_id: str,
    cache: CacheManager = Depends(get_cache),
    db: AsyncSession = Depends(get_db)
):
    # 1. 检查缓存
    document = await db.get(Document, document_id)
    cache_key = f"summary:{document.file_hash}"

    cached = await cache.get(cache_key)
    if cached:
        return json.loads(cached)

    # 2. 生成摘要
    summarizer = DocumentSummarizer(llm_client)
    summary = await summarizer.generate_summary(document.parsed_content)

    # 3. 写入缓存 (24小时)
    await cache.set(cache_key, json.dumps(summary), expire=86400)

    return summary
```

**验收标准**:
- ✓ 相同文档不重复生成
- ✓ 缓存命中率 > 80%

---

### [P1-015] 实现前端摘要显示组件

**文件**: `frontend/components/chat/SummaryCard.tsx`

```typescript
export function SummaryCard({ summary }: { summary: Summary }) {
  return (
    <div className="summary-card p-4 border rounded-lg">
      <h3 className="text-lg font-bold mb-2">📄 文档摘要</h3>

      <div className="topic mb-4">
        <span className="text-sm text-gray-500">主题：</span>
        <p>{summary.topic}</p>
      </div>

      <div className="core-points mb-4">
        <span className="text-sm text-gray-500">核心论点：</span>
        <ul className="list-disc pl-5">
          {summary.core_points.map((point, i) => (
            <li key={i}>{point}</li>
          ))}
        </ul>
      </div>

      <div className="highlights">
        <span className="text-sm text-gray-500">重点提炼：</span>
        {summary.highlights.map((highlight, i) => (
          <HighlightCard key={i} highlight={highlight} />
        ))}
      </div>
    </div>
  );
}
```

**验收标准**:
- ✓ 摘要正确显示
- ✓ 样式美观

---

### [P1-016] 实现重点定位功能

**文件**: `frontend/components/chat/HighlightCard.tsx`

```typescript
export function HighlightCard({ highlight }: { highlight: Highlight }) {
  const handleClick = () => {
    // 滚动到原文位置
    const element = document.querySelector(`[data-page="${highlight.page}"]`);
    element?.scrollIntoView({ behavior: 'smooth' });

    // 高亮文本
    highlightText(highlight.start, highlight.end);

    // 3秒后移除高亮
    setTimeout(() => removeHighlight(), 3000);
  };

  return (
    <div
      className="highlight-card cursor-pointer hover:bg-gray-100 p-2 rounded"
      onClick={handleClick}
    >
      {highlight.text}
    </div>
  );
}
```

**验收标准**:
- ✓ 点击重点卡片可跳转到原文
- ✓ 原文高亮显示
- ✓ 3秒后高亮消失

---

### [P1-VERIFY] 验证 P1 功能完整性

**测试场景**:

1. **上传并阅读文档**:
   - 上传 5MB PDF 文件
   - 验证 2 秒内加载完成
   - 验证文档正确渲染
   - 验证滚动和缩放

2. **生成摘要**:
   - 点击"生成摘要"按钮
   - 验证 3 秒内返回结果
   - 验证摘要包含主题、论点、结论、重点
   - 验证格式正确

3. **重点定位**:
   - 点击重点卡片
   - 验证跳转到原文位置
   - 验证文本高亮

4. **边缘情况**:
   - 上传不支持的格式 → 显示错误提示
   - 上传 > 50MB 文件 → 显示警告
   - AI 服务不可用 → 显示友好错误

**验收标准**:
- ✓ 所有场景通过
- ✓ E2E 测试通过
- ✓ 性能指标达标

---

## Phase 3: P2 用户故事 - 智能对话与引导式问答

**目标**: 用户可以与 AI 对话，AI 主动提出引导性问题

**估时**: 4-5 天

**依赖**: P1 功能完成

---

### [P2-001] 实现文本向量化和存储

**文件**: `backend/app/core/ai/embeddings.py`

```python
from sentence_transformers import SentenceTransformer
from chromadb import Client

class EmbeddingService:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.chroma = Client()
        self.collection = self.chroma.get_or_create_collection("documents")

    async def generate_embeddings(self, document_id: str, text_chunks: List[str]):
        embeddings = self.model.encode(text_chunks)

        self.collection.add(
            embeddings=embeddings.tolist(),
            documents=text_chunks,
            metadatas=[{"document_id": document_id, "chunk_index": i}
                       for i in range(len(text_chunks))],
            ids=[f"{document_id}_{i}" for i in range(len(text_chunks))]
        )
```

**Celery 任务**: 文档上传后异步生成 embeddings

**验收标准**:
- ✓ 可生成文本向量
- ✓ 存储到 ChromaDB
- ✓ 支持语义搜索

---

### [P2-002] 实现 RAG 问答引擎

**文件**: `backend/app/core/ai/qa_engine.py`

```python
class QAEngine:
    def __init__(self, llm_client: LLMClient, embedding_service: EmbeddingService):
        self.llm = llm_client
        self.embeddings = embedding_service

    async def answer_question(
        self,
        question: str,
        document_id: str,
        chat_history: List[Dict] = []
    ) -> Dict:
        # 1. 检索相关段落
        results = self.embeddings.collection.query(
            query_texts=[question],
            where={"document_id": document_id},
            n_results=3
        )

        context = "\n\n".join(results["documents"][0])

        # 2. 构建 Prompt
        history_text = self._format_history(chat_history[-10:])

        prompt = f"""你是智能阅读助手。请基于以下文档内容回答用户问题。

文档相关段落：
{context}

历史对话：
{history_text}

用户问题：{question}

回答要求：
1. 如果文档中包含答案，请基于原文回答并引用相关段落
2. 如果文档中未提及，请明确说明"文档中未找到相关内容"
3. 回答简洁明了，不超过200字

请回答："""

        response = await self.llm.generate(prompt)

        return {
            "answer": response,
            "sources": [
                {
                    "text": doc,
                    "metadata": meta
                }
                for doc, meta in zip(results["documents"][0], results["metadatas"][0])
            ]
        }
```

**API 端点**: `POST /api/v1/documents/{document_id}/qa`

**验收标准**:
- ✓ 可基于文档回答问题
- ✓ 引用原文位置
- ✓ 响应时间 < 2 秒
- ✓ 支持多轮对话

---

### [P2-003] 实现引导性问题生成

**文件**: `backend/app/core/ai/question_generator.py`

```python
class QuestionGenerator:
    async def generate_guiding_questions(self, summary: Dict) -> List[str]:
        prompt = f"""基于以下文档摘要，生成3个引导性问题帮助用户深入理解。

文档主题：{summary['topic']}
核心论点：{', '.join(summary['core_points'])}

要求：
1. 问题要有深度，引导用户思考
2. 问题之间有递进关系
3. 每个问题不超过50字

请生成3个问题："""

        response = await self.llm.generate(prompt)
        questions = self._parse_questions(response)
        return questions[:3]
```

**触发时机**: 摘要生成完成后自动生成

**验收标准**:
- ✓ 生成 3 个引导性问题
- ✓ 问题有深度
- ✓ 问题可点击

---

### [P2-004] 实现前端对话界面

**文件**: `frontend/components/chat/ChatInterface.tsx`

```typescript
export function ChatInterface({ documentId }: { documentId: string }) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const askQuestionMutation = useAskQuestion(documentId);

  const handleSend = async () => {
    if (!input.trim()) return;

    // 添加用户消息
    const userMessage = { role: 'user', content: input };
    setMessages([...messages, userMessage]);

    // 调用 API
    const response = await askQuestionMutation.mutateAsync({
      question: input,
      chat_history: messages,
    });

    // 添加 AI 回复
    const aiMessage = {
      role: 'assistant',
      content: response.answer,
      sources: response.sources
    };
    setMessages([...messages, userMessage, aiMessage]);

    setInput('');
  };

  return (
    <div className="chat-interface flex flex-col h-full">
      <MessageList messages={messages} />

      <div className="input-area flex gap-2 p-4">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && e.ctrlKey) {
              handleSend();
            }
          }}
          placeholder="输入问题... (Ctrl+Enter 发送)"
          className="flex-1 border rounded p-2"
        />
        <Button onClick={handleSend}>发送</Button>
      </div>
    </div>
  );
}
```

**验收标准**:
- ✓ 可输入问题
- ✓ 显示对话历史
- ✓ 快捷键发送 (Ctrl+Enter)
- ✓ 显示加载状态

---

### [P2-005] 实现引用原文跳转

**文件**: `frontend/components/chat/MessageItem.tsx`

```typescript
export function MessageItem({ message }: { message: Message }) {
  if (message.role === 'user') {
    return <div className="user-message">{message.content}</div>;
  }

  return (
    <div className="ai-message">
      <div className="content">{message.content}</div>

      {message.sources && message.sources.length > 0 && (
        <div className="sources mt-2">
          <span className="text-sm text-gray-500">引用来源：</span>
          {message.sources.map((source, i) => (
            <button
              key={i}
              className="source-link text-blue-500 underline"
              onClick={() => {
                // 跳转到原文位置
                jumpToDocument(source.metadata.page, source.metadata.position);
              }}
            >
              📖 查看原文
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
```

**验收标准**:
- ✓ 显示引用来源
- ✓ 点击可跳转到原文

---

### [P2-006] 实现引导性问题卡片

**文件**: `frontend/components/chat/GuidingQuestions.tsx`

```typescript
export function GuidingQuestions({ questions }: { questions: string[] }) {
  const handleQuestionClick = (question: string) => {
    // 自动填入输入框并发送
    sendMessage(question);
  };

  return (
    <div className="guiding-questions mt-4">
      <p className="text-sm text-gray-500 mb-2">💡 你可能想了解：</p>

      <div className="grid gap-2">
        {questions.map((q, i) => (
          <button
            key={i}
            className="question-card text-left p-3 border rounded hover:bg-gray-50"
            onClick={() => handleQuestionClick(q)}
          >
            {q}
          </button>
        ))}
      </div>
    </div>
  );
}
```

**验收标准**:
- ✓ 摘要生成后自动显示问题
- ✓ 点击问题自动发送

---

### [P2-007] 实现对话历史保存

**文件**: `backend/app/models/chat_message.py`

```python
class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(String(50), primary_key=True)
    document_id = Column(String(50), ForeignKey("documents.id"))
    user_id = Column(String(50), ForeignKey("users.id"))
    role = Column(Enum("user", "assistant"), nullable=False)
    content = Column(Text, nullable=False)
    sources = Column(JSON)  # AI 回答的引用来源
    created_at = Column(DateTime, default=datetime.utcnow)
```

**API**: 每条消息自动保存到数据库

**验收标准**:
- ✓ 对话历史持久化
- ✓ 刷新页面后历史仍在

---

### [P2-VERIFY] 验证 P2 功能完整性

**测试场景**:

1. **用户主动提问**:
   - 输入问题"什么是监督学习？"
   - 验证 2 秒内返回答案
   - 验证答案基于文档内容
   - 验证显示引用来源
   - 点击"查看原文"跳转正确

2. **AI 主动提问**:
   - 生成摘要后自动显示 3 个引导性问题
   - 点击问题自动发送
   - 验证 AI 展开深度解答

3. **多轮对话**:
   - 连续提问 3 次
   - 验证 AI 理解上下文
   - 验证对话历史正确保存

**验收标准**:
- ✓ 所有场景通过
- ✓ E2E 测试通过

---

## Phase 4: P3 用户故事 - 阅读标注与笔记管理

**目标**: 用户可以标注文档、添加批注、管理笔记

**估时**: 3-4 天

**依赖**: P1 功能完成

---

### [P3-001] 实现文本选择监听

**文件**: `frontend/components/reader/TextSelection.tsx`

```typescript
export function useTextSelection() {
  const [selection, setSelection] = useState<Selection | null>(null);
  const [position, setPosition] = useState({ x: 0, y: 0 });

  useEffect(() => {
    function handleSelectionChange() {
      const sel = window.getSelection();

      if (sel && sel.toString().trim().length > 0) {
        const range = sel.getRangeAt(0);
        const rect = range.getBoundingClientRect();

        setPosition({
          x: rect.left + rect.width / 2,
          y: rect.bottom + 10,
        });
        setSelection(sel);
      } else {
        setSelection(null);
      }
    }

    document.addEventListener('selectionchange', handleSelectionChange);
    return () => document.removeEventListener('selectionchange', handleSelectionChange);
  }, []);

  return { selection, position };
}
```

**验收标准**:
- ✓ 选中文本时触发事件
- ✓ 获取选中文本和位置

---

### [P3-002] 实现标注工具栏

**文件**: `frontend/components/reader/Annotation/AnnotationToolbar.tsx`

```typescript
export function AnnotationToolbar({ selection, position, onAnnotate }: AnnotationToolbarProps) {
  const [showNoteInput, setShowNoteInput] = useState(false);
  const [noteText, setNoteText] = useState('');

  if (!selection) return null;

  const handleHighlight = (color: 'yellow' | 'red') => {
    const text = selection.toString();
    const range = selection.getRangeAt(0);

    onAnnotate({
      type: color === 'yellow' ? 'highlight' : 'important',
      text,
      position: getSelectionPosition(range),
    });
  };

  const handleNote = () => {
    const text = selection.toString();
    const range = selection.getRangeAt(0);

    onAnnotate({
      type: 'note',
      text,
      note_content: noteText,
      position: getSelectionPosition(range),
    });

    setShowNoteInput(false);
    setNoteText('');
  };

  return (
    <div
      className="annotation-toolbar fixed z-50 bg-white shadow-lg rounded-lg p-2"
      style={{ left: position.x, top: position.y, transform: 'translateX(-50%)' }}
    >
      {!showNoteInput ? (
        <>
          <Button onClick={() => handleHighlight('yellow')}>🟡 高亮</Button>
          <Button onClick={() => handleHighlight('red')}>🔴 重点</Button>
          <Button onClick={() => setShowNoteInput(true)}>📝 批注</Button>
        </>
      ) : (
        <>
          <Input
            placeholder="输入批注..."
            value={noteText}
            onChange={(e) => setNoteText(e.target.value)}
            autoFocus
          />
          <Button onClick={handleNote}>保存</Button>
          <Button onClick={() => setShowNoteInput(false)}>取消</Button>
        </>
      )}
    </div>
  );
}
```

**验收标准**:
- ✓ 选中文本后弹出工具栏
- ✓ 可添加高亮、重点、批注
- ✓ 工具栏位置正确

---

### [P3-003] 实现标注保存 API

**文件**: `backend/app/api/v1/annotations.py`

```python
@router.post("")
async def create_annotation(
    annotation: AnnotationCreate,
    db: AsyncSession = Depends(get_db)
):
    new_annotation = Annotation(
        id=f"ann_{uuid4().hex[:12]}",
        document_id=annotation.document_id,
        user_id=annotation.user_id,
        type=annotation.type,
        position=annotation.position,
        selected_text=annotation.selected_text,
        note_content=annotation.note_content,
        color=annotation.color,
    )

    db.add(new_annotation)
    await db.commit()

    return new_annotation
```

**API 端点**:
- `POST /api/v1/annotations` - 创建标注
- `GET /api/v1/annotations?document_id=xxx` - 获取文档的所有标注
- `PATCH /api/v1/annotations/{annotation_id}` - 编辑批注
- `DELETE /api/v1/annotations/{annotation_id}` - 删除标注

**验收标准**:
- ✓ 标注立即保存
- ✓ 刷新页面后标注保留

---

### [P3-004] 实现标注渲染

**文件**: `frontend/components/reader/Annotation/AnnotationMarker.tsx`

```typescript
export function AnnotationMarker({ annotation }: { annotation: Annotation }) {
  const ref = useRef<HTMLSpanElement>(null);

  useEffect(() => {
    // 根据 position 定位到文档中的位置
    const element = document.querySelector(
      `[data-page="${annotation.position.page}"]`
    );

    if (element) {
      // 高亮文本
      highlightTextInElement(
        element,
        annotation.position.start,
        annotation.position.end,
        annotation.color
      );
    }
  }, [annotation]);

  if (annotation.type === 'note') {
    return (
      <span
        ref={ref}
        className="note-marker cursor-pointer"
        title={annotation.note_content}
      >
        📝
      </span>
    );
  }

  return null;
}
```

**验收标准**:
- ✓ 高亮正确显示
- ✓ 批注图标正确显示
- ✓ 鼠标悬停显示批注内容

---

### [P3-005] 实现笔记列表

**文件**: `frontend/components/notes/NotesList.tsx`

```typescript
export function NotesList({ documentId }: { documentId: string }) {
  const { data: annotations } = useAnnotations(documentId);

  return (
    <div className="notes-list p-4">
      <h3 className="text-lg font-bold mb-4">📝 我的笔记</h3>

      {annotations?.map((annotation) => (
        <NoteItem
          key={annotation.id}
          annotation={annotation}
          onLocate={() => jumpToAnnotation(annotation)}
          onEdit={(content) => updateAnnotation(annotation.id, content)}
          onDelete={() => deleteAnnotation(annotation.id)}
        />
      ))}
    </div>
  );
}
```

**验收标准**:
- ✓ 显示所有笔记
- ✓ 按时间倒序排列
- ✓ 可定位到原文

---

### [P3-006] 实现笔记导出

**文件**: `backend/app/api/v1/annotations.py`

```python
@router.get("/{document_id}/export")
async def export_annotations(
    document_id: str,
    format: str = "markdown",
    db: AsyncSession = Depends(get_db)
):
    document = await db.get(Document, document_id)
    annotations = await db.execute(
        select(Annotation).where(Annotation.document_id == document_id)
    )

    if format == "markdown":
        content = f"# {document.title}\n\n"
        for ann in annotations.scalars():
            content += f"## {ann.selected_text}\n\n"
            if ann.note_content:
                content += f"> {ann.note_content}\n\n"

        return Response(content, media_type="text/markdown")

    elif format == "pdf":
        # 生成 PDF
        pass
```

**验收标准**:
- ✓ 可导出为 Markdown
- ✓ 可导出为 PDF

---

### [P3-VERIFY] 验证 P3 功能完整性

**测试场景**:

1. **添加高亮**:
   - 选中文本
   - 点击"高亮"
   - 验证文本变为黄色
   - 刷新页面，验证高亮保留

2. **添加批注**:
   - 选中文本
   - 点击"批注"，输入"这段话很重要"
   - 验证显示 📝 图标
   - 鼠标悬停，验证显示批注内容

3. **笔记列表**:
   - 切换到笔记列表
   - 验证显示所有标注
   - 点击"定位"，验证跳转到原文

4. **笔记导出**:
   - 导出为 Markdown
   - 验证格式正确

**验收标准**:
- ✓ 所有场景通过

---

## Phase 5: P4 用户故事 - 学习记录与个性化推荐

**目标**: 记录用户行为，生成学习报告和个性化建议

**估时**: 4-5 天

**依赖**: P1-P3 数据积累

---

### [P4-001] 实现阅读会话追踪

**文件**: `backend/app/services/analytics_service.py`

```python
class AnalyticsService:
    async def start_session(self, user_id: str, document_id: str) -> str:
        session = ReadingSession(
            id=f"session_{uuid4().hex[:12]}",
            user_id=user_id,
            document_id=document_id,
            start_time=datetime.utcnow(),
        )
        await db.add(session)
        await db.commit()
        return session.id

    async def end_session(self, session_id: str, pages_read: List[int]):
        session = await db.get(ReadingSession, session_id)
        session.end_time = datetime.utcnow()
        session.duration_seconds = (session.end_time - session.start_time).seconds
        session.pages_read = pages_read
        await db.commit()
```

**验收标准**:
- ✓ 打开文档时创建会话
- ✓ 关闭文档时结束会话
- ✓ 记录阅读时长和页码

---

### [P4-002] 实现统计数据聚合

**文件**: `backend/app/api/v1/users.py`

```python
@router.get("/{user_id}/statistics")
async def get_user_statistics(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    # 累计阅读时长
    total_duration = await db.execute(
        select(func.sum(ReadingSession.duration_seconds))
        .where(ReadingSession.user_id == user_id)
    )

    # 已阅读文档数量
    document_count = await db.execute(
        select(func.count(Document.id))
        .where(Document.user_id == user_id)
    )

    # 提问次数
    question_count = await db.execute(
        select(func.count(ChatMessage.id))
        .where(ChatMessage.user_id == user_id, ChatMessage.role == "user")
    )

    # 笔记数量
    note_count = await db.execute(
        select(func.count(Annotation.id))
        .where(Annotation.user_id == user_id)
    )

    return {
        "total_reading_time": total_duration.scalar() or 0,
        "documents_read": document_count.scalar() or 0,
        "questions_asked": question_count.scalar() or 0,
        "notes_created": note_count.scalar() or 0,
    }
```

**验收标准**:
- ✓ 统计数据准确
- ✓ 查询性能良好

---

### [P4-003] 实现阅读趋势图表

**文件**: `frontend/components/profile/ReadingTrendChart.tsx`

```typescript
import { LineChart, Line, XAxis, YAxis, Tooltip } from 'recharts';

export function ReadingTrendChart({ userId }: { userId: string }) {
  const { data } = useReadingTrend(userId, { days: 7 });

  return (
    <div className="trend-chart">
      <h3 className="text-lg font-bold mb-4">📈 阅读趋势（近7天）</h3>

      <LineChart width={600} height={300} data={data}>
        <XAxis dataKey="date" />
        <YAxis />
        <Tooltip />
        <Line type="monotone" dataKey="minutes" stroke="#8884d8" />
      </LineChart>
    </div>
  );
}
```

**验收标准**:
- ✓ 图表正确显示
- ✓ 数据动态更新

---

### [P4-004] 实现个性化学习建议生成

**文件**: `backend/app/core/ai/recommendation.py`

```python
class RecommendationEngine:
    async def generate_suggestions(self, user_id: str) -> List[str]:
        # 分析用户行为数据
        user_data = await self._analyze_user_behavior(user_id)

        prompt = f"""基于以下用户学习数据，生成3条个性化学习建议：

阅读主题：{user_data['topics']}
提问频率最高的概念：{user_data['frequent_questions']}
标注较少的内容：{user_data['weak_areas']}

要求：
1. 建议具体可行
2. 符合用户学习路径
3. 每条建议不超过100字

请生成3条建议："""

        response = await self.llm.generate(prompt)
        return self._parse_suggestions(response)
```

**触发**: 每周日自动生成

**验收标准**:
- ✓ 建议个性化
- ✓ 建议可行

---

### [P4-005] 实现薄弱知识点识别

**文件**: `backend/app/services/weak_point_detector.py`

```python
class WeakPointDetector:
    async def detect_weak_points(self, user_id: str) -> List[str]:
        # 查询用户提问记录
        questions = await db.execute(
            select(ChatMessage.content)
            .where(ChatMessage.user_id == user_id, ChatMessage.role == "user")
        )

        # 统计提问频率
        question_topics = {}
        for q in questions.scalars():
            topics = self._extract_topics(q)
            for topic in topics:
                question_topics[topic] = question_topics.get(topic, 0) + 1

        # 查询标注记录
        annotations = await db.execute(
            select(Annotation.selected_text)
            .where(Annotation.user_id == user_id)
        )

        annotation_topics = set(self._extract_topics(a) for a in annotations.scalars())

        # 找出提问多但未标注的主题
        weak_points = [
            topic for topic, count in question_topics.items()
            if count >= 3 and topic not in annotation_topics
        ]

        return weak_points[:5]
```

**验收标准**:
- ✓ 准确识别薄弱点
- ✓ 提供复习建议

---

### [P4-006] 实现自测测验生成

**文件**: `backend/app/core/ai/quiz_generator.py`

```python
class QuizGenerator:
    async def generate_quiz(self, document_id: str, topic: str) -> List[Dict]:
        document = await db.get(Document, document_id)

        prompt = f"""基于以下文档内容，生成3道关于"{topic}"的选择题：

文档内容：
{document.parsed_content}

要求：
1. 题目有深度，考察理解而非记忆
2. 提供4个选项，1个正确答案
3. 提供详细解析

请生成3道题："""

        response = await self.llm.generate(prompt)
        return self._parse_quiz(response)
```

**验收标准**:
- ✓ 生成 3-5 道题
- ✓ 题目质量高
- ✓ 答题后显示解析

---

### [P4-007] 实现用户中心页面

**文件**: `frontend/app/profile/page.tsx`

```typescript
export default function ProfilePage() {
  const { data: stats } = useUserStatistics();
  const { data: suggestions } = useLearningsuggestions();
  const { data: weakPoints } = useWeakPoints();

  return (
    <div className="profile-page p-8">
      <h1 className="text-2xl font-bold mb-8">📊 学习中心</h1>

      {/* 统计卡片 */}
      <div className="grid grid-cols-4 gap-4 mb-8">
        <StatCard icon="📚" label="累计阅读时长" value={formatTime(stats.total_reading_time)} />
        <StatCard icon="📄" label="已阅读文档" value={stats.documents_read} />
        <StatCard icon="💬" label="提问次数" value={stats.questions_asked} />
        <StatCard icon="📝" label="笔记数量" value={stats.notes_created} />
      </div>

      {/* 阅读趋势图 */}
      <ReadingTrendChart />

      {/* 学习建议 */}
      <div className="suggestions mt-8">
        <h2 className="text-xl font-bold mb-4">💡 学习建议</h2>
        {suggestions?.map((s, i) => (
          <SuggestionCard key={i} suggestion={s} />
        ))}
      </div>

      {/* 薄弱知识点 */}
      {weakPoints.length > 0 && (
        <div className="weak-points mt-8">
          <h2 className="text-xl font-bold mb-4">⚠️ 薄弱知识点</h2>
          {weakPoints.map((point, i) => (
            <WeakPointCard key={i} point={point} onQuiz={() => startQuiz(point)} />
          ))}
        </div>
      )}
    </div>
  );
}
```

**验收标准**:
- ✓ 页面布局美观
- ✓ 数据实时更新

---

### [P4-VERIFY] 验证 P4 功能完整性

**测试场景**:

1. **统计数据**:
   - 使用应用 7 天
   - 验证统计数据准确
   - 验证趋势图正确

2. **学习建议**:
   - 验证每周日自动生成建议
   - 验证建议个性化

3. **薄弱知识点**:
   - 对某概念提问 3 次但不标注
   - 验证识别为薄弱点
   - 点击"生成测验"
   - 验证题目质量

**验收标准**:
- ✓ 所有场景通过

---

## Phase 6: 收尾与优化

**目标**: 完善细节，优化性能，准备发布

**估时**: 3-4 天

---

### [POLISH-001] 性能优化

**任务**:
- 前端代码分割和懒加载
- 图片懒加载
- Service Worker 缓存
- 数据库查询优化
- Redis 缓存热点数据

**验收标准**:
- ✓ Lighthouse 性能评分 > 90
- ✓ 首屏加载时间 < 3 秒
- ✓ API 响应时间 < 500ms (95th percentile)

---

### [POLISH-002] 无障碍审计

**任务**:
- 所有交互元素可键盘访问
- 添加 ARIA 标签
- 颜色对比度检查
- 屏幕阅读器测试

**验收标准**:
- ✓ axe DevTools 评分 > 90
- ✓ 通过 WCAG 2.1 AA 级标准
- ✓ 手动键盘导航测试通过

---

### [POLISH-003] E2E 测试完善

**文件**: `frontend/tests/e2e/complete-flow.spec.ts`

```typescript
test('complete reading flow', async ({ page }) => {
  // 1. 上传文档
  await page.goto('http://localhost:3000');
  await page.setInputFiles('input[type="file"]', 'tests/fixtures/sample.pdf');
  await page.click('button:has-text("上传文档")');

  // 2. 等待文档加载
  await expect(page.locator('.pdf-viewer')).toBeVisible({ timeout: 5000 });

  // 3. 生成摘要
  await page.click('button:has-text("生成摘要")');
  await expect(page.locator('.summary-card')).toBeVisible({ timeout: 5000 });

  // 4. 提问
  await page.fill('textarea', '这篇文档的主题是什么？');
  await page.press('textarea', 'Control+Enter');
  await expect(page.locator('.ai-response')).toBeVisible({ timeout: 3000 });

  // 5. 添加标注
  await page.selectText('.document-content', { start: 100, end: 200 });
  await page.click('button:has-text("高亮")');
  await expect(page.locator('.highlight-yellow')).toBeVisible();

  // 6. 查看用户中心
  await page.goto('/profile');
  await expect(page.locator('.stat-card')).toHaveCount(4);
});
```

**验收标准**:
- ✓ 所有用户流程测试通过
- ✓ 覆盖率 > 80%

---

### [POLISH-004] 错误处理和用户反馈

**任务**:
- 统一错误提示样式
- 添加 Toast 通知
- 网络错误重试机制
- 友好的 404/500 页面

**验收标准**:
- ✓ 所有错误场景有友好提示
- ✓ 用户操作有明确反馈

---

### [POLISH-005] 文档和部署指南

**文件**:
- `docs/development/setup.md` - 开发环境配置
- `docs/deployment/production.md` - 生产环境部署
- `docs/api/openapi.yaml` - API 文档
- `README.md` - 项目说明

**验收标准**:
- ✓ 文档完整清晰
- ✓ 新手可按文档部署成功

---

### [POLISH-006] 监控和日志

**任务**:
- 配置 Sentry / GlitchTip
- 配置 Prometheus + Grafana
- 日志格式统一
- 关键指标 Dashboard

**验收标准**:
- ✓ 错误自动上报
- ✓ 关键指标可视化

---

## Phase 7: 发布前验收

**目标**: 全面测试，确保质量

**估时**: 2 天

---

### [RELEASE-001] 完整功能验收

**测试清单**:

- [ ] P1 功能完整且稳定
  - [ ] 文档上传（PDF/EPUB/Markdown）
  - [ ] 文档渲染（滚动/缩放）
  - [ ] AI 摘要生成
  - [ ] 重点定位

- [ ] P2 功能完整且稳定
  - [ ] 智能问答
  - [ ] 引导性问题
  - [ ] 多轮对话
  - [ ] 引用跳转

- [ ] P3 功能完整且稳定
  - [ ] 文本标注（高亮/批注）
  - [ ] 笔记列表
  - [ ] 笔记导出

- [ ] P4 功能完整且稳定
  - [ ] 统计数据
  - [ ] 学习建议
  - [ ] 薄弱知识点
  - [ ] 自测测验

**验收标准**:
- ✓ 所有功能可用
- ✓ 无阻塞性 Bug

---

### [RELEASE-002] 性能验收

**指标**:
- [ ] 文档加载 < 2s (文件 < 10MB)
- [ ] AI 摘要响应 < 3s
- [ ] AI 问答响应 < 2s
- [ ] UI 交互延迟 < 100ms
- [ ] 应用启动时间 < 3s
- [ ] 内存占用 < 500MB

**验收标准**:
- ✓ 所有指标达标

---

### [RELEASE-003] 安全审计

**检查项**:
- [ ] SQL 注入防护
- [ ] XSS 防护
- [ ] CSRF 防护
- [ ] 文件上传安全
- [ ] API 认证和授权
- [ ] 敏感数据加密

**验收标准**:
- ✓ 无高危漏洞

---

### [RELEASE-004] 部署到生产环境

**步骤**:
1. 构建前端生产版本
2. 构建后端 Docker 镜像
3. 部署到 Cloudflare Pages + VPS
4. 配置域名和 SSL
5. 配置监控和告警
6. 数据库备份策略

**验收标准**:
- ✓ 生产环境稳定运行
- ✓ 监控和告警正常

---

## Summary

### 总体进度

| 阶段 | 任务数 | 估时 | 依赖 |
|------|--------|------|------|
| Phase 0: 项目初始化 | 5 | 1-2天 | - |
| Phase 1: 基础设施 | 7 | 3-4天 | Phase 0 |
| Phase 2: P1 功能 | 16 | 5-7天 | Phase 1 |
| Phase 3: P2 功能 | 7 | 4-5天 | Phase 2 |
| Phase 4: P3 功能 | 6 | 3-4天 | Phase 2 |
| Phase 5: P4 功能 | 7 | 4-5天 | Phase 2-4 |
| Phase 6: 收尾优化 | 6 | 3-4天 | Phase 2-5 |
| Phase 7: 发布验收 | 4 | 2天 | All |
| **总计** | **58** | **25-35天** | - |

### 并行开发建议

**Week 1-2**: 基础设施 + P1 前期
- Team A: 前端初始化 + 文档渲染
- Team B: 后端初始化 + 文档解析
- Team C: 数据库设计 + API

**Week 3-4**: P1 后期 + P2/P3 开始
- Team A: P2 对话界面
- Team B: P1 AI 摘要 + P2 问答引擎
- Team C: P3 标注系统

**Week 5**: P2/P3 完成 + P4 开始
- Team A: P4 前端界面
- Team B: P4 数据分析
- Team C: 优化和测试

**Week 6**: 收尾和发布
- All: 测试、优化、部署

### 关键里程碑

- **Day 7**: Phase 1 完成，基础设施就绪
- **Day 14**: P1 完成，MVP 可演示
- **Day 21**: P2 完成，核心功能就绪
- **Day 28**: P3-P4 完成，全功能版本
- **Day 35**: 发布到生产环境

---

**Status**: ✅ 任务列表已完成，可开始实施

**Next Step**: 使用 `/speckit.implement` 开始逐项实现
