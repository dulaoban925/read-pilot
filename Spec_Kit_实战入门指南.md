# Spec Kit 实战入门指南：用规格驱动开发改变你的编程方式

## 前言

在 AI 辅助编程时代，我们常常陷入一个困境：让 AI 直接生成代码虽然快速,但往往缺乏系统性思考；而传统的需求文档又显得过于笨重。GitHub 推出的开源工具 Spec Kit 提供了一个优雅的解决方案——**规格驱动开发**（Spec-Driven Development），让你在需求与实现之间找到最佳平衡点。

本文将带你深入理解 Spec Kit 的核心理念,并通过实战演练掌握这一工具的使用方法。

## 一、什么是 Spec Kit?

Spec Kit 是 GitHub 官方开源的规格驱动开发工具包，由 Den Delimarsky 和 John Lam 维护。它的核心理念可以用官方文档中的一句话概括：

> "Spec-Driven Development flips the script on traditional software development...specifications become executable, directly generating working implementations"

简单来说，Spec Kit 让**规格说明书变得可执行**——你不再是写完文档后再开始编码，而是通过结构化的规格说明直接驱动 AI 生成高质量代码。

### 核心优势

1. **意图驱动**：关注"想要什么"而非"如何实现"
2. **结构化工作流**：从项目原则到任务拆解的完整路径
3. **AI 深度集成**：支持 Claude、GitHub Copilot、Gemini 等多种 AI 助手
4. **渐进式交付**：支持独立用户故事的并行开发

## 二、环境准备

### 系统要求

你需要准备以下环境：

- **操作系统**：Linux、macOS 或 Windows
- **Python**：3.11 或更高版本
- **Git**：用于版本控制
- **uv 包管理器**：Python 的现代化包管理工具
- **AI 编程助手**：Claude Code、GitHub Copilot、Gemini 或 Codebuddy CLI（任选其一）

### 安装步骤

使用 `uvx` 命令初始化项目是最推荐的方式：

```bash
uvx --from git+https://github.com/github/spec-kit.git specify init my-project
```

你可以通过 `--ai` 参数指定 AI 助手：

```bash
# 使用 Claude
uvx --from git+https://github.com/github/spec-kit.git specify init my-project --ai claude

# 使用 GitHub Copilot
uvx --from git+https://github.com/github/spec-kit.git specify init my-project --ai copilot

# 使用 Gemini
uvx --from git+https://github.com/github/spec-kit.git specify init my-project --ai gemini
```

**脚本类型选择**：

- Windows 系统默认使用 PowerShell（`.ps1`）
- Linux/macOS 默认使用 Shell（`.sh`）
- 可通过 `--script` 参数覆盖默认选择：

```bash
# 强制使用 Shell 脚本
uvx --from git+https://github.com/github/spec-kit.git specify init my-project --script sh

# 强制使用 PowerShell 脚本
uvx --from git+https://github.com/github/spec-kit.git specify init my-project --script ps
```

初始化完成后，系统会创建 `.specify/scripts` 目录，其中包含项目所需的脚本文件。

> 若为已有项目初始化 Spec Kit，项目名称使用点（.）替代，表示在当前目录下初始化

### Linux 用户注意事项

如果在 Linux 上遇到 Git 认证问题，官方文档提供了 Git Credential Manager 的安装脚本作为解决方案。

## 三、核心工作流：五步法则

Spec Kit 提供了五个核心命令，构成了完整的开发工作流。这些命令在你的 AI 助手中以斜杠命令的形式出现：

### 1. `/speckit.constitution` - 制定项目宪章

项目宪章是整个开发流程的"基本法",它定义了项目的核心原则和技术约束。根据源码中的 `memory/constitution.md` 模板，一个完整的宪章包含：

**核心结构**：

- **5 条核心原则**：定义项目的价值观和开发准则
- **附加要求与约束**：技术栈限制、性能要求等
- **流程与工作流指南**：代码审查、测试策略等
- **治理规则**：宪章权威性、修订流程、合规要求

**实战示例**：

假设你要开发一个阅读辅助应用，宪章可能包含：

```markdown
## Core Principles

### Principle 1: 用户隐私至上
用户的阅读数据和笔记必须完全本地存储，不得上传到云端，除非用户明确授权。

### Principle 2: 库优先策略
优先使用成熟的开源库而非自研，除非现有方案无法满足核心需求。

### Principle 3: 渐进增强
确保核心阅读功能在所有设备上可用，高级功能可根据设备能力渐进启用。
```

