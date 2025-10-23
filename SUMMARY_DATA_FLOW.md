# 摘要数据流转逻辑文档

## 数据流转概述

```
用户触发 → 后端生成 → 数据库存储 → API 转换 → 前端展示
```

## 1. 数据库模型 (AISummary)

**表名**: `ai_summaries`

**字段结构**:
```python
class AISummary(Base, TimestampMixin):
    id: str                          # 主键
    document_id: str                 # 关联文档ID
    summary_type: str                # 摘要类型 (full/chapter/section/custom)

    # 核心数据 - JSON 格式
    content: dict = {
        "abstract": "摘要文字",
        "key_insights": ["见解1", "见解2", ...],
        "main_concepts": ["概念1", "概念2", ...],
        "depth": "detailed"  # 或 "brief"
    }

    # 纯文本版本
    text: str                        # 格式化的纯文本摘要

    # AI 元数据
    ai_metadata: dict = {
        "model": "qwen-max",         # 使用的模型
        "depth": "detailed"          # 摘要深度
    }

    # 其他字段
    target_section: str              # 目标章节 (可选)
    guiding_questions: list          # 引导问题 (可选)
    created_at: datetime
    updated_at: datetime
```

## 2. 生成流程

### Step 1: 用户触发生成

**API 端点**: `POST /api/v1/documents/{id}/summarize`

**请求参数**:
```json
{
  "depth": "detailed"  // 或 "brief"
}
```

### Step 2: Celery 异步任务

任务: `generate_summary_task`

```python
def generate_summary_task(document_id: str, depth: str):
    # 1. 获取文档内容
    document = get_document(document_id)

    # 2. 调用 AI Service 生成摘要
    summary_data = ai_service.generate_summary(
        text=document.parsed_content,
        depth=depth
    )
    # summary_data = {
    #     "abstract": "...",
    #     "key_insights": [...],
    #     "main_concepts": [...],
    #     "model": "qwen-max",
    #     "depth": "detailed"
    # }

    # 3. 构造存储数据
    content = {
        "abstract": summary_data["abstract"],
        "key_insights": summary_data["key_insights"],
        "main_concepts": summary_data["main_concepts"],
        "depth": depth
    }

    text_version = format_as_text(content)  # 生成纯文本

    ai_metadata = {
        "model": summary_data["model"],
        "depth": depth
    }

    # 4. 保存到数据库
    summary = AISummary(
        id=uuid4(),
        document_id=document_id,
        summary_type="full",
        content=content,           # JSON
        text=text_version,         # 纯文本
        ai_metadata=ai_metadata    # JSON
    )
    db.add(summary)
    db.commit()
```

## 3. 数据获取流程

### Step 1: 前端请求摘要

**API 端点**: `GET /api/v1/documents/{id}/summary`

### Step 2: 后端查询数据库

```python
async def get_summary(document_id: str):
    # 1. 从数据库查询
    summary = await db.query(AISummary).filter(
        AISummary.document_id == document_id
    ).first()

    # 2. 转换为响应格式
    summary_response = SummaryResponse.from_ai_summary(summary)

    # 3. 返回 JSON
    return {
        "code": 200,
        "data": summary_response.model_dump()
    }
```

## 4. 数据转换层 (Schema)

### SummaryResponse Schema

**作用**: 将数据库模型转换为前端需要的格式

```python
class SummaryResponse(BaseModel):
    id: str
    document_id: str
    abstract: str              # 从 content["abstract"] 提取
    key_insights: List[str]    # 从 content["key_insights"] 提取
    main_concepts: List[str]   # 从 content["main_concepts"] 提取
    depth_level: str           # 从 content["depth"] 提取
    model_used: str            # 从 ai_metadata["model"] 提取
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_ai_summary(cls, summary: AISummary) -> 'SummaryResponse':
        """从 AISummary 模型创建响应对象"""
        content = summary.content or {}
        ai_metadata = summary.ai_metadata or {}

        return cls(
            id=summary.id,
            document_id=summary.document_id,
            abstract=content.get('abstract', ''),
            key_insights=content.get('key_insights', []),
            main_concepts=content.get('main_concepts', []),
            depth_level=content.get('depth', 'detailed'),
            model_used=ai_metadata.get('model', 'unknown'),
            created_at=summary.created_at,
            updated_at=summary.updated_at,
        )
```

