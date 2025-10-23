"""统一响应数据结构"""
from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel, Field

# 泛型类型变量
T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """
    统一API响应格式

    成功响应示例:
    {
        "code": 0,
        "message": "Success",
        "data": {...}
    }

    错误响应示例:
    {
        "code": 400,
        "message": "Error message",
        "data": null
    }
    """
    code: int = Field(default=0, description="响应码，0表示成功，非0表示错误")
    message: str = Field(default="Success", description="响应消息")
    data: Optional[T] = Field(default=None, description="响应数据")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "code": 0,
                    "message": "Success",
                    "data": {"id": "123", "name": "example"}
                }
            ]
        }
    }


class PaginationData(BaseModel, Generic[T]):
    """
    分页数据结构
    """
    items: list[T] = Field(default_factory=list, description="数据列表")
    total: int = Field(default=0, description="总数据量")
    page: int = Field(default=1, ge=1, description="当前页码")
    page_size: int = Field(default=20, ge=1, le=100, description="每页数量")
    total_pages: int = Field(default=0, description="总页数")

    @classmethod
    def create(cls, items: list[T], total: int, page: int, page_size: int) -> "PaginationData[T]":
        """创建分页数据"""
        total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )


# 便捷函数
def success(data: Any = None, message: str = "Success") -> dict[str, Any]:
    """
    创建成功响应

    Args:
        data: 响应数据
        message: 成功消息

    Returns:
        统一格式的响应字典
    """
    return {
        "code": 0,
        "message": message,
        "data": data
    }


def error(code: int, message: str, data: Any = None) -> dict[str, Any]:
    """
    创建错误响应

    Args:
        code: 错误码
        message: 错误消息
        data: 附加数据（可选）

    Returns:
        统一格式的错误响应字典
    """
    return {
        "code": code,
        "message": message,
        "data": data
    }


def paginated_success(
    items: list[Any],
    total: int,
    page: int,
    page_size: int,
    message: str = "Success"
) -> dict[str, Any]:
    """
    创建分页成功响应

    Args:
        items: 数据列表
        total: 总数据量
        page: 当前页码
        page_size: 每页数量
        message: 成功消息

    Returns:
        统一格式的分页响应字典
    """
    total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
    return {
        "code": 0,
        "message": message,
        "data": {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }
    }