宪章的重要性在于：后续的技术规划（`/speckit.plan`）会自动检查是否违反了宪章原则，如有违反需要记录在"复杂度追踪表"中并给出合理理由。

### 2. `/speckit.specify` - 编写功能规格

这是整个流程中最关键的一步。根据 `templates/spec-template.md` 的结构，一份完整的功能规格包含三大强制部分：

#### 2.1 用户场景与测试（必填）

采用**优先级驱动**的用户故事格式：

```markdown
## P1: 基础文本阅读
**描述**：用户能够打开常见格式的文本文件并进行阅读

**优先级理由**：这是产品的最小可行版本（MVP），没有此功能产品无法使用

**独立测试**：在没有其他功能的情况下，单独测试文本显示的正确性

**验收场景**：
- **Given**: 用户已安装应用并打开主界面
- **When**: 用户选择一个 TXT 格式文件
- **Then**: 文件内容正确显示，支持滚动浏览，字体大小适中可读
```

**重点提示**：

- P1 必须是独立可测试的 MVP
- P2、P3 的功能应该能够在 P1 基础上独立添加
- 避免在此阶段提及具体技术实现

#### 2.2 功能需求（必填）

使用 `FR-###` 格式编号：

```markdown
## Functional Requirements

**FR-001**: 系统应支持打开 TXT、EPUB、PDF 三种格式的文件
**FR-002**: 阅读界面应提供字体大小调节功能（12px - 24px）
**FR-003**: 用户的阅读进度应自动保存，下次打开时恢复
```

#### 2.3 成功标准（必填）

使用 `SC-###` 格式编号，必须**可量化且技术无关**：

```markdown
## Success Criteria

**SC-001**: 90% 的用户能在 3 次点击内打开文件并开始阅读
**SC-002**: 文件打开时间不超过 2 秒（文件大小 < 10MB）
**SC-003**: 用户首周留存率达到 60%
```

**最佳实践**：

官方快速入门指南强调：

> "Be explicit about requirements. Avoid technical details in initial spec."

在这个阶段，你要专注于"**What**"和"**Why**"，而非"**How**"。不要写"使用 React 构建界面"，而是写"界面应响应用户操作，提供流畅的交互体验"。

### 3. `/speckit.plan` - 制定技术方案

规格通过验证后，使用此命令生成技术实现方案。根据 `templates/plan-template.md`，技术方案包含：

#### 3.1 技术上下文（需人工填写）

这是唯一需要你主动输入的部分：

```markdown
## Technical Context

- **Language**: Python 3.11
- **Primary Dependencies**: FastAPI, SQLAlchemy, Sentence-Transformers
- **Storage**: PostgreSQL + ChromaDB
- **Authentication**: JWT + OAuth2
- **Hosting**: Docker + AWS ECS
```

#### 3.2 宪章检查（自动生成）

系统会自动检查技术选型是否违反项目宪章。如有违反，需在"复杂度追踪表"中记录：

| 原则       | 违反描述         | 合理性说明                           |
| ---------- | ---------------- | ------------------------------------ |
| 库优先策略 | 自研向量检索算法 | 现有库无法满足离线运行的严格隐私要求 |

#### 3.3 项目结构（三选一）

模板提供三种预设结构：

**选项 A - 单体项目**：

```
src/
  ├── core/         # 核心业务逻辑
  ├── services/     # 服务层
  ├── models/       # 数据模型
  └── utils/        # 工具函数
```

**选项 B - Web 应用**：

```
frontend/           # React/Vue 前端
backend/            # API 后端
shared/             # 共享类型定义
```

**选项 C - 移动端 + API**：

```
mobile/             # iOS/Android 客户端
api/                # 后端 API
shared/             # 共享模型
```

同时，文档结构统一为：

```
specs/
  └── [###-feature-name]/
      ├── spec.md       # 功能规格
      ├── plan.md       # 技术方案
      ├── tasks.md      # 任务列表
      └── checklist.md  # 质量检查清单
```

### 4. `/speckit.tasks` - 生成任务列表

根据 `templates/tasks-template.md`，任务拆解遵循明确的阶段划分：

