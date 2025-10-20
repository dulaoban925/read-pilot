"""
Parlant Tools for ReadPilot
"""
from .document_tools import *
from .vector_tools import *
from .context_tools import *
from .llm_tools import *

__all__ = [
    # Document tools
    "extract_text",
    "detect_document_type",
    "retrieve_document_context",
    "cite_source",

    # Vector tools
    "semantic_search",
    "embed_text",

    # Context tools
    "update_reading_history",
    "sync_context_to_database",
    "get_user_weak_points",
    "get_conversation_history",
    "update_conversation_history",
    "collect_feedback",
    "update_user_preference",
    "generate_tags",
    "link_to_knowledge_graph",
    "analyze_weak_points",
    "adaptive_difficulty",
    "update_quiz_history",

    # LLM tools
    "generate_hierarchical_summary",
    "generate_technical_summary",
    "generate_narrative_summary",
    "generate_answer",
    "generate_follow_up_questions",
    "deep_dive_answer",
    "extract_key_concepts",
    "create_flashcards",
    "generate_markdown_notes",
    "generate_mcq",
    "generate_fill_blank",
    "generate_short_answer",
]
