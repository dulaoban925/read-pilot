# ReadPilot - AI 阅读助手

让每个人都能拥有一个「懂自己、会共读」的 AI 伴读伙伴。

## 产品愿景

ReadPilot 是一个基于 AI 的智能阅读助手，通过理解用户阅读内容，自动生成摘要、提炼重点、提出引导性问题，并记录学习轨迹，打造一个持续进化的个性化阅读伴侣。

## 核心功能

- 📄 **文档阅读**: 支持 PDF、EPUB、Markdown、DOCX 等多种格式
- 🤖 **AI 摘要**: 自动生成文档摘要和重点提炼
- 💬 **智能问答**: 基于文档内容的互动式对话
- 📝 **标注笔记**: 高亮、批注、笔记管理
- 📊 **学习记录**: 阅读统计、个性化推荐、薄弱知识点识别

## 技术栈

### 前端
- **框架**: Next.js 15 + React 19 + TypeScript 5.7
- **UI**: Tailwind CSS 4.0 + Radix UI
- **状态管理**: Zustand 5.0
- **文档渲染**: react-pdf 9.0, epubjs

### 后端
- **框架**: FastAPI 0.115 + Python 3.12
- **数据库**: PostgreSQL 17 / SQLite 3.47
- **AI**: Ollama (本地) / OpenAI / Anthropic
- **向量数据库**: ChromaDB 0.5
- **任务队列**: Celery 5.4 + Redis 7.4

## 快速开始

### 前置要求

- Node.js 22 LTS
- Python 3.12+
- Docker 27+
- pnpm 9.14+

### 开发环境

1. 克隆项目

```bash
git clone https://github.com/yourusername/readpilot.git
cd readpilot
```

2. 启动开发环境

```bash
docker-compose up -d
```

3. 访问应用

- 前端: http://localhost:3000
- 后端 API: http://localhost:8000
- API 文档: http://localhost:8000/docs

## 项目结构

```
readpilot/
├── frontend/          # Next.js 前端应用
├── backend/           # FastAPI 后端应用
├── shared/            # 共享类型定义和常量
├── docs/              # 项目文档
├── scripts/           # 工具脚本
├── docker/            # Docker 配置
└── .specify/          # Spec Kit 规格文档
```

## 开发文档

- [功能规格](. specify/specs/001-core-reading-experience/spec.md)
- [技术方案](.specify/specs/001-core-reading-experience/plan.md)
- [任务列表](.specify/specs/001-core-reading-experience/tasks.md)
- [项目宪章](.specify/memory/constitution.md)

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

详见 [CONTRIBUTING.md](./CONTRIBUTING.md)
