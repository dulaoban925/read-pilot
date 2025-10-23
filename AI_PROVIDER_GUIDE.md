# ReadPilot AI 提供商配置指南

ReadPilot 支持三种 AI 提供商,提供灵活的配置选项和自动降级机制。

## 支持的 AI 提供商

### 1. 阿里云千问 (Qwen) - 推荐

**优势**:
- ✅ 同时支持 LLM 和 Embedding 服务
- ✅ 国内访问速度快,无需代理
- ✅ 价格相对便宜
- ✅ 支持多种模型规格 (qwen-max, qwen-plus, qwen-turbo, qwen-flash)

**服务**:
- **LLM**: qwen-max, qwen-plus, qwen-turbo, qwen-flash
- **Embedding**: text-embedding-v1, text-embedding-v2, text-embedding-v3

**获取 API Key**: [阿里云 DashScope 控制台](https://dashscope.console.aliyun.com/)

### 2. OpenAI

**优势**:
- ✅ 最成熟的 AI 服务
- ✅ 强大的模型性能
- ✅ 同时支持 LLM 和 Embedding 服务

**服务**:
- **LLM**: gpt-4o, gpt-4o-mini, gpt-4-turbo, gpt-3.5-turbo
- **Embedding**: text-embedding-3-large, text-embedding-3-small, text-embedding-ada-002

**获取 API Key**: [OpenAI Platform](https://platform.openai.com/api-keys)

### 3. Anthropic

**优势**:
- ✅ Claude 模型在长文本理解方面表现优异
- ✅ 更好的安全对齐

**限制**:
- ⚠️ 不支持 Embedding (需要配合其他提供商)

**服务**:
- **LLM**: claude-3-5-sonnet, claude-3-opus, claude-3-sonnet, claude-3-haiku

**获取 API Key**: [Anthropic Console](https://console.anthropic.com/)

## 环境变量配置

### 基础配置 (.env)

```bash
# ===== AI/LLM Configuration =====
# 至少配置一个 API Key

# 阿里云千问 (推荐)
QWEN_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# OpenAI (可选 - 作为备用)
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Anthropic (可选)
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### LLM 服务配置

```bash
# 主要 LLM 提供商
PRIMARY_AI_PROVIDER=qwen  # qwen, openai, anthropic

# 降级 LLM 提供商 (主提供商失败时使用)
FALLBACK_AI_PROVIDER=openai  # qwen, openai, anthropic

# 默认 LLM 提供商和模型
LLM_PROVIDER=qwen
LLM_MODEL=qwen-max
```

### Embedding 服务配置

**重要**: Embedding 服务跟随 `PRIMARY_AI_PROVIDER` 配置,确保与 LLM 提供商一致:

1. **PRIMARY_AI_PROVIDER=qwen** → 使用 Qwen Embedding (需要 `QWEN_API_KEY`)
2. **PRIMARY_AI_PROVIDER=openai** → 使用 OpenAI Embedding (需要 `OPENAI_API_KEY`)
3. **PRIMARY_AI_PROVIDER=anthropic** → 降级到 OpenAI 或 Qwen (Anthropic 不支持 Embedding)

```bash
# Embedding 模型名称 (仅用于记录)
EMBEDDING_MODEL=text-embedding-v3
EMBEDDING_DIMENSION=1536
```

这样可以避免出现"使用 Qwen LLM 但调用 OpenAI Embedding"的不一致情况。

## 推荐配置方案

### 方案 1: 纯千问 (推荐 - 国内用户)

最简单的配置,只需一个 API Key:

```bash
QWEN_API_KEY=sk-xxxx
PRIMARY_AI_PROVIDER=qwen
FALLBACK_AI_PROVIDER=qwen
LLM_PROVIDER=qwen
LLM_MODEL=qwen-max
EMBEDDING_MODEL=text-embedding-v3
```

**优势**: 配置简单,速度快,成本低

### 方案 2: 千问 + OpenAI 备用 (推荐 - 追求稳定性)

主用千问,OpenAI 作为备用:

```bash
QWEN_API_KEY=sk-xxxx
OPENAI_API_KEY=sk-xxxx
PRIMARY_AI_PROVIDER=qwen
FALLBACK_AI_PROVIDER=openai
LLM_PROVIDER=qwen
LLM_MODEL=qwen-max
EMBEDDING_MODEL=text-embedding-v3
```

**优势**: 高可用性,自动降级

### 方案 3: 纯 OpenAI (国际用户)

如果在海外或有 OpenAI 额度:

```bash
OPENAI_API_KEY=sk-xxxx
PRIMARY_AI_PROVIDER=openai
FALLBACK_AI_PROVIDER=openai
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small
```

### 方案 4: Anthropic + OpenAI

使用 Claude 做 LLM,OpenAI 做 Embedding:

```bash
ANTHROPIC_API_KEY=sk-ant-xxxx
OPENAI_API_KEY=sk-xxxx
PRIMARY_AI_PROVIDER=anthropic
FALLBACK_AI_PROVIDER=openai
LLM_PROVIDER=anthropic
LLM_MODEL=claude-3-5-sonnet
EMBEDDING_MODEL=text-embedding-3-small
```

**注意**: Anthropic 不支持 Embedding,必须配置 OpenAI 或千问的 API Key

## 模型选择指南

### LLM 模型对比

| 提供商 | 模型 | 用途 | 速度 | 成本 | 质量 |
|--------|------|------|------|------|------|
| Qwen | qwen-flash | 快速响应 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| Qwen | qwen-turbo | 平衡选择 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Qwen | qwen-plus | 高质量 | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| Qwen | qwen-max | 最佳质量 | ⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| OpenAI | gpt-4o-mini | 经济实惠 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| OpenAI | gpt-4o | 最强性能 | ⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| Anthropic | claude-3-5-sonnet | 长文本理解 | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |

### Embedding 模型对比

| 提供商 | 模型 | 维度 | 性能 | 成本 |
|--------|------|------|------|------|
| Qwen | text-embedding-v3 | 1536 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| OpenAI | text-embedding-3-small | 1536 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| OpenAI | text-embedding-3-large | 3072 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |

## 架构说明

### LLM 服务流程

```
用户请求 (摘要/问答)
    ↓
AIService (backend/app/services/ai_service.py)
    ↓
检查 PRIMARY_AI_PROVIDER
    ↓
调用对应的 LLM Service:
- QwenLLMService (backend/app/core/ai/qwen_service.py)
- OpenAILLMService (backend/app/core/ai/openai_service.py)
- AnthropicLLMService (backend/app/core/ai/anthropic_service.py)
    ↓
如果失败,尝试 FALLBACK_AI_PROVIDER
    ↓
返回结果或抛出异常
```

### Embedding 服务流程

```
文档上传 → 分块
    ↓
Celery 任务: generate_embeddings
    ↓
get_embedding_service() (backend/app/core/ai/__init__.py)
    ↓
自动选择:
1. QWEN_API_KEY 存在? → QwenEmbeddingService
2. OPENAI_API_KEY 存在? → OpenAIEmbeddingService
3. 否则抛出异常
    ↓
生成向量 → 存储到 ChromaDB
```

## 故障排查

### 问题 1: Embedding 生成失败

**错误信息**: `No embedding service available`

**解决方案**: 至少配置 `QWEN_API_KEY` 或 `OPENAI_API_KEY` 其中之一

### 问题 2: 摘要生成失败

**错误信息**: `Unsupported LLM provider`

**解决方案**: 检查 `LLM_PROVIDER` 是否为 `qwen`, `openai`, 或 `anthropic`

### 问题 3: API Key 无效

**错误信息**: `AuthenticationError: invalid x-api-key`

**解决方案**:
1. 检查 API Key 是否正确复制 (注意空格和换行)
2. 确认 API Key 未过期
3. 验证账户余额是否充足

### 问题 4: 千问 API 访问超时

**解决方案**:
1. 检查网络连接
2. 如果使用代理,尝试关闭: `HTTP_PROXY='' HTTPS_PROXY=''`
3. 切换到备用提供商

## 成本估算

基于典型用例 (月活 1000 用户, 每用户 10 篇文档):

### 千问 (Qwen)

- **LLM** (qwen-max): ¥0.12/千token
  - 每篇文档摘要 (~2000 tokens): ¥0.24
  - 每月 10,000 篇: ¥2,400

- **Embedding** (text-embedding-v3): ¥0.0007/千token
  - 每篇文档 (~5000 tokens): ¥0.0035
  - 每月 10,000 篇: ¥35

**月总成本**: ~¥2,435

### OpenAI

- **LLM** (gpt-4o-mini): $0.15/1M tokens
  - 每篇文档摘要 (~2000 tokens): $0.0003
  - 每月 10,000 篇: $3

- **Embedding** (text-embedding-3-small): $0.02/1M tokens
  - 每篇文档 (~5000 tokens): $0.0001
  - 每月 10,000 篇: $1

**月总成本**: ~$4 (约 ¥28)

**建议**: OpenAI 在大规模使用时成本更低,但千问在小规模使用和国内环境下更有优势。

## 更多资源

- [阿里云 DashScope 文档](https://help.aliyun.com/zh/dashscope/)
- [OpenAI API 文档](https://platform.openai.com/docs)
- [Anthropic API 文档](https://docs.anthropic.com/)
- [ReadPilot 开发文档](./README.md)
