"""
Parlant Agents for ReadPilot
"""
from .coordinator import setup_coordinator_agent
from .summarizer import setup_summarizer_agent
from .qa import setup_qa_agent
from .note_builder import setup_note_builder_agent
from .quiz_generator import setup_quiz_generator_agent

__all__ = [
    "setup_coordinator_agent",
    "setup_summarizer_agent",
    "setup_qa_agent",
    "setup_note_builder_agent",
    "setup_quiz_generator_agent",
]
