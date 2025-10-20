"""
User management API endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from models.user import (
    UserCreate,
    UserResponse,
    UserLogin,
    UserUpdate,
    UserPreferences
)
from services.database_service import db_service
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from config import settings

router = APIRouter(prefix="/users", tags=["users"])

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security
security = HTTPBearer()


def create_access_token(data: dict) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Verify JWT token"""
    try:
        token = credentials.credentials
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate):
    """Register a new user"""
    try:
        # Check if user already exists
        existing_user = await db_service.get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        # Hash password
        password_hash = pwd_context.hash(user_data.password)

        # Create user
        user = await db_service.create_user(
            email=user_data.email,
            name=user_data.name,
            password_hash=password_hash
        )

        return user

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/login")
async def login(credentials: UserLogin):
    """User login"""
    try:
        # Get user
        user = await db_service.get_user_by_email(credentials.email)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        # Verify password
        if not pwd_context.verify(credentials.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        # Update last login
        await db_service.update_user(user.id, last_login=datetime.utcnow())

        # Create access token
        access_token = create_access_token({"sub": user.id})

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": UserResponse.from_orm(user)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/me", response_model=UserResponse)
async def get_current_user(user_id: str = Depends(verify_token)):
    """Get current user information"""
    try:
        user = await db_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return user

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/me", response_model=UserResponse)
async def update_user(
    user_data: UserUpdate,
    user_id: str = Depends(verify_token)
):
    """Update user information"""
    try:
        update_data = {}

        if user_data.name:
            update_data["name"] = user_data.name

        if user_data.preferences:
            update_data["preferences"] = user_data.preferences.dict()

        user = await db_service.update_user(user_id, **update_data)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return user

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/me/preferences", response_model=UserPreferences)
async def update_preferences(
    preferences: UserPreferences,
    user_id: str = Depends(verify_token)
):
    """Update user preferences"""
    try:
        user = await db_service.update_user(
            user_id,
            preferences=preferences.dict()
        )

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return UserPreferences(**user.preferences)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/me/stats")
async def get_user_stats(user_id: str = Depends(verify_token)):
    """Get user learning statistics"""
    try:
        user = await db_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return {
            "reading_count": user.reading_count,
            "total_questions_asked": user.total_questions_asked,
            "quiz_scores": user.quiz_scores,
            "weak_topics": user.weak_topics,
            "mastered_topics": user.mastered_topics
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
