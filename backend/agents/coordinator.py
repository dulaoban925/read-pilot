"""
Coordinator Agent - Routes user requests to specialized agents
"""
from parlant import Server, Agent
from tools.context_tools import (
    update_reading_history,
    sync_context_to_database,
    get_user_weak_points,
)
from tools.document_tools import retrieve_document_context


async def setup_coordinator_agent(server: Server) -> Agent:
    """
    Setup the Coordinator Agent

    Responsibilities:
    - Route user requests to appropriate specialized agents
    - Maintain session state and context
    - Track user behavior and preferences
    """

    coordinator = await server.create_agent(
        name="ReadingCoordinator",
        description=(
            "智能协调者，理解用户意图并分配给合适的专业 Agent。"
            "负责任务路由、上下文管理和用户行为追踪。"
        )
    )

    # ===== Guideline 1: Document Summarization =====
    await coordinator.create_guideline(
        condition="用户上传文档或请求总结、摘要、概述",
        action=(
            "识别为文档总结任务。"
            "1. 调用 Summarizer Agent 生成摘要"
            "2. 更新用户阅读历史"
            "3. 返回结构化摘要给用户"
        ),
        tools=[update_reading_history, retrieve_document_context]
    )

    # ===== Guideline 2: Question Answering =====
    await coordinator.create_guideline(
        condition=(
            "用户提出关于文档内容的问题，或使用疑问词"
            "（如：什么、为什么、如何、怎么、解释、说明）"
        ),
        action=(
            "识别为问答任务。"
            "1. 调用 QA Agent 进行深度问答"
            "2. 基于文档上下文和对话历史生成回答"
            "3. 提供引用来源"
        ),
        tools=[retrieve_document_context]
    )

    # ===== Guideline 3: Note Generation =====
    await coordinator.create_guideline(
        condition=(
            "用户请求生成笔记、知识卡片、记忆卡片、"
            "或提到'整理'、'归纳'、'记录'"
        ),
        action=(
            "识别为笔记生成任务。"
            "1. 调用 Note Builder Agent 提炼关键信息"
            "2. 生成结构化笔记和知识卡片"
            "3. 自动添加标签和分类"
        ),
        tools=[]
    )

    # ===== Guideline 4: Quiz Generation =====
    await coordinator.create_guideline(
        condition=(
            "用户需要测验、检验理解、自测，"
            "或提到'题目'、'测试'、'练习'"
        ),
        action=(
            "识别为测验生成任务。"
            "1. 调用 Quiz Generator Agent 生成个性化题目"
            "2. 基于用户薄弱点调整题目难度"
            "3. 提供详细解析"
        ),
        tools=[get_user_weak_points]
    )

    # ===== Guideline 5: Context Synchronization =====
    await coordinator.create_guideline(
        condition="完成任何任务后",
        action=(
            "同步上下文到数据库，确保用户数据持久化。"
            "更新会话状态和活动时间。"
        ),
        tools=[sync_context_to_database]
    )

    # ===== Guideline 6: Greeting and General Conversation =====
    await coordinator.create_guideline(
        condition="用户打招呼或进行一般性对话",
        action=(
            "友好回应，介绍 ReadPilot 的功能。"
            "引导用户上传文档或提出问题。"
        ),
        tools=[]
    )

    return coordinator