```markdown
## Phase 1: 项目初始化
- [SETUP-001] 创建项目目录结构
- [SETUP-002] 配置开发环境和依赖

## Phase 2: 基础设施（阻塞性前置任务）
- [FOUND-001] 实现数据库连接层
- [FOUND-002] 配置日志和错误处理

## Phase 3: P1 用户故事 - 基础文本阅读
**目标**: 用户能够打开并阅读 TXT 文件
**独立测试**: 在空白项目中，此功能应独立工作

- [P1-001] 实现文件选择器 (src/ui/file_picker.py)
- [P1-002] [P] 开发文本渲染组件 (src/ui/text_viewer.py)
- [P1-003] [P] 添加阅读进度保存逻辑 (src/services/progress.py)
- [P1-004] 验证 P1 功能完整性

## Phase 4: P2 用户故事 - PDF 支持
...

## Phase N: 收尾工作
- [POLISH-001] 性能优化
- [POLISH-002] 无障碍功能审计
```

**任务格式说明**：

- `[ID]`：任务唯一标识
- `[P]`：可并行执行标记
- 具体文件路径：明确实现位置
- 独立测试标准：每个用户故事的验证点

**关键特性**：

根据模板说明，这种拆解方式支持：

- **独立交付**：每个用户故事可单独完成和测试
- **并行开发**：标记 `[P]` 的任务可同时进行
- **渐进增强**：优先级低的功能不影响高优先级功能的交付

### 5. `/speckit.implement` - 执行实现

这是最后一步，由 AI 助手根据任务列表逐项实现代码。在这个阶段：

- AI 会严格按照任务列表顺序工作
- 每完成一个任务会进行检查点验证
- 你可以随时介入调整和审查
- 跨用户故事的依赖会被自动识别

## 四、实战案例：构建智能阅读助手

让我们通过一个完整案例演示整个流程。

### 4.1 初始化项目

```bash
uvx --from git+https://github.com/github/spec-kit.git specify init ReadPilot --ai claude
cd ReadPilot
```

### 4.2 制定宪章

在 AI 助手中输入：

```
/speckit.constitution

我要构建一个 AI 阅读助手 ReadPilot，请帮我制定项目宪章。核心原则：
1. 隐私优先 - 用户数据本地存储
2. 性能优先 - 文档处理响应时间 < 2s
3. 可扩展性 - 模块化架构支持插件系统
4. 可访问性 - 支持屏幕阅读器和键盘导航
5. 简约设计 - 界面简洁，避免功能堆砌
```

AI 会生成完整的宪章文档，包括治理规则和修订流程。

### 4.3 编写功能规格

```
/speckit.specify

我要实现"智能摘要"功能。用户场景：
- P1: 用户能够对选中的文本段落生成摘要
- P2: 用户可以调整摘要的详细程度（简要/详细/要点）
- P3: 摘要结果可以保存为笔记

需求：
- 摘要生成时间不超过 3 秒
- 支持中英文内容
- 摘要长度为原文的 30%-50%

成功标准：
- 80% 的用户认为摘要准确捕捉了要点
- 用户每周至少使用此功能 5 次
```

AI 会按照标准模板生成规格文档，并提醒你补充缺失的验收场景和边缘情况。

### 4.4 制定技术方案

```
/speckit.plan

技术上下文：
- Language: Python 3.11
- Framework: FastAPI
- AI Model: Sentence-Transformers + GPT-4 API
- Storage: PostgreSQL
- Frontend: React + TypeScript
```

AI 会：

1. 检查是否违反宪章（如 GPT-4 API 可能违反"本地存储"原则）
2. 提出替代方案（如使用本地运行的 Llama 模型）
3. 生成项目结构建议
4. 输出完整的 `plan.md` 文档

### 4.5 拆解任务

```
/speckit.tasks
```

AI 会生成详细的任务列表，例如：

```markdown
## Phase 1: Setup
- [SETUP-001] Initialize Python project with Poetry
- [SETUP-002] Configure pre-commit hooks

## Phase 2: Foundation
- [FOUND-001] Implement text extraction service
- [FOUND-002] Setup model loading and caching

## Phase 3: P1 - Basic Summarization
**Goal**: User can generate summary from selected text
**Test**: Select 500-word paragraph → Click summarize → Get result in <3s

- [P1-001] Create text selection handler (frontend/src/components/TextSelector.tsx)
- [P1-002] [P] Implement summarization API endpoint (backend/api/summarize.py)
- [P1-003] [P] Add model inference logic (backend/services/summarizer.py)
- [P1-004] Connect frontend to API
- [P1-VERIFY] Test P1 acceptance criteria

## Phase 4: P2 - Adjustable Detail Level
...
```

### 4.6 开始实现

```
/speckit.implement
```

AI 会按任务顺序开始编码，每个阶段完成后会暂停让你审查。

## 五、进阶技巧

### 5.1 质量检查清单的使用

