"""
认证服务 (Authentication Service)

提供用户认证相关的业务逻辑:
- 用户注册
- 用户登录
- Token 刷新
- 密码验证
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token, verify_password
from app.models.user import User
from app.schemas.auth import TokenPair, UserCreate, UserLogin
from app.utils.logger import get_logger

logger = get_logger(__name__)


class AuthenticationError(Exception):
    """认证错误基类"""

    pass


class InvalidCredentialsError(AuthenticationError):
    """无效凭证错误"""

    pass


class UserAlreadyExistsError(AuthenticationError):
    """用户已存在错误"""

    pass


class AuthService:
    """
    认证服务类

    处理用户认证相关的所有业务逻辑
    """

    def __init__(self, db: AsyncSession):
        """
        初始化认证服务

        Args:
            db: 数据库会话
        """
        self.db = db

    async def register_user(self, user_data: UserCreate) -> User:
        """
        注册新用户

        Args:
            user_data: 用户注册数据

        Returns:
            创建的用户对象

        Raises:
            UserAlreadyExistsError: 用户已存在
        """
        # 检查邮箱是否已存在
        existing_user = await self._get_user_by_email(user_data.email)
        if existing_user:
            logger.warning(
                "registration_failed_email_exists",
                email=user_data.email,
            )
            raise UserAlreadyExistsError(f"Email {user_data.email} already registered")

        # 创建新用户
        user = User(
            email=user_data.email,
            password_hash=user_data.password,  # User 模型会自动哈希密码
            display_name=user_data.display_name,
        )

        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        logger.info(
            "user_registered",
            user_id=str(user.id),
            email=user.email,
        )

        return user

    async def login_user(self, login_data: UserLogin) -> tuple[User, TokenPair]:
        """
        用户登录

        Args:
            login_data: 登录凭证

        Returns:
            用户对象和 Token 对

        Raises:
            InvalidCredentialsError: 凭证无效
        """
        # 获取用户
        user = await self._get_user_by_email(login_data.email)
        if not user:
            logger.warning(
                "login_failed_user_not_found",
                email=login_data.email,
            )
            raise InvalidCredentialsError("Invalid email or password")

        # 验证密码
        if not verify_password(login_data.password, user.password_hash):
            logger.warning(
                "login_failed_invalid_password",
                user_id=str(user.id),
                email=user.email,
            )
            raise InvalidCredentialsError("Invalid email or password")

        # 检查账户是否激活
        if not user.is_active:
            logger.warning(
                "login_failed_account_inactive",
                user_id=str(user.id),
                email=user.email,
            )
            raise InvalidCredentialsError("Account is inactive")

        # 更新最后登录时间
        user.last_login_at = datetime.now(timezone.utc)
        await self.db.commit()

        # 生成 Token
        tokens = self._generate_tokens(user.id)

        logger.info(
            "user_logged_in",
            user_id=str(user.id),
            email=user.email,
        )

        return user, tokens

    async def refresh_access_token(
        self, user_id: UUID, refresh_token: str
    ) -> TokenPair:
        """
        刷新访问 Token

        Args:
            user_id: 用户 ID
            refresh_token: 刷新 Token (用于验证)

        Returns:
            新的 Token 对

        Raises:
            InvalidCredentialsError: Token 无效
        """
        # 获取用户
        user = await self._get_user_by_id(user_id)
        if not user or not user.is_active:
            raise InvalidCredentialsError("Invalid user")

        # 生成新 Token
        tokens = self._generate_tokens(user.id)

        logger.info(
            "access_token_refreshed",
            user_id=str(user.id),
        )

        return tokens

    async def _get_user_by_email(self, email: str) -> Optional[User]:
        """
        根据邮箱获取用户

        Args:
            email: 用户邮箱

        Returns:
            用户对象或 None
        """
        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def _get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """
        根据 ID 获取用户

        Args:
            user_id: 用户 ID

        Returns:
            用户对象或 None
        """
        stmt = select(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    def _generate_tokens(self, user_id: UUID) -> TokenPair:
        """
        生成 Token 对

        Args:
            user_id: 用户 ID

        Returns:
            访问 Token 和刷新 Token
        """
        access_token = create_access_token(
            data={"sub": str(user_id)},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )

        refresh_token = create_refresh_token(
            data={"sub": str(user_id)},
            expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        )

        return TokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )
