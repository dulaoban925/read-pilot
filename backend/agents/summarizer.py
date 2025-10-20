"""
Summarizer Agent - Document analysis and hierarchical summarization
"""
from parlant import Server, Agent
from tools.document_tools import (
    extract_text,
    detect_document_type,
)
from tools.llm_tools import (
    generate_hierarchical_summary,
    generate_technical_summary,
    generate_narrative_summary,
)
from tools.context_tools import (
    update_user_preference,
    collect_feedback,
)


async def setup_summarizer_agent(server: Server) -> Agent:
    """
    Setup the Summarizer Agent

    Responsibilities:
    - Document analysis and type detection
    - Hierarchical summary generation (Abstract → Key Insights → Concepts → Examples)
    - Key sentence extraction
    - Learn and adapt to user preferences
    """

    summarizer = await server.create_agent(
        name="DocumentSummarizer",
        description=(
            "专业文档分析师，擅长提炼要点、生成结构化摘要。"
            "能够识别文档类型并调整摘要策略，学习用户偏好。"
        )
    )

    # ===== Guideline 1: Generate Hierarchical Summary =====
    await summarizer.create_guideline(
        condition="收到完整文档或长文本",
        action=(
            "生成多层级摘要，按以下结构："
            "1. 一句话概要（Abstract）- 20字内精炼总结"
            "2. 核心要点（Key Insights）- 3-5个主要观点"
            "3. 重要概念解释（Concepts）- 关键术语和定义"
            "4. 典型例子（Examples）- 具体案例或应用"
            ""
            "输出格式："
            "```json\n"
            "{\n"
            '  "abstract": "...",\n'
            '  "key_insights": [...],\n'
            '  "concepts": {...},\n'
            '  "examples": [...]\n'
            "}\n"
            "```"
        ),
        tools=[extract_text, generate_hierarchical_summary]
    )

    # ===== Guideline 2: Technical/Academic Document =====
    await summarizer.create_guideline(
        condition=(
            "文档类型是技术文档、学术论文、研究报告"
        ),
        action=(
            "采用专业术语，重点提取："
            "1. 研究背景和问题"
            "2. 方法论和实验设计"
            "3. 主要发现和结果"
            "4. 结论和未来方向"
            ""
            "保持专业性，不过度简化术语。"
        ),
        tools=[detect_document_type, generate_technical_summary]
    )

    # ===== Guideline 3: Narrative/News Document =====
    await summarizer.create_guideline(
        condition=(
            "文档类型是叙事类、新闻报道、故事类内容"
        ),
        action=(
            "采用通俗语言，重点提取："
            "1. 主要事件和情节"
            "2. 关键人物和角色"
            "3. 时间线和因果关系"
            "4. 影响和意义"
            ""
            "使用易懂的表达，避免专业术语。"
        ),
        tools=[detect_document_type, generate_narrative_summary]
    )

    # ===== Guideline 4: Adapt to User Preferences =====
    await summarizer.create_guideline(
        condition="用户对摘要提供反馈或修改建议",
        action=(
            "记录用户偏好："
            "- summary_style: concise（简洁）/ detailed（详细）/ visual（可视化）"
            "- detail_level: low / medium / high"
            "- language_style: professional / casual"
            ""
            "在后续摘要中应用这些偏好。"
        ),
        tools=[collect_feedback, update_user_preference]
    )

    # ===== Guideline 5: Handle Long Documents =====
    await summarizer.create_guideline(
        condition="文档超过 10000 字或 20 页",
        action=(
            "采用分段摘要策略："
            "1. 将文档分为逻辑章节"
            "2. 每章节生成独立摘要"
            "3. 生成全局概览摘要"
            "4. 提供章节导航"
        ),
        tools=[extract_text, generate_hierarchical_summary]
    )

    # ===== Guideline 6: Extract Key Quotes =====
    await summarizer.create_guideline(
        condition="生成摘要后",
        action=(
            "提取 3-5 个最具代表性的原文引用："
            "- 核心论点"
            "- 精彩观点"
            "- 重要数据"
            ""
            "格式: \"引用内容\" - 第 X 页/段落"
        ),
        tools=[]
    )

    return summarizer
