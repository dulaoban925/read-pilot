# 数据模型：核心阅读体验 (Data Model: Core Reading Experience)

**功能特性 (Feature)**: 001-core-reading-experience
**日期 (Date)**: 2025-10-22
**状态 (Status)**: 已批准 (Approved)

本文档定义了核心阅读体验功能的数据模型设计，包括实体定义、关系、索引策略和状态机。

---

## 实体关系图 (Entity Relationship Diagram)

```
User (用户)
 ├──< documents (1:N)
 ├──< chat_sessions (1:N)
 └──< reading_histories (1:N)

Document (文档)
 ├──< document_chunks (1:N)
 ├──< chat_sessions (1:N)
 ├──< reading_histories (1:N)
 └──o summary (1:1, nullable)

ChatSession (对话会话)
 ├──> user (N:1)
 ├──> document (N:1, nullable)
 └──< messages (1:N)

Message (消息)
 └──> chat_session (N:1)

DocumentChunk (文档分块)
 └──> document (N:1)

Summary (摘要)
 └──> document (1:1)

ReadingHistory (阅读历史)
 ├──> user (N:1)
 └──> document (N:1)
```

---

## 1. User (用户)

**描述**: 系统用户账户

**字段 (Fields)**:

| 字段名 | 类型 | 约束 | 描述 |
|--------|------|------|------|
| id | UUID | PK | 用户唯一标识符 |
| email | String(255) | UNIQUE, NOT NULL | 邮箱地址（登录凭证） |
| password_hash | String(255) | NOT NULL | 密码哈希值 (bcrypt) |
| display_name | String(100) | NOT NULL | 显示名称 |
| preferences | JSONB | DEFAULT '{}' | 用户偏好设置（AI 模型选择、语言等） |
| is_active | Boolean | DEFAULT TRUE | 账户是否激活 |
| created_at | Timestamp | NOT NULL | 创建时间 |
| updated_at | Timestamp | NOT NULL | 更新时间 |
| last_login_at | Timestamp | NULLABLE | 最后登录时间 |

**索引 (Indexes)**:
- `idx_user_email`: UNIQUE INDEX ON (email)
- `idx_user_created_at`: INDEX ON (created_at DESC)

**验证规则 (Validation Rules)**:
- email: 符合 RFC 5322 邮箱格式
- password_hash: bcrypt 哈希，work factor = 12
- display_name: 2-100 字符，不包含特殊字符

**示例数据 (Example Data)**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "display_name": "张三",
  "preferences": {
    "language": "zh-CN",
    "ai_provider": "openai",
    "theme": "light"
  },
  "is_active": true,
  "created_at": "2025-10-22T10:00:00Z",
  "updated_at": "2025-10-22T10:00:00Z"
}
```

---

## 2. Document (文档)

**描述**: 用户上传的文档

**字段 (Fields)**:

| 字段名 | 类型 | 约束 | 描述 |
|--------|------|------|------|
| id | UUID | PK | 文档唯一标识符 |
| user_id | UUID | FK(User.id), NOT NULL | 所属用户 |
| title | String(500) | NOT NULL | 文档标题 |
| file_path | String(1000) | NOT NULL | 文件存储路径 |
| file_type | Enum | NOT NULL | 文件类型 (pdf/epub/docx/markdown) |
| file_size | BigInteger | NOT NULL | 文件大小（字节） |
| page_count | Integer | NULLABLE | 页数（PDF/EPUB） |
| word_count | Integer | NULLABLE | 字数 |
| language | String(10) | NULLABLE | 文档语言（自动检测） |
| processing_status | Enum | NOT NULL, DEFAULT 'pending' | 处理状态 |
| processing_error | Text | NULLABLE | 处理错误信息 |
| uploaded_at | Timestamp | NOT NULL | 上传时间 |
| processed_at | Timestamp | NULLABLE | 处理完成时间 |

**枚举类型 (Enum Types)**:
- `FileType`: pdf, epub, docx, markdown
- `ProcessingStatus`: pending, processing, completed, failed

**索引 (Indexes)**:
- `idx_document_user_id`: INDEX ON (user_id, uploaded_at DESC)
- `idx_document_status`: INDEX ON (processing_status) WHERE processing_status IN ('pending', 'processing')

**外键约束 (Foreign Key Constraints)**:
- `fk_document_user`: FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE

**验证规则 (Validation Rules)**:
- file_size: 0 < size ≤ 50MB (52,428,800 bytes)
- page_count: 1 ≤ page_count ≤ 1000
- file_type: 必须在枚举值中

**状态机 (State Machine)**:
```
pending → processing → completed
                    ↘ failed
