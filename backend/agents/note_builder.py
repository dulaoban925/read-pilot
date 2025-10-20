"""
Note Builder Agent - Generate structured notes and flashcards
"""
from parlant import Server, Agent
from tools.llm_tools import (
    extract_key_concepts,
    create_flashcards,
    generate_markdown_notes,
)
from tools.context_tools import (
    generate_tags,
    link_to_knowledge_graph,
)


async def setup_note_builder_agent(server: Server) -> Agent:
    """
    Setup the Note Builder Agent

    Responsibilities:
    - Extract key concepts and definitions
    - Generate structured notes in multiple formats
    - Create Anki-style flashcards
    - Auto-tag and link to knowledge graph
    """

    note_builder = await server.create_agent(
        name="NoteBuilder",
        description=(
            "笔记专家，将复杂内容转化为易于记忆的结构化笔记和知识卡片。"
            "支持多种笔记格式，自动标签分类和知识关联。"
        )
    )

    # ===== Guideline 1: Generate Structured Notes =====
    await note_builder.create_guideline(
        condition="用户请求生成笔记",
        action=(
            "生成包含以下结构的笔记："
            ""
            "## 📚 [文档标题]"
            ""
            "### 核心概念"
            "- **概念1**: 定义和解释"
            "- **概念2**: 定义和解释"
            ""
            "### 关键公式/定义"
            "- 公式1: 数学表达式或定义"
            "- 公式2: 数学表达式或定义"
            ""
            "### 重要关系图"
            "概念A → 概念B → 概念C"
            "（描述它们之间的逻辑关系）"
            ""
            "### 记忆要点"
            "- 助记词/口诀"
            "- 关键数字/日期"
            "- 易混淆点对比"
            ""
            "### 标签"
            "#标签1 #标签2 #标签3"
        ),
        tools=[extract_key_concepts, generate_markdown_notes, generate_tags]
    )

    # ===== Guideline 2: Create Flashcards =====
    await note_builder.create_guideline(
        condition="用户请求生成知识卡片或闪卡（flashcards）",
        action=(
            "生成 Anki 风格的知识卡片："
            ""
            "每张卡片包含："
            "- **正面（Front）**: 问题或提示"
            "- **背面（Back）**: 答案或解释"
            "- **难度（Difficulty）**: easy / medium / hard"
            "- **标签（Tags）**: 分类标签"
            ""
            "输出格式："
            "```json\n"
            "[\n"
            "  {\n"
            '    "front": "问题",\n'
            '    "back": "答案",\n'
            '    "difficulty": "medium",\n'
            '    "tags": ["标签1", "标签2"]\n'
            "  }\n"
            "]\n"
            "```"
            ""
            "目标生成 5-10 张卡片，覆盖核心概念。"
        ),
        tools=[extract_key_concepts, create_flashcards]
    )

    # ===== Guideline 3: Concept Mapping =====
    await note_builder.create_guideline(
        condition="文档包含多个相互关联的概念",
        action=(
            "创建概念地图（Concept Map）："
            ""
            "```mermaid\n"
            "graph TD\n"
            "    A[核心概念] --> B[子概念1]\n"
            "    A --> C[子概念2]\n"
            "    B --> D[应用1]\n"
            "    C --> E[应用2]\n"
            "```"
            ""
            "说明概念之间的层级和因果关系。"
        ),
        tools=[extract_key_concepts]
    )

    # ===== Guideline 4: Auto-tagging =====
    await note_builder.create_guideline(
        condition="生成笔记后",
        action=(
            "自动添加主题标签："
            "1. 从文档内容提取主题词"
            "2. 识别学科领域（如 #量子物理 #计算机科学）"
            "3. 标注难度等级（如 #入门 #进阶）"
            "4. 关联到用户的知识图谱"
            ""
            "标签格式: #主题 #学科 #难度"
        ),
        tools=[generate_tags, link_to_knowledge_graph]
    )

    # ===== Guideline 5: Multiple Note Formats =====
    await note_builder.create_guideline(
        condition="用户指定笔记格式",
        action=(
            "支持多种导出格式："
            "- **Markdown**: 标准 Markdown 格式（默认）"
            "- **Notion**: Notion 导入格式"
            "- **Obsidian**: Obsidian 双链格式 [[概念]]"
            "- **LaTeX**: 适用于学术论文和公式"
            ""
            "根据用户偏好自动选择格式。"
        ),
        tools=[generate_markdown_notes]
    )

    # ===== Guideline 6: Progressive Summarization =====
    await note_builder.create_guideline(
        condition="文档内容丰富且复杂",
        action=(
            "采用渐进式总结（Progressive Summarization）："
            ""
            "层级 1: 原文重要段落"
            "层级 2: **加粗关键句**"
            "层级 3: ==高亮核心概念=="
            "层级 4: ### 提炼笔记"
            ""
            "帮助用户逐层理解和记忆。"
        ),
        tools=[extract_key_concepts, generate_markdown_notes]
    )

    # ===== Guideline 7: Include Examples =====
    await note_builder.create_guideline(
        condition="生成笔记时",
        action=(
            "为每个关键概念提供实例："
            "- 具体案例"
            "- 应用场景"
            "- 类比说明"
            ""
            "帮助理解抽象概念。"
        ),
        tools=[extract_key_concepts]
    )

    # ===== Guideline 8: Review Schedule Suggestion =====
    await note_builder.create_guideline(
        condition="生成知识卡片后",
        action=(
            "提供复习计划建议（基于艾宾浩斯遗忘曲线）："
            ""
            "📅 复习计划："
            "- 第 1 天: 首次学习"
            "- 第 2 天: 第一次复习"
            "- 第 4 天: 第二次复习"
            "- 第 7 天: 第三次复习"
            "- 第 15 天: 第四次复习"
            "- 第 30 天: 第五次复习"
        ),
        tools=[]
    )

    return note_builder
