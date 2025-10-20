# 📐 ReadPilot Parlant Agent 架构设计

## 一、整体架构图

```
┌─────────────────────────────────────────────────────────────┐
│                    ReadPilot System                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Coordinator  │──│ Summarizer   │  │ QA Agent     │     │
│  │    Agent     │  │    Agent     │  │              │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│         │                 │                  │             │
│         └─────────────────┴──────────────────┘             │
│                           │                                │
│         ┌─────────────────┴─────────────────┐              │
│         │                                   │              │
│  ┌──────▼───────┐                    ┌──────▼───────┐     │
│  │ Note Builder │                    │ Quiz Generator│     │
│  │    Agent     │                    │    Agent     │     │
│  └──────────────┘                    └──────────────┘     │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                   Shared Context Layer                      │
│  • User Reading History  • Document Embeddings             │
│  • User Preferences      • Session State                   │
└─────────────────────────────────────────────────────────────┘
```

## 二、核心 Agent 设计

### 🎯 1. Coordinator Agent（协调者）

**职责：** 路由用户请求、协调其他 Agent、维护会话状态

**核心能力：**
- 识别用户意图（摘要/问答/笔记/测验）
- 智能路由到对应的专业 Agent
- 维护会话上下文和用户偏好
- 记录用户行为轨迹

**关键 Guidelines：**
```python
# 规则1：文档总结路由
condition: "用户上传文档或请求总结"
action: "调用 Summarizer Agent 生成摘要，并更新阅读历史"
tools: [route_to_summarizer, update_reading_history]

# 规则2：问答路由
condition: "用户提出关于文档的问题"
action: "调用 QA Agent 进行深度问答，基于文档上下文回答"
tools: [route_to_qa, retrieve_document_context]

# 规则3：笔记生成路由
condition: "用户请求生成笔记或知识卡片"
action: "调用 Note Builder Agent 提炼关键信息"
tools: [route_to_note_builder]

# 规则4：测验生成路由
condition: "用户需要测验或检验理解"
action: "调用 Quiz Generator Agent 生成个性化题目"
tools: [route_to_quiz_generator, get_user_weak_points]
```

---

### 📝 2. Summarizer Agent（摘要专家）

**职责：** 文档分析、层级摘要生成、关键句提取

**核心能力：**
- 生成多层级摘要（Abstract → Key Insights → Concepts → Examples）
- 识别文档类型并调整摘要策略
- 提取关键句和重要概念
- 记忆用户摘要偏好（简洁/详细/可视化）

**关键 Guidelines：**
```python
# 规则1：生成层级摘要
condition: "收到完整文档"
action: """
按以下结构生成摘要：
1. 一句话概要（Abstract）
2. 3-5个核心要点（Key Insights）
3. 重要概念解释（Concepts）
4. 典型例子（Examples）
"""
tools: [extract_text, generate_hierarchical_summary]

# 规则2：文档类型自适应
condition: "文档是技术文档或学术论文"
action: "重点提取方法论、实验结果、结论，使用专业术语"
tools: [detect_document_type, technical_summary]

condition: "文档是叙事类或新闻类"
action: "提取主要事件、人物、时间线，使用通俗语言"
tools: [narrative_summary]

# 规则3：用户偏好学习
condition: "生成摘要后"
action: "记录用户对摘要的反馈（点赞/修改），优化后续风格"
tools: [collect_feedback, update_user_preference]
```

**输出示例：**
```json
{
  "abstract": "本文介绍量子计算的基本原理和应用前景",
  "key_insights": [
    "量子叠加态允许同时计算多个可能性",
    "量子纠缠实现远距离信息传输",
    "当前量子计算机面临退相干问题"
  ],
  "concepts": {
    "量子叠加": "量子系统可同时处于多个状态",
    "量子纠缠": "两个粒子状态相互关联的现象"
  },
  "examples": ["Shor算法分解大数", "量子密钥分发"]
}
```

---

### 💬 3. QA Agent（问答专家）

**职责：** 基于文档上下文的深度问答、多轮对话