```

**示例数据 (Example Data)**:
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "深入理解计算机系统.pdf",
  "file_path": "550e8400-e29b-41d4-a716-446655440000/660e8400-e29b-41d4-a716-446655440001.pdf",
  "file_type": "pdf",
  "file_size": 15728640,
  "page_count": 856,
  "word_count": 320000,
  "language": "zh-CN",
  "processing_status": "completed",
  "uploaded_at": "2025-10-22T10:30:00Z",
  "processed_at": "2025-10-22T10:31:00Z"
}
```

---

## 3. DocumentChunk (文档分块)

**描述**: 文档文本分块，用于向量搜索 (Vector Search)

**字段 (Fields)**:

| 字段名 | 类型 | 约束 | 描述 |
|--------|------|------|------|
| id | UUID | PK | 分块唯一标识符 |
| document_id | UUID | FK(Document.id), NOT NULL | 所属文档 |
| chunk_index | Integer | NOT NULL | 分块序号（从 0 开始） |
| content | Text | NOT NULL | 分块文本内容 |
| token_count | Integer | NOT NULL | Token 数量 |
| start_page | Integer | NULLABLE | 起始页码 |
| end_page | Integer | NULLABLE | 结束页码 |
| embedding_id | String(100) | NULLABLE | 向量数据库中的 ID |
| created_at | Timestamp | NOT NULL | 创建时间 |

**索引 (Indexes)**:
- `idx_chunk_document_id`: INDEX ON (document_id, chunk_index)
- `idx_chunk_embedding_id`: INDEX ON (embedding_id)

**外键约束 (Foreign Key Constraints)**:
- `fk_chunk_document`: FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE

**验证规则 (Validation Rules)**:
- token_count: 100 ≤ token_count ≤ 1000
- chunk_index: ≥ 0

**示例数据 (Example Data)**:
```json
{
  "id": "770e8400-e29b-41d4-a716-446655440002",
  "document_id": "660e8400-e29b-41d4-a716-446655440001",
  "chunk_index": 0,
  "content": "第一章 计算机系统漫游\n\n计算机系统是由硬件和系统软件组成的...",
  "token_count": 785,
  "start_page": 1,
  "end_page": 2,
  "embedding_id": "doc_660e8400_chunk_0",
  "created_at": "2025-10-22T10:31:00Z"
}
```

---

## 4. Summary (摘要)

**描述**: 文档的 AI 生成摘要

**字段 (Fields)**:

| 字段名 | 类型 | 约束 | 描述 |
|--------|------|------|------|
| id | UUID | PK | 摘要唯一标识符 |
| document_id | UUID | FK(Document.id), UNIQUE, NOT NULL | 所属文档 |
| abstract | Text | NOT NULL | 摘要概述 |
| key_insights | JSONB | NOT NULL | 关键见解（数组） |
| main_concepts | JSONB | NOT NULL | 主要概念（数组） |
| document_type | String(50) | NULLABLE | 文档类型（technical/narrative/academic） |
| depth_level | Enum | NOT NULL, DEFAULT 'detailed' | 摘要深度 |
| model_used | String(50) | NOT NULL | 使用的 AI 模型 |
| generated_at | Timestamp | NOT NULL | 生成时间 |
| updated_at | Timestamp | NOT NULL | 更新时间 |

**枚举类型 (Enum Types)**:
- `DepthLevel`: brief, detailed

**索引 (Indexes)**:
- `idx_summary_document_id`: UNIQUE INDEX ON (document_id)

**外键约束 (Foreign Key Constraints)**:
- `fk_summary_document`: FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE

**验证规则 (Validation Rules)**:
- abstract: 50-2000 字符
- key_insights: 数组长度 3-10
- main_concepts: 数组长度 3-15

