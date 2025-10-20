"""
Database service for managing data persistence
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from config import settings
from models.user import User
from models.document import Document, DocumentChunk
from models.session import Session, Message
from typing import Optional, List
import uuid


class DatabaseService:
    """Database service for CRUD operations"""

    def __init__(self):
        self.engine = create_async_engine(
            settings.DATABASE_URL,
            echo=settings.DB_ECHO
        )
        self.async_session = sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

    async def create_user(self, email: str, name: str, password_hash: str) -> User:
        """Create a new user"""
        async with self.async_session() as session:
            user = User(
                id=str(uuid.uuid4()),
                email=email,
                name=name,
                password_hash=password_hash
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        async with self.async_session() as session:
            result = await session.execute(
                select(User).where(User.email == email)
            )
            return result.scalars().first()

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        async with self.async_session() as session:
            result = await session.execute(
                select(User).where(User.id == user_id)
            )
            return result.scalars().first()

    async def update_user(self, user_id: str, **kwargs) -> Optional[User]:
        """Update user information"""
        async with self.async_session() as session:
            user = await self.get_user_by_id(user_id)
            if user:
                for key, value in kwargs.items():
                    setattr(user, key, value)
                await session.commit()
                await session.refresh(user)
            return user

    async def create_document(
        self,
        user_id: str,
        title: str,
        file_name: str,
        file_type: str,
        file_size: int,
        file_path: str
    ) -> Document:
        """Create a new document"""
        async with self.async_session() as session:
            document = Document(
                id=str(uuid.uuid4()),
                user_id=user_id,
                title=title,
                file_name=file_name,
                file_type=file_type,
                file_size=file_size,
                file_path=file_path
            )
            session.add(document)
            await session.commit()
            await session.refresh(document)
            return document

    async def get_document(self, document_id: str) -> Optional[Document]:
        """Get document by ID"""
        async with self.async_session() as session:
            result = await session.execute(
                select(Document).where(Document.id == document_id)
            )
            return result.scalars().first()

    async def get_user_documents(self, user_id: str) -> List[Document]:
        """Get all documents for a user"""
        async with self.async_session() as session:
            result = await session.execute(
                select(Document).where(Document.user_id == user_id)
                .order_by(Document.created_at.desc())
            )
            return result.scalars().all()

    async def update_document(self, document_id: str, **kwargs) -> Optional[Document]:
        """Update document information"""
        async with self.async_session() as session:
            document = await self.get_document(document_id)
            if document:
                for key, value in kwargs.items():
                    setattr(document, key, value)
                await session.commit()
                await session.refresh(document)
            return document

    async def create_session(
        self,
        user_id: str,
        document_id: Optional[str] = None,
        session_type: str = "chat"
    ) -> Session:
        """Create a new conversation session"""
        async with self.async_session() as session:
            conv_session = Session(
                id=str(uuid.uuid4()),
                user_id=user_id,
                document_id=document_id,
                session_type=session_type
            )
            session.add(conv_session)
            await session.commit()
            await session.refresh(conv_session)
            return conv_session

    async def get_session(self, session_id: str) -> Optional[Session]:
        """Get session by ID"""
        async with self.async_session() as session:
            result = await session.execute(
                select(Session).where(Session.id == session_id)
            )
            return result.scalars().first()

    async def create_message(
        self,
        session_id: str,
        role: str,
        content: str,
        agent_name: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> Message:
        """Create a new message"""
        async with self.async_session() as session:
            message = Message(
                id=str(uuid.uuid4()),
                session_id=session_id,
                role=role,
                content=content,
                agent_name=agent_name,
                metadata=metadata or {}
            )
            session.add(message)
            await session.commit()
            await session.refresh(message)
            return message

    async def get_session_messages(self, session_id: str) -> List[Message]:
        """Get all messages for a session"""
        async with self.async_session() as session:
            result = await session.execute(
                select(Message).where(Message.session_id == session_id)
                .order_by(Message.created_at.asc())
            )
            return result.scalars().all()


# Global database service instance
db_service = DatabaseService()
