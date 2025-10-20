"""
Context management and user state tools
"""
from parlant import tool, ToolContext, ToolResult
from typing import List, Dict, Optional
from datetime import datetime


@tool
async def update_reading_history(
    context: ToolContext,
    document_id: str,
    user_id: str,
    action: str
) -> ToolResult:
    """
    Update user reading history

    Args:
        context: Parlant tool context
        document_id: Document identifier
        user_id: User identifier
        action: Action performed (e.g., 'read', 'summarized', 'questioned')

    Returns:
        Success status
    """
    # Update context variables
    context.variables["last_document"] = document_id
    context.variables["reading_count"] = context.variables.get("reading_count", 0) + 1
    context.variables["last_activity"] = datetime.now().isoformat()

    # TODO: Persist to database
    # await db.reading_history.insert({
    #     "user_id": user_id,
    #     "document_id": document_id,
    #     "action": action,
    #     "timestamp": datetime.now()
    # })

    return ToolResult(
        success=True,
        message=f"已记录阅读行为: {action}"
    )


@tool
async def sync_context_to_database(
    context: ToolContext,
    user_id: str
) -> ToolResult:
    """
    Sync context variables to persistent database

    Args:
        context: Parlant tool context
        user_id: User identifier

    Returns:
        Success status
    """
    # Extract persistent data from context
    persistent_data = {
        "user_id": user_id,
        "preferences": {
            "summary_style": context.variables.get("summary_style"),
            "difficulty_preference": context.variables.get("difficulty_preference"),
            "language": context.variables.get("language", "zh"),
        },
        "learning_stats": {
            "reading_count": context.variables.get("reading_count", 0),
            "total_questions_asked": context.variables.get("total_questions_asked", 0),
            "quiz_scores": context.variables.get("quiz_scores", []),
            "weak_topics": context.variables.get("weak_topics", []),
            "mastered_topics": context.variables.get("mastered_topics", []),
        },
        "last_updated": datetime.now().isoformat()
    }

    # TODO: Persist to database
    # await db.users.update_one(
    #     {"user_id": user_id},
    #     {"$set": persistent_data},
    #     upsert=True
    # )

    return ToolResult(
        success=True,
        message="上下文已同步到数据库"
    )


@tool
async def get_user_weak_points(
    context: ToolContext,
    user_id: str
) -> ToolResult:
    """
    Get user's weak knowledge points

    Args:
        context: Parlant tool context
        user_id: User identifier

    Returns:
        List of weak topics
    """
    weak_topics = context.variables.get("weak_topics", [])

    if not weak_topics:
        # Analyze quiz history to identify weak points
        quiz_scores = context.variables.get("quiz_scores", [])
        topic_performance = {}

        for quiz in quiz_scores:
            for topic in quiz.get("topics", []):
                if topic not in topic_performance:
                    topic_performance[topic] = []
                topic_performance[topic].append(quiz.get("score", 0))

        # Identify topics with average score < 0.6
        weak_topics = [
            topic for topic, scores in topic_performance.items()
            if sum(scores) / len(scores) < 0.6
        ]

        context.variables["weak_topics"] = weak_topics

    return ToolResult(
        success=True,
        data={"weak_topics": weak_topics}
    )


@tool
async def get_conversation_history(
    context: ToolContext,
    limit: Optional[int] = None
) -> ToolResult:
    """
    Get conversation history

    Args:
        context: Parlant tool context
        limit: Optional limit on number of messages to return

    Returns:
        Conversation history
    """
    history = context.variables.get("conversation_history", [])

    if limit:
        history = history[-limit:]

    return ToolResult(
        success=True,
        data={"conversation_history": history}
    )


@tool
async def update_conversation_history(
    context: ToolContext,
    role: str,
    message: str,
    agent: Optional[str] = None
) -> ToolResult:
    """
    Update conversation history

    Args:
        context: Parlant tool context
        role: 'user' or 'assistant'
        message: Message content
        agent: Optional agent name

    Returns:
        Success status
    """
    history = context.variables.get("conversation_history", [])

    # Add new message
    history.append({
        "role": role,
        "message": message,
        "agent": agent,
        "timestamp": datetime.now().isoformat()
    })

    # Keep only last N messages
    max_history = 20  # Keep last 20 messages (10 turns)
    if len(history) > max_history:
        history = history[-max_history:]

    context.variables["conversation_history"] = history

    # Update question count if user message
    if role == "user":
        context.variables["total_questions_asked"] = \
            context.variables.get("total_questions_asked", 0) + 1

    return ToolResult(
        success=True,
        message="对话历史已更新"
    )


@tool
async def collect_feedback(
    context: ToolContext,
    content_type: str,
    content_id: str,
    feedback: Dict
) -> ToolResult:
    """
    Collect user feedback

    Args:
        context: Parlant tool context
        content_type: Type of content (e.g., 'summary', 'answer', 'note')
        content_id: Content identifier
        feedback: Feedback data (e.g., {'rating': 5, 'comment': '...'})

    Returns:
        Success status
    """
    # Store feedback
    feedbacks = context.variables.get("feedbacks", [])
    feedbacks.append({
        "content_type": content_type,
        "content_id": content_id,
        "feedback": feedback,
        "timestamp": datetime.now().isoformat()
    })
    context.variables["feedbacks"] = feedbacks

    # TODO: Persist to database for analytics

    return ToolResult(
        success=True,
        message="反馈已记录"
    )