**示例数据 (Example Data)**:
```json
{
  "id": "880e8400-e29b-41d4-a716-446655440003",
  "document_id": "660e8400-e29b-41d4-a716-446655440001",
  "abstract": "本书从程序员的视角详细阐述了计算机系统的本质概念，展示了这些概念如何影响应用程序的正确性、性能和实用性...",
  "key_insights": [
    "计算机系统不仅仅是硬件和软件的简单堆砌，而是一个层次化的抽象体系",
    "理解底层系统如何工作，可以帮助程序员编写更高效、更可靠的程序",
    "硬件和软件的协同设计是现代计算机系统的核心"
  ],
  "main_concepts": [
    "信息的表示和处理",
    "程序的机器级表示",
    "处理器体系结构",
    "存储器层次结构",
    "链接",
    "异常控制流",
    "虚拟内存",
    "系统级I/O",
    "网络编程",
    "并发编程"
  ],
  "document_type": "technical",
  "depth_level": "detailed",
  "model_used": "gpt-4o-mini",
  "generated_at": "2025-10-22T10:32:00Z",
  "updated_at": "2025-10-22T10:32:00Z"
}
```

---

## 5. ChatSession (对话会话)

**描述**: 用户与 AI 的对话会话

**字段 (Fields)**:

| 字段名 | 类型 | 约束 | 描述 |
|--------|------|------|------|
| id | UUID | PK | 会话唯一标识符 |
| user_id | UUID | FK(User.id), NOT NULL | 所属用户 |
| document_id | UUID | FK(Document.id), NULLABLE | 关联文档（可选） |
| title | String(200) | NOT NULL | 会话标题 |
| created_at | Timestamp | NOT NULL | 创建时间 |
| updated_at | Timestamp | NOT NULL | 更新时间 |

**索引 (Indexes)**:
- `idx_session_user_id`: INDEX ON (user_id, updated_at DESC)
- `idx_session_document_id`: INDEX ON (document_id) WHERE document_id IS NOT NULL

**外键约束 (Foreign Key Constraints)**:
- `fk_session_user`: FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
- `fk_session_document`: FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE SET NULL

**验证规则 (Validation Rules)**:
- title: 1-200 字符

**示例数据 (Example Data)**:
```json
{
  "id": "990e8400-e29b-41d4-a716-446655440004",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "document_id": "660e8400-e29b-41d4-a716-446655440001",
  "title": "关于第三章处理器体系结构的讨论",
  "created_at": "2025-10-22T11:00:00Z",
  "updated_at": "2025-10-22T11:15:00Z"
}
```

---

## 6. Message (消息)

**描述**: 对话会话中的单条消息

**字段 (Fields)**:

| 字段名 | 类型 | 约束 | 描述 |
|--------|------|------|------|
| id | UUID | PK | 消息唯一标识符 |
| session_id | UUID | FK(ChatSession.id), NOT NULL | 所属会话 |
| role | Enum | NOT NULL | 角色 (user/assistant) |
| content | Text | NOT NULL | 消息内容 |
| sources | JSONB | NULLABLE | 来源引用（文档分块 ID 和页码） |
| model_used | String(50) | NULLABLE | 使用的 AI 模型（assistant 消息） |
| token_count | Integer | NULLABLE | Token 使用量 |
| created_at | Timestamp | NOT NULL | 创建时间 |

**枚举类型 (Enum Types)**:
- `MessageRole`: user, assistant

**索引 (Indexes)**:
- `idx_message_session_id`: INDEX ON (session_id, created_at ASC)

**外键约束 (Foreign Key Constraints)**:
- `fk_message_session`: FOREIGN KEY (session_id) REFERENCES chat_sessions(id) ON DELETE CASCADE

**验证规则 (Validation Rules)**:
- content: 1-10000 字符
- sources: 数组，每个元素包含 {chunk_id, page, excerpt}

**示例数据 (Example Data)**:
```json
{
  "id": "aa0e8400-e29b-41d4-a716-446655440005",
  "session_id": "990e8400-e29b-41d4-a716-446655440004",
  "role": "user",
  "content": "请解释一下流水线的概念",
  "created_at": "2025-10-22T11:00:00Z"
}
```

