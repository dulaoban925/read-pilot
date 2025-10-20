"""
Document management API endpoints
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form
from models.document import DocumentResponse, DocumentCreate, DocumentSummaryResponse
from services.database_service import db_service
from services.vector_service import vector_service
from config import settings
from typing import List
import aiofiles
import os
import uuid

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    user_id: str = Form(...),
    title: str = Form(None)
):
    """
    Upload a document for processing

    Supports: PDF, TXT, MD, DOCX
    """
    try:
        # Validate file type
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in settings.ALLOWED_FILE_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"File type {file_ext} not supported. Allowed: {settings.ALLOWED_FILE_TYPES}"
            )

        # Validate file size
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Seek back to start

        if file_size > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File size exceeds limit of {settings.MAX_UPLOAD_SIZE} bytes"
            )

        # Generate unique file ID and storage path
        file_id = str(uuid.uuid4())
        storage_dir = "/storage/documents"  # TODO: Configure storage location
        os.makedirs(storage_dir, exist_ok=True)

        file_path = os.path.join(storage_dir, f"{file_id}{file_ext}")

        # Save file
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)

        # Create document record
        document = await db_service.create_document(
            user_id=user_id,
            title=title or file.filename,
            file_name=file.filename,
            file_type=file_ext[1:],  # Remove leading dot
            file_size=file_size,
            file_path=file_path
        )

        # TODO: Trigger async document processing
        # - Extract text
        # - Generate embeddings
        # - Index in vector database
        # - Generate summary

        return document

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: str):
    """Get document by ID"""
    try:
        document = await db_service.get_document(document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        return document

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user/{user_id}", response_model=List[DocumentResponse])
async def get_user_documents(user_id: str):
    """Get all documents for a user"""
    try:
        documents = await db_service.get_user_documents(user_id)
        return documents

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{document_id}/summary", response_model=DocumentSummaryResponse)
async def get_document_summary(document_id: str):
    """Get document summary"""
    try:
        document = await db_service.get_document(document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        if not document.summary:
            raise HTTPException(
                status_code=404,
                detail="Summary not yet generated. Try again later."
            )

        return DocumentSummaryResponse(
            document_id=document.id,
            **document.summary
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{document_id}")
async def delete_document(document_id: str):
    """Delete a document"""
    try:
        document = await db_service.get_document(document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        # Delete file from storage
        if os.path.exists(document.file_path):
            os.remove(document.file_path)

        # Delete from vector database
        await vector_service.delete_document(document_id)

        # TODO: Delete from database
        # await db_service.delete_document(document_id)

        return {"status": "success", "message": "Document deleted"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{document_id}/process")
async def process_document(document_id: str):
    """
    Manually trigger document processing

    This endpoint can be used to:
    - Re-process a document
    - Generate embeddings if indexing failed
    - Update summary
    """
    try:
        document = await db_service.get_document(document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        # Update status
        await db_service.update_document(
            document_id,
            processing_status="processing"
        )

        # TODO: Trigger async processing task
        # This should:
        # 1. Extract text from document
        # 2. Split into chunks
        # 3. Generate embeddings
        # 4. Index in vector database
        # 5. Generate summary using Summarizer agent
        # 6. Update document record

        return {
            "status": "success",
            "message": "Document processing started"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