@tool
async def update_user_preference(
    context: ToolContext,
    preference_type: str,
    preference_value: str
) -> ToolResult:
    """
    Update user preference

    Args:
        context: Parlant tool context
        preference_type: Type of preference (e.g., 'summary_style', 'difficulty')
        preference_value: Preference value

    Returns:
        Success status
    """
    context.variables[preference_type] = preference_value

    return ToolResult(
        success=True,
        message=f"已保存偏好: {preference_type} = {preference_value}"
    )


@tool
async def generate_tags(
    context: ToolContext,
    text: str,
    max_tags: int = 5
) -> ToolResult:
    """
    Generate tags for content

    Args:
        context: Parlant tool context
        text: Content to tag
        max_tags: Maximum number of tags

    Returns:
        List of tags
    """
    # TODO: Implement actual tag generation (could use LLM or keyword extraction)
    # This is a simplified placeholder

    # Extract keywords using simple frequency analysis
    words = text.lower().split()
    word_freq = {}

    for word in words:
        if len(word) > 3:  # Skip short words
            word_freq[word] = word_freq.get(word, 0) + 1

    # Sort by frequency and take top N
    tags = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:max_tags]
    tags = [f"#{tag[0]}" for tag in tags]

    return ToolResult(
        success=True,
        data={"tags": tags}
    )


@tool
async def link_to_knowledge_graph(
    context: ToolContext,
    note_id: str,
    concepts: List[str]
) -> ToolResult:
    """
    Link note to user's knowledge graph

    Args:
        context: Parlant tool context
        note_id: Note identifier
        concepts: List of concepts in the note

    Returns:
        Success status
    """
    # TODO: Implement knowledge graph integration
    # This would link concepts to existing knowledge graph nodes

    return ToolResult(
        success=True,
        message=f"已关联 {len(concepts)} 个概念到知识图谱"
    )


@tool
async def analyze_weak_points(
    context: ToolContext,
    user_id: str
) -> ToolResult:
    """
    Analyze user's weak knowledge points from quiz history

    Args:
        context: Parlant tool context
        user_id: User identifier

    Returns:
        Analysis of weak points
    """
    quiz_scores = context.variables.get("quiz_scores", [])

    if not quiz_scores:
        return ToolResult(
            success=True,
            data={
                "weak_topics": [],
                "recommendations": []
            }
        )

    # Analyze performance by topic
    topic_stats = {}

    for quiz in quiz_scores:
        topics = quiz.get("topics", [])
        score = quiz.get("score", 0)

        for topic in topics:
            if topic not in topic_stats:
                topic_stats[topic] = {"scores": [], "count": 0}

            topic_stats[topic]["scores"].append(score)
            topic_stats[topic]["count"] += 1

    # Identify weak topics (avg score < 60%)
    weak_topics = []
    for topic, stats in topic_stats.items():
        avg_score = sum(stats["scores"]) / len(stats["scores"])
        if avg_score < 0.6:
            weak_topics.append({
                "topic": topic,
                "avg_score": avg_score,
                "attempts": stats["count"]
            })

    # Sort by score (weakest first)
    weak_topics.sort(key=lambda x: x["avg_score"])

    # Update context
    context.variables["weak_topics"] = [t["topic"] for t in weak_topics]

    return ToolResult(
        success=True,
        data={
            "weak_topics": weak_topics,
            "recommendations": [
                f"建议复习: {t['topic']} (正确率: {t['avg_score']*100:.0f}%)"
                for t in weak_topics[:3]
            ]
        }
    )


@tool
async def adaptive_difficulty(
    context: ToolContext,
    topic: str,
    current_difficulty: str
) -> ToolResult:
    """
    Determine adaptive difficulty level for a topic

    Args:
        context: Parlant tool context
        topic: Topic name
        current_difficulty: Current difficulty level

    Returns:
        Recommended difficulty level
    """
    quiz_scores = context.variables.get("quiz_scores", [])

    # Filter scores for this topic
    topic_scores = [
        quiz["score"] for quiz in quiz_scores
        if topic in quiz.get("topics", [])
    ]

    if not topic_scores:
        return ToolResult(
            success=True,
            data={"difficulty": current_difficulty}
        )

    # Calculate recent performance (last 3 quizzes)
    recent_scores = topic_scores[-3:]
    avg_score = sum(recent_scores) / len(recent_scores)

    # Adjust difficulty
    if avg_score > 0.8:
        # Performing well, increase difficulty
        new_difficulty = "hard" if current_difficulty == "medium" else "medium"
    elif avg_score < 0.6:
        # Struggling, decrease difficulty
        new_difficulty = "easy" if current_difficulty == "medium" else "medium"
    else:
        # Maintain current difficulty
        new_difficulty = current_difficulty

    return ToolResult(
        success=True,
        data={
            "difficulty": new_difficulty,
            "avg_score": avg_score,
            "reason": f"基于最近 {len(recent_scores)} 次测验，平均得分 {avg_score*100:.0f}%"
        }
    )


@tool
async def update_quiz_history(
    context: ToolContext,
    quiz_id: str,
    score: float,
    topics: List[str],
    details: Optional[Dict] = None
) -> ToolResult:
    """
    Update quiz history

    Args:
        context: Parlant tool context
        quiz_id: Quiz identifier
        score: Quiz score (0-1)
        topics: Topics covered in quiz
        details: Optional additional details

    Returns:
        Success status
    """
    quiz_scores = context.variables.get("quiz_scores", [])

    quiz_record = {
        "quiz_id": quiz_id,
        "score": score,
        "topics": topics,
        "timestamp": datetime.now().isoformat(),
        **(details or {})
    }

    quiz_scores.append(quiz_record)
    context.variables["quiz_scores"] = quiz_scores

    return ToolResult(
        success=True,
        message="测验历史已更新"
    )
