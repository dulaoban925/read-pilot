"""
结构化日志配置 (Structured Logging)

使用 structlog 提供:
- 结构化日志输出 (JSON 格式)
- 上下文绑定
- 请求追踪
- 性能分析
"""

import logging
import sys
from typing import Any

import structlog
from structlog.types import EventDict, Processor

from app.core.config import settings


def add_app_context(
    logger: logging.Logger, method_name: str, event_dict: EventDict
) -> EventDict:
    """
    添加应用上下文信息到日志

    Args:
        logger: Logger 实例
        method_name: 方法名
        event_dict: 事件字典

    Returns:
        增强后的事件字典
    """
    event_dict["app"] = "readpilot"
    event_dict["environment"] = settings.ENVIRONMENT
    return event_dict


def drop_color_message_key(
    logger: logging.Logger, method_name: str, event_dict: EventDict
) -> EventDict:
    """
    移除 structlog 的颜色消息键 (仅用于 JSON 输出)

    Args:
        logger: Logger 实例
        method_name: 方法名
        event_dict: 事件字典

    Returns:
        清理后的事件字典
    """
    event_dict.pop("color_message", None)
    return event_dict


def setup_logging(log_level: str | None = None) -> None:
    """
    配置结构化日志系统

    Args:
        log_level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
                  默认从配置文件读取
    """
    log_level = log_level or settings.LOG_LEVEL

    # 配置 structlog 处理器链
    processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,  # 合并上下文变量
        structlog.stdlib.filter_by_level,  # 按级别过滤
        structlog.processors.TimeStamper(fmt="iso", utc=True),  # ISO 时间戳
        structlog.stdlib.add_logger_name,  # 添加 logger 名称
        structlog.stdlib.add_log_level,  # 添加日志级别
        structlog.stdlib.PositionalArgumentsFormatter(),  # 格式化位置参数
        add_app_context,  # 添加应用上下文
        structlog.processors.StackInfoRenderer(),  # 堆栈信息
        structlog.processors.format_exc_info,  # 异常信息格式化
        structlog.processors.UnicodeDecoder(),  # Unicode 解码
    ]

    # 根据环境选择输出格式
    if settings.ENVIRONMENT == "development":
        # 开发环境: 彩色控制台输出
        processors.append(structlog.dev.ConsoleRenderer(colors=True))
    else:
        # 生产环境: JSON 格式输出
        processors.extend(
            [
                drop_color_message_key,  # 移除颜色消息
                structlog.processors.JSONRenderer(sort_keys=True),  # JSON 渲染
            ]
        )

    # 配置 structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # 配置标准 logging 模块
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper()),
    )

    # 调整第三方库日志级别
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """
    获取结构化 logger 实例

    Args:
        name: Logger 名称,通常使用 __name__

    Returns:
        structlog BoundLogger 实例

    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("user_registered", user_id="123", email="user@example.com")
    """
    return structlog.get_logger(name)


# 全局 logger 实例
logger = get_logger(__name__)