**核心能力：**
- 语义检索相关文档段落
- 多轮对话记忆和上下文理解
- 引用原文并生成详细回答
- 主动提出引导性问题

**关键 Guidelines：**
```python
# 规则1：智能问答
condition: "用户提出问题"
action: """
1. 从向量数据库检索最相关的3-5个段落
2. 结合用户历史提问理解意图
3. 生成详细回答并引用原文
4. 如果不确定，说明并建议用户提供更多上下文
"""
tools: [semantic_search, generate_answer, cite_source]

# 规则2：多轮对话
condition: "用户继续追问或说'详细解释一下'"
action: "基于上一轮对话内容深入展开，保持连贯性"
tools: [get_conversation_history, deep_dive_answer]

# 规则3：引导式学习
condition: "回答完问题后"
action: "提出1-2个引导性问题，帮助用户深入思考"
tools: [generate_follow_up_questions]
```

**对话示例：**
```
用户: "量子纠缠是什么？"
QA Agent:
  "量子纠缠是指两个或多个量子粒子形成一个整体系统，无论它们相隔多远，
   一个粒子的状态改变会立即影响另一个粒子的状态。

   [参考] 第3页：'纠缠态粒子表现出非局域关联性...'

   💡 延伸思考：量子纠缠如何应用在量子通信中？"
```

---

### 🗒️ 4. Note Builder Agent（笔记生成器）

**职责：** 提炼关键信息、生成结构化笔记、知识卡片

**核心能力：**
- 生成结构化笔记（概念/定义/关系/记忆要点）
- 创建 Anki 风格的知识卡片
- 自动标签分类和知识图谱关联
- 支持多种笔记格式（Markdown/Notion/Obsidian）

**关键 Guidelines：**
```python
# 规则1：结构化笔记生成
condition: "用户请求生成笔记"
action: """
生成包含以下内容的笔记：
1. 核心概念（Concepts）
2. 关键公式/定义（Definitions）
3. 重要关系图（Relationships）
4. 记忆要点（Mnemonics）
"""
tools: [extract_key_concepts, create_flashcards]

# 规则2：知识图谱关联
condition: "生成笔记后"
action: "自动添加主题标签，并关联到用户的知识图谱"
tools: [generate_tags, link_to_knowledge_graph]
```

**输出示例：**
```markdown
## 量子计算基础

### 核心概念
- **量子比特（Qubit）**: 量子计算的基本单位，可处于 |0⟩、|1⟩ 或叠加态
- **量子叠加**: 系统同时处于多个状态的能力
- **量子纠缠**: 多个粒子关联的量子现象

### 关键公式
- 量子态表示: |ψ⟩ = α|0⟩ + β|1⟩
- 概率计算: P(0) = |α|², P(1) = |β|²

### 知识卡片
**Q**: 量子比特与经典比特的主要区别？
**A**: 量子比特可同时处于 0 和 1 的叠加态，而经典比特只能是 0 或 1

#量子计算 #量子物理 #计算机科学
```

---

### 🧩 5. Quiz Generator Agent（测验生成器）

**职责：** 生成个性化测验题、评估理解程度

**核心能力：**
- 生成多种题型（选择题/填空题/简答题）
- 基于用户薄弱点自适应出题
- 动态调整题目难度
- 提供详细解析和学习建议

**关键 Guidelines：**
```python
# 规则1：多样化题型生成
condition: "用户完成一段阅读"
action: """
生成以下类型题目（根据内容选择）：
1. 选择题（Multiple Choice）- 考察关键概念
2. 填空题（Fill in the Blank）- 考察细节记忆
3. 简答题（Short Answer）- 考察深度理解
"""
tools: [generate_mcq, generate_fill_blank, generate_short_answer]

# 规则2：自适应难度
condition: "用户有答题历史"
action: "优先生成用户薄弱知识点的题目，动态调整难度"
tools: [analyze_weak_points, adaptive_difficulty]
```

