# 🧠 ReadPilot - AI 伴读助手

> 让每个人都能拥有一个「懂自己、会共读」的 AI 伴读伙伴

ReadPilot 是一个基于 **Parlant 多智能体架构**的 AI 阅读助手，通过理解用户阅读内容，自动生成摘要、提炼重点、提出引导性问题，并记录学习轨迹，打造一个**持续进化的个性化阅读伴侣**。

## ✨ 核心特性

### 🤖 多智能体协作
- **Coordinator Agent**: 智能路由，理解用户意图并分配任务
- **Summarizer Agent**: 文档分析和层级摘要生成
- **QA Agent**: 基于上下文的深度问答
- **Note Builder Agent**: 结构化笔记和知识卡片生成
- **Quiz Generator Agent**: 个性化测验题目生成

### 🧠 上下文记忆系统
- 持续记忆用户偏好和阅读习惯
- 跨会话的学习轨迹追踪
- 智能识别薄弱知识点
- 自适应难度调整

### 📚 完整学习闭环
```
阅读文档 → AI 摘要 → 深度问答 → 生成笔记 → 测验巩固 → 反馈优化
```

## 🏗️ 技术架构

### 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| **前端** | Next.js + React | (待实现) |
| **后端** | FastAPI + Python | RESTful API |
| **AI 框架** | Parlant SDK | 多 Agent 协作 |
| **LLM** | OpenAI / Anthropic Claude | 文本理解和生成 |
| **向量数据库** | Pinecone / Qdrant | 语义检索 |
| **数据库** | PostgreSQL | 用户和文档数据 |

### 架构图

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
└─────────────────────────────────────────────────────────────┘
```

详细架构设计参见：[PARLANT_AGENT_STRUCTURE.md](./PARLANT_AGENT_STRUCTURE.md)

## 🚀 快速开始

### 前置要求

- Python 3.11+
- PostgreSQL 15+
- Redis (可选，用于缓存)
- 向量数据库 (Pinecone 或 Qdrant)
- OpenAI API Key 或 Anthropic API Key

### 安装步骤

#### 方式一：使用自动安装脚本（推荐）

```bash
git clone https://github.com/yourusername/ReadPilot.git
cd ReadPilot
./setup.sh
```

安装脚本会自动：

- ✅ 创建环境变量文件
- ✅ 设置 Python 虚拟环境
- ✅ 安装所有依赖
- ✅ 检查数据库配置

#### 方式二：手动安装

##### 1. 克隆项目

```bash
git clone https://github.com/yourusername/ReadPilot.git
cd ReadPilot
```

##### 2. 配置环境变量

**重要：** 项目有两个环境变量文件：

```bash
# 根目录 - 项目整体配置
cp .env.example .env

# backend 目录 - 后端详细配置
cp backend/.env.example backend/.env
```

编辑 `backend/.env`，填入必填配置：

```env
# LLM API
OPENAI_API_KEY=your-openai-api-key
# 或
ANTHROPIC_API_KEY=your-anthropic-api-key

# 数据库
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/readpilot

# 向量数据库 (二选一)
PINECONE_API_KEY=your-pinecone-api-key
# 或
QDRANT_URL=http://localhost:6333
```

#### 3. 安装后端依赖

```bash
cd backend
pip install -r requirements.txt
```

#### 4. 初始化数据库

```bash
# TODO: 添加数据库迁移脚本
# alembic upgrade head
```

#### 5. 启动后端服务

```bash
python main.py
```

后端服务将在 http://localhost:8000 启动

#### 6. 访问 API 文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📖 使用示例

### 1. 上传文档

```bash
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -F "file=@document.pdf" \
  -F "user_id=user_123" \
  -F "title=量子计算入门"
```

### 2. 与 AI 对话

```bash
curl -X POST "http://localhost:8000/api/v1/chat/" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "message": "帮我总结这篇文档",
    "document_id": "doc_456"
  }'
```

### 3. 获取文档摘要

```bash
curl "http://localhost:8000/api/v1/documents/doc_456/summary"
```

## 🎯 产品路线图

### Phase 1: MVP (当前)
- ✅ 多 Agent 架构设计
- ✅ 文档上传和处理
- ✅ 智能摘要生成
- ✅ 问答功能
- 🔄 笔记和测验生成

### Phase 2: 功能完善
- ⬜ 前端界面 (Next.js)
- ⬜ 用户系统和认证
- ⬜ 阅读计划和进度追踪
- ⬜ 知识图谱可视化

### Phase 3: 个性化
- ⬜ 自适应学习难度
- ⬜ 个性化推荐
- ⬜ 长期学习曲线追踪

### Phase 4: 扩展
- ⬜ Chrome 浏览器插件
- ⬜ Notion/Obsidian 集成
- ⬜ 多语言支持
- ⬜ SaaS 多租户版本

## 📚 文档

- [架构设计文档](./PARLANT_AGENT_STRUCTURE.md) - 详细的 Parlant Agent 架构
- [后端 README](./backend/README.md) - 后端开发指南
- [API 文档](http://localhost:8000/docs) - 运行后访问

## 🤝 贡献指南

欢迎贡献！请阅读 [贡献指南](./CONTRIBUTING.md) 了解详情。

### 开发流程

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 🐛 问题反馈

如果遇到问题，请[创建 Issue](https://github.com/yourusername/ReadPilot/issues)。

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](./LICENSE) 文件

## 🙏 致谢

- [Parlant](https://github.com/emcie-co/parlant) - AI Agent 框架
- [FastAPI](https://fastapi.tiangolo.com/) - Web 框架
- [OpenAI](https://openai.com/) - LLM API
- [Anthropic](https://www.anthropic.com/) - Claude API

## 📞 联系方式

- 项目主页: https://github.com/yourusername/ReadPilot
- 问题反馈: https://github.com/yourusername/ReadPilot/issues
- 邮箱: your.email@example.com

---

⭐ 如果这个项目对你有帮助，请给我们一个 Star！