```json
{
  "id": "bb0e8400-e29b-41d4-a716-446655440006",
  "session_id": "990e8400-e29b-41d4-a716-446655440004",
  "role": "assistant",
  "content": "流水线（Pipelining）是一种提高处理器性能的重要技术。它的核心思想是将指令的执行过程划分为多个阶段，每个阶段由不同的硬件单元处理...",
  "sources": [
    {
      "chunk_id": "770e8400-e29b-41d4-a716-446655440002",
      "page": 256,
      "excerpt": "流水线技术通过重叠执行多条指令的不同阶段..."
    }
  ],
  "model_used": "gpt-4o-mini",
  "token_count": 450,
  "created_at": "2025-10-22T11:00:05Z"
}
```

---

## 7. ReadingHistory (阅读历史)

**描述**: 用户的文档阅读记录

**字段 (Fields)**:

| 字段名 | 类型 | 约束 | 描述 |
|--------|------|------|------|
| id | UUID | PK | 记录唯一标识符 |
| user_id | UUID | FK(User.id), NOT NULL | 用户 ID |
| document_id | UUID | FK(Document.id), NOT NULL | 文档 ID |
| duration_seconds | Integer | NOT NULL, DEFAULT 0 | 阅读时长（秒） |
| last_page | Integer | NULLABLE | 最后阅读的页码 |
| progress_percentage | Float | NOT NULL, DEFAULT 0.0 | 阅读进度百分比 |
| completed | Boolean | NOT NULL, DEFAULT FALSE | 是否读完 |
| created_at | Timestamp | NOT NULL | 首次阅读时间 |
| updated_at | Timestamp | NOT NULL | 最后更新时间 |

**索引 (Indexes)**:
- `idx_history_user_document`: UNIQUE INDEX ON (user_id, document_id)
- `idx_history_updated_at`: INDEX ON (user_id, updated_at DESC)

**外键约束 (Foreign Key Constraints)**:
- `fk_history_user`: FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
- `fk_history_document`: FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE

**验证规则 (Validation Rules)**:
- duration_seconds: ≥ 0
- progress_percentage: 0.0 ≤ value ≤ 100.0
- completed: progress_percentage == 100.0 时自动设为 TRUE

**示例数据 (Example Data)**:
```json
{
  "id": "cc0e8400-e29b-41d4-a716-446655440007",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "document_id": "660e8400-e29b-41d4-a716-446655440001",
  "duration_seconds": 7200,
  "last_page": 256,
  "progress_percentage": 29.9,
  "completed": false,
  "created_at": "2025-10-22T10:35:00Z",
  "updated_at": "2025-10-22T12:35:00Z"
}
```

---

## 数据库约束总结

### 外键级联策略 (Foreign Key Cascade Strategies)

| 父表 | 子表 | 删除策略 |
|------|------|---------|
| User | Document | CASCADE (用户删除时删除所有文档) |
| User | ChatSession | CASCADE (用户删除时删除所有会话) |
| User | ReadingHistory | CASCADE (用户删除时删除阅读记录) |
| Document | DocumentChunk | CASCADE (文档删除时删除所有分块) |
| Document | Summary | CASCADE (文档删除时删除摘要) |
| Document | ChatSession | SET NULL (文档删除时会话保留但关联清空) |
| Document | ReadingHistory | CASCADE (文档删除时删除阅读记录) |
| ChatSession | Message | CASCADE (会话删除时删除所有消息) |

### 检查约束 (Check Constraints)

```sql
-- Document 表
ALTER TABLE documents ADD CONSTRAINT check_file_size
  CHECK (file_size > 0 AND file_size <= 52428800);

ALTER TABLE documents ADD CONSTRAINT check_page_count
  CHECK (page_count IS NULL OR (page_count >= 1 AND page_count <= 1000));

-- DocumentChunk 表
ALTER TABLE document_chunks ADD CONSTRAINT check_token_count
  CHECK (token_count >= 100 AND token_count <= 1000);

ALTER TABLE document_chunks ADD CONSTRAINT check_chunk_index
  CHECK (chunk_index >= 0);

-- ReadingHistory 表
ALTER TABLE reading_histories ADD CONSTRAINT check_progress
  CHECK (progress_percentage >= 0.0 AND progress_percentage <= 100.0);

ALTER TABLE reading_histories ADD CONSTRAINT check_duration
  CHECK (duration_seconds >= 0);
```

---

## 迁移脚本示例 (Migration Script Example)

