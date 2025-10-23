"""文档API端点"""
from typing import Any, Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.document import (
    DocumentListData,
    DocumentResponse,
    DocumentUpdate,
)
from app.schemas.response import paginated_success, success
from app.services.document_service import DocumentService
from app.tasks.document_processing import process_document_task

router = APIRouter()


@router.post("", status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    title: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    上传文档

    支持的格式: PDF, EPUB, DOCX, TXT, Markdown
    """
    try:
        service = DocumentService(db)
        document = await service.create_document(
            user=current_user,
            file=file,
            title=title
        )

        # 异步触发文档处理任务
        process_document_task.delay(document.id)

        # 转换为字典以便序列化
        from pydantic import TypeAdapter
        document_dict = TypeAdapter(DocumentResponse).dump_python(document, mode='json')

        return success(
            data=document_dict,
            message="文档上传成功，正在处理中"
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"上传失败: {str(e)}"
        )


@router.get("")
async def list_documents(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None, regex="^(pending|processing|completed|failed)$"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    获取用户的文档列表

    支持分页和状态过滤
    """
    service = DocumentService(db)
    skip = (page - 1) * page_size

    documents, total = await service.list_documents(
        user=current_user,
        skip=skip,
        limit=page_size,
        status=status
    )

    # 转换为字典列表
    from pydantic import TypeAdapter
    documents_data = [
        TypeAdapter(DocumentResponse).dump_python(doc, mode='json')
        for doc in documents
    ]

    return paginated_success(
        items=documents_data,
        total=total,
        page=page,
        page_size=page_size,
        message="获取文档列表成功"
    )


@router.get("/{document_id}")
async def get_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    获取文档详情
    """
    service = DocumentService(db)
    document = await service.get_document(document_id, current_user)

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文档不存在"
        )

    # 转换为字典
    from pydantic import TypeAdapter
    document_dict = TypeAdapter(DocumentResponse).dump_python(document, mode='json')

    return success(data=document_dict, message="获取文档成功")


@router.put("/{document_id}")
async def update_document(
    document_id: str,
    data: DocumentUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    更新文档信息
    """
    service = DocumentService(db)
    document = await service.update_document(
        document_id=document_id,
        user=current_user,
        title=data.title
    )

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文档不存在"
        )

    # 转换为字典
    from pydantic import TypeAdapter
    document_dict = TypeAdapter(DocumentResponse).dump_python(document, mode='json')

    return success(data=document_dict, message="更新文档成功")


@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    删除文档
    """
    service = DocumentService(db)
    result = await service.delete_document(document_id, current_user)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文档不存在"
        )

    return success(message="删除文档成功")


@router.get("/{document_id}/download")
async def download_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> StreamingResponse:
    """
    下载文档原始文件

    返回文档的原始文件供用户下载
    """
    service = DocumentService(db)
    document = await service.get_document(document_id, current_user)

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文档不存在"
        )

    try:
        # 获取文件内容
        file_content = await service.get_document_file(document)

        # 确定 MIME 类型
        content_type_map = {
            "pdf": "application/pdf",
            "epub": "application/epub+zip",
            "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "txt": "text/plain",
            "md": "text/markdown",
            "markdown": "text/markdown",
        }
        content_type = content_type_map.get(document.file_type, "application/octet-stream")

        # 构造文件名
        import os
        filename = f"{document.title}{os.path.splitext(document.file_path)[1]}"

        # 返回流式响应
        from io import BytesIO
        return StreamingResponse(
            BytesIO(file_content),
            media_type=content_type,
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Content-Length": str(len(file_content)),
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件下载失败: {str(e)}"
        )


@router.post("/{document_id}/summarize")
async def generate_summary(
    document_id: str,
    depth: str = Query("detailed", regex="^(brief|detailed)$"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    生成文档摘要

    支持两种深度:
    - brief: 简要摘要
    - detailed: 详细摘要 (默认)
    """
    service = DocumentService(db)
    document = await service.get_document(document_id, current_user)

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文档不存在"
        )

    # 检查文档是否已处理完成
    if document.processing_status != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"文档尚未处理完成，当前状态: {document.processing_status}"
        )

    try:
        # 异步触发摘要生成任务
        from app.tasks.document_processing import generate_summary_task
        task = generate_summary_task.delay(document_id, depth)

        return success(
            data={"task_id": task.id, "status": "processing"},
            message="摘要生成任务已启动"
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"启动摘要生成失败: {str(e)}"
        )


@router.get("/{document_id}/summary")
async def get_summary(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    获取文档摘要

    如果摘要不存在，返回 404
    """
    from app.services.summary_service import SummaryService
    from app.schemas.document import SummaryResponse

    summary_service = SummaryService(db)

    try:
        summary = await summary_service.get_summary(document_id, current_user)

        if not summary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="摘要不存在，请先生成摘要"
            )

        # 从 AISummary 模型转换为响应格式
        summary_response = SummaryResponse.from_ai_summary(summary)
        summary_dict = summary_response.model_dump(mode='json')

        return success(data=summary_dict, message="获取摘要成功")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取摘要失败: {str(e)}"
        )
