"""
SQLAlchemy 基础模型类

提供所有模型共享的基础功能:
- 主键 (id)
- 时间戳 (created_at, updated_at)
- 通用方法 (to_dict, etc.)
"""

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """所有模型的抽象基类"""

    pass


class TimestampMixin:
    """时间戳 Mixin - 提供 created_at 和 updated_at 字段"""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="创建时间",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新时间",
    )


class UUIDMixin:
    """UUID 主键 Mixin"""

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        comment="唯一标识符",
    )


class BaseModel(Base, UUIDMixin, TimestampMixin):
    """
    基础模型类 - 所有业务模型的父类

    提供:
    - UUID 主键
    - 创建和更新时间戳
    - 通用辅助方法
    """

    __abstract__ = True

    def to_dict(self, exclude: set[str] | None = None) -> dict[str, Any]:
        """
        将模型转换为字典

        Args:
            exclude: 需要排除的字段名集合

        Returns:
            模型的字典表示
        """
        exclude = exclude or set()
        result = {}

        for column in self.__table__.columns:
            if column.name not in exclude:
                value = getattr(self, column.name)
                # 转换 datetime 为 ISO 格式字符串
                if isinstance(value, datetime):
                    result[column.name] = value.isoformat()
                # 转换 UUID 为字符串
                elif hasattr(value, "__str__"):
                    result[column.name] = str(value)
                else:
                    result[column.name] = value

        return result

    def __repr__(self) -> str:
        """字符串表示"""
        class_name = self.__class__.__name__
        id_value = getattr(self, "id", None)
        return f"<{class_name}(id={id_value})>"
