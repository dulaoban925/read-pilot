"""全局异常处理"""
from typing import Any

from fastapi import HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    处理HTTPException异常

    将所有HTTPException转换为统一的响应格式
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.status_code,
            "message": exc.detail,
            "data": None
        }
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError | ValidationError
) -> JSONResponse:
    """
    处理请求验证错误

    将Pydantic验证错误转换为统一的响应格式
    """
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "code": 422,
            "message": "Validation error",
            "data": {
                "errors": exc.errors()
            }
        }
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    处理未捕获的异常

    将所有未处理的异常转换为统一的500错误响应
    """
    import traceback
    import logging

    logger = logging.getLogger(__name__)
    logger.error(f"Unhandled exception: {str(exc)}\n{traceback.format_exc()}")

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": 500,
            "message": "Internal server error",
            "data": None
        }
    )


# ==================== 业务异常类 ====================


class AppException(Exception):
    """应用异常基类"""

    def __init__(
        self,
        message: str,
        code: str,
        status_code: int = 400,
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}


# 文档相关异常

class DocumentError(AppException):
    """文档错误基类"""

    def __init__(self, message: str, code: str = "DOCUMENT_ERROR", details: dict | None = None):
        super().__init__(message, code, 400, details)


class InvalidFileTypeError(DocumentError):
    """不支持的文件类型"""

    def __init__(self, file_type: str, allowed_types: list[str]):
        super().__init__(
            message=f"不支持的文件类型: {file_type}",
            code="INVALID_FILE_TYPE",
            details={"file_type": file_type, "allowed_types": allowed_types},
        )


class FileSizeTooLargeError(DocumentError):
    """文件大小超过限制"""

    def __init__(self, file_size: int, max_size: int):
        super().__init__(
            message=f"文件大小超过限制: {file_size} bytes (最大 {max_size} bytes)",
            code="FILE_SIZE_TOO_LARGE",
            details={
                "file_size": file_size,
                "max_size": max_size,
                "file_size_mb": round(file_size / 1024 / 1024, 2),
                "max_size_mb": round(max_size / 1024 / 1024, 2),
            },
        )


class PageCountExceededError(DocumentError):
    """文档页数超过限制"""

    def __init__(self, page_count: int, max_pages: int):
        super().__init__(
            message=f"文档页数超过限制: {page_count} 页 (最大 {max_pages} 页)",
            code="PAGE_COUNT_EXCEEDED",
            details={"page_count": page_count, "max_pages": max_pages},
        )


class DocumentProcessingError(DocumentError):
    """文档处理失败"""

    def __init__(self, document_id: str, error_message: str):
        super().__init__(
            message=f"文档处理失败: {error_message}",
            code="DOCUMENT_PROCESSING_ERROR",
            details={"document_id": document_id, "error": error_message},
        )
        self.status_code = 500


class RateLimitExceededError(AppException):
    """速率限制超出"""

    def __init__(self, limit: int, window: int, retry_after: int):
        super().__init__(
            message=f"请求过于频繁，请 {retry_after} 秒后重试",
            code="RATE_LIMIT_EXCEEDED",
            status_code=429,
            details={
                "limit": limit,
                "window_seconds": window,
                "retry_after_seconds": retry_after,
            },
        )
