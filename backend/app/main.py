"""FastAPI Application Entry Point"""
from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.schemas.response import error, success

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print(f"🚀 Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    print(f"📝 Environment: {settings.ENVIRONMENT}")
    print(f"🔗 API URL: {settings.API_V1_PREFIX}")

    yield

    # Shutdown
    print("👋 Shutting down application")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
    redirect_slashes=False,  # Disable automatic trailing slash redirects
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 全局异常处理器 - HTTP异常
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """统一处理HTTP异常"""
    return JSONResponse(
        status_code=exc.status_code,
        content=error(
            code=exc.status_code,
            message=exc.detail or "An error occurred",
            data=None
        )
    )


# 全局异常处理器 - 验证异常
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """统一处理请求验证异常"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error(
            code=422,
            message="Validation error",
            data={"errors": exc.errors()}
        )
    )


# 全局异常处理器 - 通用异常
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """统一处理未捕获的异常"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error(
            code=500,
            message="Internal server error",
            data=None
        )
    )


@app.get("/")
async def root():
    """Root endpoint"""
    return success(
        data={
            "version": settings.VERSION,
            "docs": "/docs",
        },
        message=f"Welcome to {settings.PROJECT_NAME}"
    )


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return success(
        data={
            "status": "healthy",
            "environment": settings.ENVIRONMENT,
            "version": settings.VERSION,
        },
        message="System is healthy"
    )


# Include routers
from app.api.v1 import api_router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)