### 转换逻辑

```
数据库 (AISummary)                    API 响应 (SummaryResponse)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
content: {                         →  abstract: "..."
  "abstract": "...",
  "key_insights": [...],           →  key_insights: [...]
  "main_concepts": [...],          →  main_concepts: [...]
  "depth": "detailed"              →  depth_level: "detailed"
}

ai_metadata: {                     →  model_used: "qwen-max"
  "model": "qwen-max",
  "depth": "detailed"
}

created_at: datetime               →  created_at: "2025-10-23T..."
updated_at: datetime               →  updated_at: "2025-10-23T..."
```

## 5. API 响应格式

### 成功响应

```json
{
  "code": 200,
  "message": "获取摘要成功",
  "data": {
    "id": "9b780b64-be9c-4529-980f-d64cda8d5ff6",
    "document_id": "4d1f430b-a8e9-41b3-837f-fa293dc4b3b4",
    "abstract": "该文档探讨了人工智能在现代医疗健康领域的应用潜力与挑战...",
    "key_insights": [
      "人工智能技术通过数据分析、模式识别和自动化决策支持...",
      "AI在医学影像分析领域已取得突破性进展...",
      "算法偏见是当前AI医疗应用面临的主要伦理挑战之一...",
      ...
    ],
    "main_concepts": [
      "人工智能在医疗中的应用",
      "医学影像分析",
      "电子健康记录（EHR）",
      "个性化医疗",
      "算法偏见",
      ...
    ],
    "depth_level": "detailed",
    "model_used": "qwen-max",
    "created_at": "2025-10-23T10:33:16.000Z",
    "updated_at": "2025-10-23T10:33:32.000Z"
  }
}
```

### 错误响应

```json
{
  "code": 404,
  "message": "摘要不存在，请先生成摘要",
  "data": null
}
```

## 6. 前端数据接收

### TypeScript 接口

```typescript
export interface Summary {
  id: string;
  document_id: string;
  abstract: string;
  key_insights: string[];
  main_concepts: string[];
  depth_level: 'brief' | 'detailed';
  model_used: string;
  created_at: string;
  updated_at: string;
}
```

### 使用 React Hook

```typescript
const { summary, isLoading, refetch } = useSummary({
  documentId: id,
  enabled: !!document && document.processing_status === 'completed',
});

// summary 对象直接匹配 API 响应格式
// 可以直接传递给 SummaryDisplay 组件
<SummaryDisplay summary={summary} />
```

## 7. 展示组件

### SummaryDisplay Component

```typescript
export const SummaryDisplay: React.FC<SummaryDisplayProps> = ({ summary }) => {
  return (
    <Card>
      <CardHeader>
        <CardTitle>文档摘要</CardTitle>
        <Badge>{summary.depth_level === 'detailed' ? '详细' : '简要'}</Badge>
        <Badge>{summary.model_used}</Badge>
      </CardHeader>

      <CardContent>
        {/* 抽象 */}
        <section>
          <h3>📝 摘要</h3>
          <p>{summary.abstract}</p>
        </section>

        {/* 关键见解 */}
        <section>
          <h3>💡 关键见解</h3>
          <ul>
            {summary.key_insights.map((insight, i) => (
              <li key={i}>{insight}</li>
            ))}
          </ul>
        </section>

        {/* 主要概念 */}
        <section>
          <h3>🔑 主要概念</h3>
          <div>{summary.main_concepts.join(', ')}</div>
        </section>
      </CardContent>
    </Card>
  );
};
```

## 8. 完整数据流图