**测验示例：**
```json
{
  "question_type": "multiple_choice",
  "question": "量子叠加态的核心特征是什么？",
  "options": [
    "A. 粒子只能处于确定状态",
    "B. 粒子可同时处于多个状态",
    "C. 粒子状态不可测量",
    "D. 粒子运动速度超光速"
  ],
  "correct_answer": "B",
  "explanation": "量子叠加是指量子系统可以同时处于多个状态的线性组合...",
  "difficulty": "medium",
  "tags": ["量子叠加", "基础概念"]
}
```

---

## 三、上下文记忆系统设计

### 📦 Context Variables 结构

```python
context_schema = {
    # ===== 用户身份和偏好 =====
    "user_id": str,
    "user_name": str,
    "summary_style": str,  # "concise" | "detailed" | "visual"
    "difficulty_preference": str,  # "beginner" | "intermediate" | "advanced"
    "language": str,  # "zh" | "en"

    # ===== 当前文档状态 =====
    "current_document_id": str,
    "document_title": str,
    "document_type": str,  # "technical" | "narrative" | "academic" | "news"
    "last_summary": dict,
    "retrieved_passages": list,

    # ===== 对话历史（限制最近 10 轮）=====
    "conversation_history": [
        {
            "role": "user",
            "message": str,
            "timestamp": str
        },
        {
            "role": "assistant",
            "message": str,
            "agent": str,  # 哪个 Agent 回复的
            "timestamp": str
        }
    ],

    # ===== 学习轨迹 =====
    "reading_count": int,
    "total_questions_asked": int,
    "quiz_scores": [
        {
            "quiz_id": str,
            "score": float,
            "topics": list[str],
            "timestamp": str
        }
    ],
    "weak_topics": list[str],  # 用户薄弱的知识点
    "mastered_topics": list[str],  # 已掌握的知识点

    # ===== 生成的内容 =====
    "generated_flashcards": list[dict],
    "generated_notes": list[dict],
    "bookmarks": list[str],  # 用户标记的重要段落

    # ===== 时间戳 =====
    "session_start": str,
    "last_activity": str,
}
```

### 🔄 上下文持久化策略

```python
# 策略1：实时更新 - 高频操作
- 对话历史：每次问答后立即更新
- 当前文档状态：文档切换时更新
- 阅读进度：每分钟同步一次

# 策略2：批量同步 - 低频操作
- 用户偏好：用户主动修改时同步
- 学习统计：每完成一个学习单元同步
- 生成内容：用户保存时同步

# 策略3：会话结束 - 全量同步
- 会话结束时将所有 Context Variables 持久化到数据库
- 下次会话开始时从数据库恢复
```

---

## 四、Agent 协作流程

### 场景 1：用户上传文档并提问

```
用户: "帮我总结这篇关于量子计算的论文，然后解释一下量子纠缠"

┌──────────────────────────────────────────────────┐
│ Step 1: Coordinator Agent 识别意图               │
│    - 任务1: 文档总结                             │
│    - 任务2: 概念解释                             │
└────────┬─────────────────────────────────────────┘
         │
         ├─────► Step 2: Summarizer Agent
         │          - 文档分段和预处理
         │          - 识别为"学术论文"类型
         │          - 生成层级摘要
         │          - 提取关键概念: ["量子纠缠", "量子叠加", "量子算法"]
         │          - 更新 context.variables["last_summary"]
         │          ✅ 返回结构化摘要
         │
         └─────► Step 3: QA Agent
                    - 检测到用户问"量子纠缠"
                    - 从向量DB检索"量子纠缠"相关段落（Top 5）
                    - 结合 Step 2 的摘要上下文
                    - 生成详细解释（定义 + 例子 + 应用）
                    - 引用原文段落
                    - 提出引导性问题: "想了解量子纠缠在量子通信中的应用吗？"
                    ✅ 返回深度回答

返回给用户:
✅ 论文摘要（结构化、多层级）
✅ 量子纠缠详细解释（含引用）
✅ 引导性问题（激发深度思考）
```

### 场景 2：用户请求生成学习资料