```python
# alembic/versions/001_create_initial_tables.py

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

def upgrade():
    # 创建枚举类型
    op.execute("CREATE TYPE file_type AS ENUM ('pdf', 'epub', 'docx', 'markdown')")
    op.execute("CREATE TYPE processing_status AS ENUM ('pending', 'processing', 'completed', 'failed')")
    op.execute("CREATE TYPE depth_level AS ENUM ('brief', 'detailed')")
    op.execute("CREATE TYPE message_role AS ENUM ('user', 'assistant')")

    # 创建 users 表
    op.create_table(
        'users',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('display_name', sa.String(100), nullable=False),
        sa.Column('preferences', JSONB, default={}),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('last_login_at', sa.DateTime(timezone=True))
    )
    op.create_index('idx_user_email', 'users', ['email'], unique=True)

    # 其他表创建省略...

def downgrade():
    op.drop_table('users')
    op.execute("DROP TYPE IF EXISTS file_type CASCADE")
    # ...
```

---

## 数据一致性保证 (Data Consistency Guarantees)

### 触发器 (Triggers)

```sql
-- 自动更新 updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 自动标记阅读完成
CREATE OR REPLACE FUNCTION auto_mark_completed()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.progress_percentage >= 100.0 THEN
        NEW.completed = TRUE;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER auto_complete_reading BEFORE INSERT OR UPDATE ON reading_histories
    FOR EACH ROW EXECUTE FUNCTION auto_mark_completed();
```

---

## 数据备份策略 (Data Backup Strategy)

1. **全量备份 (Full Backup)**: 每日凌晨 2:00 执行 `pg_dump`
2. **增量备份 (Incremental Backup)**: 启用 WAL 归档，每小时备份
3. **保留策略 (Retention Policy)**:
   - 全量备份保留 30 天
   - 增量备份保留 7 天
4. **恢复测试 (Recovery Test)**: 每周执行一次恢复演练

---

## 性能优化建议 (Performance Optimization Recommendations)

1. **分区表 (Partitioning)**: 如果单表数据量超过 1000 万行，考虑按时间分区
   ```sql
   -- document_chunks 按 created_at 月度分区
   CREATE TABLE document_chunks_2025_10 PARTITION OF document_chunks
   FOR VALUES FROM ('2025-10-01') TO ('2025-11-01');
   ```

2. **物化视图 (Materialized Views)**: 用户统计数据
   ```sql
   CREATE MATERIALIZED VIEW user_stats AS
   SELECT
       user_id,
       COUNT(DISTINCT document_id) as total_documents,
       SUM(duration_seconds) as total_reading_time,
       COUNT(CASE WHEN completed THEN 1 END) as completed_count
   FROM reading_histories
   GROUP BY user_id;

   -- 每小时刷新
   REFRESH MATERIALIZED VIEW user_stats;
   ```

3. **查询优化 (Query Optimization)**: 使用 EXPLAIN ANALYZE 分析慢查询

---

## 向量数据库同步 (Vector Database Synchronization)

DocumentChunk 表中的 `embedding_id` 字段关联 ChromaDB 中的向量数据：

```python
# 同步逻辑
async def sync_chunk_to_vector_db(chunk: DocumentChunk):
    embedding = await generate_embedding(chunk.content)

    collection.add(
        ids=[str(chunk.id)],
        embeddings=[embedding],
        documents=[chunk.content],
        metadatas=[{
            "document_id": str(chunk.document_id),
            "chunk_index": chunk.chunk_index,
            "start_page": chunk.start_page,
            "end_page": chunk.end_page
        }]
    )

    chunk.embedding_id = str(chunk.id)
    await db.commit()
```

---

## 总结

本数据模型设计符合以下原则：

✅ **规范化 (Normalization)**: 满足第三范式，避免数据冗余
✅ **性能优化 (Performance Optimization)**: 合理索引，支持高并发查询
✅ **数据完整性 (Data Integrity)**: 外键约束 + 检查约束 + 触发器
✅ **可扩展性 (Extensibility)**: 使用 JSONB 存储灵活字段，支持未来扩展
✅ **审计追踪 (Audit Trail)**: 所有表包含时间戳字段

**下一步**: 生成 API 契约文档 (contracts/)
