"""
Chat API endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
from models.session import ChatRequest, ChatResponse, MessageResponse
from services.agent_service import agent_service
from services.database_service import db_service
from typing import List

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    """
    Send a message to the AI assistant

    The coordinator agent will automatically route the request
    to the appropriate specialized agent.
    """
    try:
        # Get or create session
        if request.session_id:
            session = await db_service.get_session(request.session_id)
            if not session:
                raise HTTPException(status_code=404, message="Session not found")
        else:
            # Create new session
            session = await db_service.create_session(
                user_id=request.user_id,
                document_id=request.document_id
            )

        # Save user message
        await db_service.create_message(
            session_id=session.id,
            role="user",
            content=request.message
        )

        # Send to agent service
        response = await agent_service.send_message(
            user_id=request.user_id,
            message=request.message,
            document_id=request.document_id,
            context={"session_id": session.id}
        )

        # Save assistant message
        await db_service.create_message(
            session_id=session.id,
            role="assistant",
            content=response["message"],
            agent_name=response.get("agent"),
            metadata=response.get("metadata", {})
        )

        return ChatResponse(
            session_id=session.id,
            message=response["message"],
            agent_name=response.get("agent"),
            metadata=response.get("metadata")
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}/messages", response_model=List[MessageResponse])
async def get_session_messages(session_id: str):
    """Get all messages for a session"""
    try:
        messages = await db_service.get_session_messages(session_id)
        return messages

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sessions/{session_id}/clear")
async def clear_session(session_id: str):
    """Clear session context (for debugging/testing)"""
    try:
        # TODO: Implement session context clearing
        return {"status": "success", "message": "Session cleared"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
