# 如何使用 Spec Kit 文档

## 关于 Spec Kit 命令

**重要提示**: Spec Kit 的命令行工具（如 `/speckit.implement`）在 Claude Code 环境中不可用。

这些文档是使用 Spec Kit 工具生成的规格文档，但你可以通过其他方式使用它们。

## 推荐的使用方式

### 方式 1: 直接查看任务列表

打开 [tasks.md](./specs/001-core-reading-experience/tasks.md) 查看所有任务，然后：

1. **选择要实现的任务**
   ```
   例如: [P1-001] 实现文档解析器接口
   ```

2. **直接请求 Claude 实现**
   ```
   请帮我实现 [P1-001] 文档解析器接口
   ```

3. **Claude 会自动**:
   - 阅读任务说明
   - 查看代码示例
   - 创建所需文件
   - 实现功能代码
   - 运行测试验证

### 方式 2: 按阶段逐步实现

```bash
# Phase 0: 项目初始化 ✅ (已完成)
# Phase 1: 基础设施 ⏳ (代码完成，待验证)
# Phase 2: P1 用户故事 - 文档阅读与 AI 摘要
# Phase 3: P2 用户故事 - 智能对话
# Phase 4: P3 用户故事 - 标注笔记
# Phase 5: P4 用户故事 - 学习记录
```

**示例对话**:
```
"我想开始实现 Phase 2 的 P1 功能，请帮我按照 tasks.md 中的任务列表逐个实现"
```

### 方式 3: 创建自定义工作流

我为你创建了一个便捷的任务跟踪系统：

```bash
# 查看当前进度
cat PHASE1_VERIFICATION.md

# 查看下一步要做什么
cat .specify/specs/001-core-reading-experience/tasks.md | grep "Phase 2"

# 查看具体任务
cat .specify/specs/001-core-reading-experience/tasks.md | grep "\[P1-"
```

## 实际使用示例

### 示例 1: 实现单个任务

```
你: 请帮我实现 [P1-002] PDF 解析器
```

Claude 会：
1. 读取 tasks.md 中的 [P1-002] 任务说明
2. 创建 `backend/app/core/document_parser/pdf_parser.py`
3. 实现 PDF 解析逻辑
4. 创建测试文件
5. 验证实现

### 示例 2: 实现一组任务

```
你: 请帮我实现 Phase 2 中的所有文档解析器任务 (P1-001 到 P1-005)
```

Claude 会：
1. 按顺序实现所有解析器
2. 确保它们符合统一的接口
3. 创建工厂模式
4. 运行测试

### 示例 3: 检查和验证

```
你: 请检查 Phase 1 的所有验收标准是否满足
```

Claude 会：
1. 读取 phase1-checklist.md
2. 逐项检查代码实现
3. 运行测试
4. 生成验证报告

## 快速命令参考

### 查看任务

```bash
# 查看所有 Phase 2 任务
grep -A 20 "## Phase 2:" .specify/specs/001-core-reading-experience/tasks.md

# 查看特定任务
grep -A 30 "\[P1-001\]" .specify/specs/001-core-reading-experience/tasks.md
```

### 跟踪进度

```bash
# 查看 Phase 1 验证状态
cat PHASE1_VERIFICATION.md

# 查看 Phase 1 检查清单
cat .specify/specs/001-core-reading-experience/phase1-checklist.md
```

### 运行测试

```bash
# 后端测试
cd backend
python3 scripts/test_setup.py

# 未来的单元测试
make test
```

## 推荐的开发流程

### 步骤 1: 完成 Phase 1 验证
```
请帮我完成 Phase 1 的剩余验证任务
```

### 步骤 2: 开始 Phase 2
```
Phase 1 验证完成后，请帮我开始实现 Phase 2 的 P1 用户故事
```

### 步骤 3: 逐个功能实现
```
请实现 [P1-001] 文档解析器接口
请实现 [P1-002] PDF 解析器
...
```

### 步骤 4: 功能验证
```
请运行 P1 功能的验收测试 [P1-VERIFY]
```

## 与 Claude 协作的最佳实践

### ✅ 推荐的请求方式

```
1. "请帮我实现 [P1-001] 任务"
   - 明确指定任务 ID

2. "请按照 tasks.md 实现 Phase 2 的所有解析器"
   - 指定范围和文档

3. "检查 [FOUND-001] 的所有验收标准"
   - 明确验证要求

4. "根据 phase1-checklist.md 运行所有待验证的测试"
   - 系统化验证
```

### ❌ 避免的请求方式

```
1. "运行 /speckit.implement"
   - 这个命令不存在

2. "使用 spec kit 创建任务"
   - Spec Kit 工具不可用

3. "执行 speckit 命令"
   - 没有这样的命令
```

## 文档结构说明

```
.specify/
├── HOW_TO_USE.md                   # 本文件 - 使用指南
├── memory/
│   └── constitution.md             # 项目宪章
└── specs/
    └── 001-core-reading-experience/
        ├── spec.md                 # 功能规格
        ├── plan.md                 # 技术方案
        ├── tasks.md                # 📋 任务列表 (最重要)
        ├── phase1-checklist.md     # ✅ Phase 1 检查清单
        └── cost-optimization.md    # 成本优化建议
```

### 最重要的文件

1. **[tasks.md](./specs/001-core-reading-experience/tasks.md)**
   - 所有任务的详细说明
   - 包含代码示例
   - 验收标准

2. **[phase1-checklist.md](./specs/001-core-reading-experience/phase1-checklist.md)**
   - Phase 1 的完整检查清单
   - 当前实现状态
   - 待验证项目

3. **[PHASE1_VERIFICATION.md](../../PHASE1_VERIFICATION.md)** (项目根目录)
   - 验证步骤
   - 测试命令
   - 当前状态

## 常见问题

### Q: 如何开始实现功能？
**A**: 直接告诉 Claude：
```
请帮我实现 [任务ID] 任务
```
例如：`请帮我实现 [P1-001] 文档解析器接口`

### Q: 如何验证功能是否完成？
**A**: 参考任务的"验收标准"部分，然后：
```
请验证 [任务ID] 的所有验收标准是否满足
```

### Q: 如何查看下一步要做什么？
**A**: 查看任务列表：
```
请查看 tasks.md，告诉我下一步应该实现哪个任务
```

### Q: Phase 1 还有什么没完成？
**A**: 查看验证清单：
```
请检查 PHASE1_VERIFICATION.md，列出所有待完成的验证项
```

### Q: 如何并行开发？
**A**: tasks.md 中标记 `[P]` 的任务可以并行：
```
请同时实现 [P1-002] PDF 解析器和 [P1-003] EPUB 解析器
```

## 总结

虽然 Spec Kit 的命令行工具不可用，但这些规格文档仍然非常有价值：

1. ✅ **任务列表清晰** - 知道要做什么
2. ✅ **代码示例完整** - 知道怎么做
3. ✅ **验收标准明确** - 知道何时完成
4. ✅ **可以逐步实现** - 按照文档一步步来

**建议**: 把 [tasks.md](./specs/001-core-reading-experience/tasks.md) 当作你的开发蓝图，直接告诉 Claude 你想实现哪个任务即可！

---

**创建日期**: 2025-10-22
**用途**: 替代 Spec Kit 命令行工具的使用指南