根据 `templates/checklist-template.md`，每个功能都应配备质量检查清单。清单格式为：

```markdown
# Quality Checklist: 智能摘要功能

## 功能完整性
- [ ] CHK001: 所有 P1 验收场景通过
- [ ] CHK002: 边缘情况处理（空文本、超长文本）

## 性能指标
- [ ] CHK003: 响应时间 < 3s（95th percentile）
- [ ] CHK004: 内存占用 < 500MB

## 安全性
- [ ] CHK005: 输入文本经过清洗，防止注入攻击
- [ ] CHK006: API 调用包含速率限制

## 可访问性
- [ ] CHK007: 支持键盘操作
- [ ] CHK008: 屏幕阅读器可识别
```

在 `implement` 阶段结束后，使用此清单逐项验证。

### 5.2 迭代与优化

官方快速入门指南强调：

> "Iterate on specifications. Validate before coding."

不要期望第一次就写出完美的规格。正确的流程是：

1. 写出初版 `spec.md`
2. 使用 `/speckit.plan` 检查可行性
3. 发现问题后回到 `/speckit.specify` 修改
4. 反复迭代直到规格清晰无歧义
5. 开始 `/speckit.tasks` 和 `/speckit.implement`

### 5.3 处理宪章违反

当技术方案违反宪章时，不要急于修改宪章。在 `plan.md` 的复杂度追踪表中诚实记录：

```markdown
| 原则 | 违反项 | 合理性分析 | 风险评估 | 批准状态 |
|------|--------|-----------|----------|----------|
| 隐私优先 | 使用 GPT-4 API | 本地模型质量不足，用户可选择性启用 | 数据泄露风险 | 待审批 |
```

这种透明度帮助团队做出明智的权衡决策。

### 5.4 并行开发的最佳实践

根据任务模板的说明，标记 `[P]` 的任务可以并行执行。实战中的建议：

- **前后端分离**：API 开发和 UI 开发可并行，通过 Mock 数据桥接
- **独立用户故事**：P1、P2、P3 之间互不依赖时可并行
- **测试优先**：先写测试用例，实现和测试同步进行

## 六、常见问题

### Q1: Spec Kit 与传统需求文档有何不同?

**传统文档**：写完后束之高阁，开发时很少参考，文档与代码脱节。

**Spec Kit**：规格文档是可执行的，AI 直接从中提取信息生成代码，强制保持文档与代码的一致性。

### Q2: 必须使用 AI 助手吗?

是的。Spec Kit 的核心价值在于将结构化规格转化为代码的自动化能力，这依赖 AI 的理解和生成能力。但你可以选择任何支持的 AI 助手（Claude、Copilot、Gemini 等）。

### Q3: 适合哪些项目规模?

根据官方文档的"0-to-1 Development"定位，Spec Kit 最适合：

- 新项目从零开始构建
- 中小型功能模块（1-4 周开发周期）
- 需要快速原型验证的探索性项目

对于大型遗留系统，建议从独立模块开始尝试。

### Q4: 如何处理频繁变更的需求?

Spec Kit 的优势正在于此：

1. 需求变更时，首先修改 `spec.md`
2. 重新运行 `/speckit.plan` 评估影响
3. 更新 `tasks.md` 中受影响的任务
4. 只重新实现变更部分

由于用户故事的独立性，局部变更不会引发级联崩溃。

## 七、总结

Spec Kit 的精髓在于将软件开发的思考过程结构化：

1. **宪章**定义价值观和约束
2. **规格**描述要解决的问题
3. **方案**选择技术路径
4. **任务**拆解执行步骤
5. **实现**交给 AI 完成

这个流程强制你**先思考再动手**，避免了直接让 AI 生成代码时常见的"看起来能跑但架构混乱"的问题。

官方文档中的一句话值得铭记：

> "Focus on functionality first, then moving to technical implementation."

当你习惯于用规格思考而非代码思考时，你会发现软件设计变得更清晰，团队沟通更高效，AI 生成的代码质量更高——这正是 Spec Kit 想要带给你的改变。

## 参考资源

- **官方仓库**：https://github.com/github/spec-kit
- **文档网站**：https://github.github.io/spec-kit/
- **许可协议**：MIT License
- **维护者**：Den Delimarsky, John Lam

---

_本文所有技术细节均基于 Spec Kit 官方源码和文档（截至 2025 年 1 月），包括 README.md、templates 目录下的模板文件、src/specify_cli 源码以及 docs 目录的官方指南。所有代码示例遵循官方模板规范。_