```
用户: "基于这篇文章，帮我生成笔记和测验题"

┌──────────────────────────────────────────────────┐
│ Step 1: Coordinator Agent 并行调度               │
└────────┬─────────────────────────────────────────┘
         │
         ├─────► Step 2a: Note Builder Agent (并行)
         │          - 从 context["last_summary"] 获取摘要
         │          - 提取核心概念和定义
         │          - 生成知识卡片（Anki 格式）
         │          - 添加主题标签
         │          - 保存到 context["generated_notes"]
         │          ✅ 返回结构化笔记
         │
         └─────► Step 2b: Quiz Generator Agent (并行)
                    - 分析文档内容和难度
                    - 检查 context["weak_topics"] 用户薄弱点
                    - 生成 5 道题（2选择 + 2填空 + 1简答）
                    - 自适应难度调整
                    - 保存到 context["generated_quizzes"]
                    ✅ 返回测验题集

返回给用户:
✅ 结构化笔记（Markdown 格式）
✅ 知识卡片（5 张）
✅ 测验题（5 道，含解析）
```

---

## 五、技术架构实现

### 目录结构

```
backend/
├── main.py                          # FastAPI 主应用
├── config.py                        # 配置管理
├── requirements.txt                 # 依赖清单
│
├── agents/                          # Parlant Agents
│   ├── __init__.py
│   ├── coordinator.py               # 协调者 Agent
│   ├── summarizer.py                # 摘要 Agent
│   ├── qa.py                        # 问答 Agent
│   ├── note_builder.py              # 笔记 Agent
│   └── quiz_generator.py            # 测验 Agent
│
├── tools/                           # Parlant Tools
│   ├── __init__.py
│   ├── document_tools.py            # 文档处理
│   ├── vector_tools.py              # 向量检索
│   ├── context_tools.py             # 上下文管理
│   └── llm_tools.py                 # LLM 调用
│
├── models/                          # 数据模型
│   ├── __init__.py
│   ├── user.py                      # 用户模型
│   ├── document.py                  # 文档模型
│   └── session.py                   # 会话模型
│
├── services/                        # 业务服务
│   ├── __init__.py
│   ├── vector_service.py            # 向量数据库
│   ├── database_service.py          # 数据库服务
│   └── agent_service.py             # Agent 管理
│
└── api/                             # API 路由
    ├── __init__.py
    ├── chat.py                      # 聊天接口
    ├── documents.py                 # 文档管理
    └── users.py                     # 用户管理
```

### 核心技术栈

| 层级 | 技术选型 | 说明 |
|------|---------|------|
| **Agent 框架** | Parlant SDK | 多 Agent 协作、Guidelines、Memory |
| **Web 框架** | FastAPI | 异步、高性能、自动文档 |
| **LLM** | OpenAI API / Claude API | 文本生成、摘要、问答 |
| **向量数据库** | Pinecone / Qdrant | 语义检索、文档嵌入 |
| **关系数据库** | PostgreSQL | 用户数据、文档元数据 |
| **ORM** | SQLAlchemy | 数据库操作 |
| **数据验证** | Pydantic | 模型验证、配置管理 |
| **任务队列** | Celery (可选) | 异步任务处理 |

### API 设计

```python
# 1. 聊天接口（核心）
POST /api/chat
{
  "user_id": "user_123",
  "message": "帮我总结这篇文档",
  "document_id": "doc_456",
  "session_id": "session_789"  # 可选
}

# 2. 文档上传
POST /api/documents/upload
Content-Type: multipart/form-data
{
  "file": <binary>,
  "user_id": "user_123"
}

# 3. 获取笔记
GET /api/notes?user_id=user_123&document_id=doc_456

# 4. 获取测验
GET /api/quizzes?user_id=user_123&document_id=doc_456

# 5. 提交测验答案
POST /api/quizzes/submit
{
  "quiz_id": "quiz_789",
  "answers": [...]
}

# 6. 用户偏好设置
PUT /api/users/{user_id}/preferences
{
  "summary_style": "detailed",
  "difficulty_preference": "intermediate"
}
```