```
┌─────────────────────────────────────────────────────────────┐
│ 1. 用户触发                                                  │
│    POST /api/v1/documents/{id}/summarize                    │
│    { "depth": "detailed" }                                  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. Celery 任务                                               │
│    - 获取文档内容                                            │
│    - 调用 Qwen AI 生成摘要                                   │
│    - 返回: { abstract, key_insights, main_concepts, model } │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. 数据整理                                                  │
│    content = {                                              │
│      "abstract": "...",                                     │
│      "key_insights": [...],                                 │
│      "main_concepts": [...],                                │
│      "depth": "detailed"                                    │
│    }                                                        │
│    ai_metadata = { "model": "qwen-max" }                   │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. 存储到数据库 (AISummary)                                 │
│    - id, document_id, summary_type                          │
│    - content (JSON)                                         │
│    - text (纯文本)                                          │
│    - ai_metadata (JSON)                                     │
│    - created_at, updated_at                                 │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. 前端请求                                                  │
│    GET /api/v1/documents/{id}/summary                       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. 后端查询 + 转换                                           │
│    summary = db.query(AISummary).first()                   │
│    response = SummaryResponse.from_ai_summary(summary)     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 7. API 响应 (扁平化格式)                                    │
│    {                                                        │
│      "id": "...",                                           │
│      "document_id": "...",                                  │
│      "abstract": "...",        ← 从 content 提取            │
│      "key_insights": [...],    ← 从 content 提取            │
│      "main_concepts": [...],   ← 从 content 提取            │
│      "depth_level": "detailed",← 从 content 提取            │
│      "model_used": "qwen-max", ← 从 ai_metadata 提取        │
│      "created_at": "...",                                   │
│      "updated_at": "..."                                    │
│    }                                                        │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 8. 前端接收并展示                                            │
│    useSummary() → Summary 对象                              │
│    SummaryDisplay 组件渲染                                  │
└─────────────────────────────────────────────────────────────┘
```

## 9. 关键设计决策

### 为什么使用 JSON 字段存储？

**优点**:
1. **灵活性**: 可以随时添加新字段而不需要数据库迁移
2. **结构化**: 保持数据的层次结构
3. **查询效率**: 单次查询获取所有数据

**缺点**:
1. **查询限制**: 无法直接在 SQL 中查询 JSON 内部字段
2. **索引**: JSON 字段难以建立索引

### 为什么需要转换层？

1. **解耦**: 数据库结构与 API 响应格式解耦
2. **灵活性**: 可以自由修改数据库结构而不影响 API
3. **清晰性**: 前端获得扁平化、易用的数据结构
4. **兼容性**: 不同版本的数据可以转换为统一格式

### 为什么保留 text 字段？

1. **备份**: 如果 JSON 解析失败，仍有纯文本可用
2. **全文搜索**: 可以在纯文本上建立全文索引
3. **导出**: 方便生成 PDF、Markdown 等格式

## 10. 故障处理

### JSON 解析失败

```python
content = summary.content or {}  # 如果为 None，使用空字典
abstract = content.get('abstract', '未生成摘要')  # 提供默认值
```

### 数据不完整

```python
key_insights = content.get('key_insights', [])  # 默认空列表
if not key_insights:
    # 可以从 text 字段提取或使用占位符
    key_insights = ["摘要数据不完整，请重新生成"]
```

### 模型信息缺失

```python
ai_metadata = summary.ai_metadata or {}
model_used = ai_metadata.get('model', 'unknown')  # 未知模型
```

## 11. 未来优化方向

1. **多版本支持**: 保存同一文档的多个摘要版本
2. **增量更新**: 只更新变化的部分
3. **智能缓存**: 基于文档内容的哈希值缓存
4. **结构化提取**: 自动识别并提取特定领域的结构化信息
5. **多语言支持**: 根据文档语言自动切换提示词

## 总结

整个数据流转的核心在于 **分离存储结构和 API 响应格式**：

- **存储**: 使用 JSON 灵活存储复杂数据
- **转换**: Schema 层负责数据转换
- **响应**: API 返回扁平化、类型明确的数据
- **展示**: 前端获得开箱即用的数据结构

这种设计既保证了灵活性，又维持了前后端的清晰接口。