---

## 六、关键优势

| 特性 | 实现方式 | 用户价值 |
|------|---------|---------|
| **智能路由** | Coordinator Agent 统一分发 | 用户无需关心调用哪个功能，自然对话 |
| **上下文记忆** | Context Variables + 数据库持久化 | 记住用户偏好和学习轨迹，个性化体验 |
| **多轮对话** | QA Agent 维护对话历史 | 连贯的伴读体验，深度理解用户意图 |
| **个性化学习** | 基于历史答题生成针对性测验 | 高效复习薄弱点，提升学习效率 |
| **专业分工** | 每个 Agent 专注特定任务 | 更高质量的输出，可独立优化 |
| **可扩展性** | 模块化设计，工具可复用 | 快速添加新功能（如翻译 Agent） |

---

## 七、MVP 实施路线图

### Phase 1: 核心对话能力（2-3周）
- ✅ Coordinator Agent
- ✅ Summarizer Agent
- ✅ QA Agent
- ✅ 基础向量检索
- ✅ 会话管理

**交付物：** 用户可上传文档、获取摘要、进行问答

### Phase 2: 学习闭环（2-3周）
- ✅ Note Builder Agent
- ✅ Quiz Generator Agent
- ✅ 用户偏好系统
- ✅ 学习轨迹记录

**交付物：** 完整的"阅读-理解-记忆-测验"闭环

### Phase 3: 个性化优化（2周）
- ✅ 自适应难度系统
- ✅ 知识图谱关联
- ✅ 多文档关联阅读
- ✅ 性能监控

**交付物：** 高度个性化的伴读体验

### Phase 4: 扩展功能（长期）
- 📚 多模态支持（图像、表格识别）
- 🌐 多语言翻译 Agent
- 🧩 第三方集成（Notion/Obsidian 插件）
- ☁️ SaaS 多租户支持

---

## 八、监控和优化

### 关键指标

```python
# Agent 性能指标
{
  "agent_name": "QA Agent",
  "avg_response_time": 1.2,  # 秒
  "success_rate": 0.95,
  "user_satisfaction": 4.5,  # 1-5分
  "context_memory_usage": "512KB"
}

# 用户行为指标
{
  "daily_active_users": 1000,
  "avg_reading_time": 25,  # 分钟
  "questions_per_session": 8,
  "quiz_completion_rate": 0.75
}

# LLM 成本指标
{
  "daily_api_calls": 50000,
  "avg_tokens_per_call": 1500,
  "daily_cost_usd": 12.5
}
```

### 优化策略

1. **缓存策略** - 相似问题使用缓存答案
2. **模型选择** - 简单任务用小模型，复杂任务用大模型
3. **异步处理** - 非实时任务（如笔记生成）异步执行
4. **向量索引优化** - 定期重建索引，提升检索速度

---

## 九、安全和隐私

### 数据安全

- ✅ 用户文档加密存储
- ✅ API 鉴权（JWT Token）
- ✅ 敏感信息脱敏
- ✅ HTTPS 传输加密

### 隐私保护

- ✅ 用户数据隔离（多租户）
- ✅ 可选的数据删除
- ✅ 不向第三方共享用户数据
- ✅ 符合 GDPR/CCPA 规范

---

## 十、总结

ReadPilot 的 Parlant Agent 架构通过以下设计实现核心价值：

1. **多智能体协作** - 5个专业 Agent 分工明确，协同工作
2. **语义记忆系统** - 持续记忆用户偏好和学习轨迹
3. **教育闭环** - 理解 → 测试 → 反思 → 强化
4. **高扩展性** - 模块化设计，快速迭代新功能

**技术亮点：**
- 基于 Parlant Guidelines 的可控 AI 行为
- Context Variables 实现的跨 Agent 状态共享
- 向量检索 + LLM 的混合问答系统
- 自适应学习难度的智能测验

这套架构既满足 MVP 快速上线需求，又为未来的 SaaS 化和多模态扩展预留了空间。
