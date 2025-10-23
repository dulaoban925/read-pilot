"""
文件存储抽象和实现

提供统一的文件存储接口:
- 本地文件系统存储 (开发环境)
- S3 兼容对象存储 (生产环境)
"""

import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import BinaryIO, Optional
from uuid import UUID

import aiofiles
import boto3
from botocore.exceptions import ClientError

from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class FileStorageError(Exception):
    """文件存储错误基类"""

    pass


class FileNotFoundError(FileStorageError):
    """文件未找到错误"""

    pass


class FileStorageBase(ABC):
    """
    文件存储抽象基类

    定义文件存储的统一接口
    """

    @abstractmethod
    async def save(
        self,
        file_content: bytes | BinaryIO,
        file_path: str,
        content_type: Optional[str] = None,
    ) -> str:
        """
        保存文件

        Args:
            file_content: 文件内容 (bytes 或文件对象)
            file_path: 文件路径 (相对路径,如 "user_id/document_id.pdf")
            content_type: 文件 MIME 类型

        Returns:
            文件存储路径或 URL

        Raises:
            FileStorageError: 存储失败
        """
        pass

    @abstractmethod
    async def get(self, file_path: str) -> bytes:
        """
        获取文件内容

        Args:
            file_path: 文件路径

        Returns:
            文件内容

        Raises:
            FileNotFoundError: 文件不存在
        """
        pass

    @abstractmethod
    async def delete(self, file_path: str) -> bool:
        """
        删除文件

        Args:
            file_path: 文件路径

        Returns:
            是否删除成功

        Raises:
            FileStorageError: 删除失败
        """
        pass

    @abstractmethod
    async def exists(self, file_path: str) -> bool:
        """
        检查文件是否存在

        Args:
            file_path: 文件路径

        Returns:
            文件是否存在
        """
        pass

    @abstractmethod
    def get_public_url(self, file_path: str, expires_in: int = 3600) -> str:
        """
        获取文件访问 URL

        Args:
            file_path: 文件路径
            expires_in: 过期时间 (秒)

        Returns:
            文件访问 URL
        """
        pass


class LocalFileStorage(FileStorageBase):
    """
    本地文件系统存储实现

    用于开发环境或小规模部署
    """

    def __init__(self, base_dir: Optional[str] = None):
        """
        初始化本地文件存储

        Args:
            base_dir: 基础目录路径,默认使用配置中的路径
        """
        self.base_dir = Path(base_dir or settings.UPLOAD_DIR)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        logger.info("local_file_storage_initialized", base_dir=str(self.base_dir))

    async def save(
        self,
        file_content: bytes | BinaryIO,
        file_path: str,
        content_type: Optional[str] = None,
    ) -> str:
        """保存文件到本地文件系统"""
        full_path = self.base_dir / file_path

        # 创建父目录
        full_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            # 写入文件
            if isinstance(file_content, bytes):
                async with aiofiles.open(full_path, "wb") as f:
                    await f.write(file_content)
            else:
                # 如果是文件对象,读取内容后写入
                content = file_content.read()
                async with aiofiles.open(full_path, "wb") as f:
                    await f.write(content)

            logger.info(
                "file_saved_locally",
                file_path=file_path,
                size_bytes=full_path.stat().st_size,
            )

            return file_path

        except Exception as e:
            logger.error("file_save_failed", file_path=file_path, error=str(e))
            raise FileStorageError(f"Failed to save file: {e}")

    async def get(self, file_path: str) -> bytes:
        """从本地文件系统获取文件"""
        full_path = self.base_dir / file_path

        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            async with aiofiles.open(full_path, "rb") as f:
                content = await f.read()
            return content
        except Exception as e:
            logger.error("file_read_failed", file_path=file_path, error=str(e))
            raise FileStorageError(f"Failed to read file: {e}")

    async def delete(self, file_path: str) -> bool:
        """从本地文件系统删除文件"""
        full_path = self.base_dir / file_path

        if not full_path.exists():
            logger.warning("file_delete_not_found", file_path=file_path)
            return False

        try:
            full_path.unlink()
            logger.info("file_deleted_locally", file_path=file_path)
            return True
        except Exception as e:
            logger.error("file_delete_failed", file_path=file_path, error=str(e))
            raise FileStorageError(f"Failed to delete file: {e}")

    async def exists(self, file_path: str) -> bool:
        """检查文件是否存在"""
        full_path = self.base_dir / file_path
        return full_path.exists()

    def get_public_url(self, file_path: str, expires_in: int = 3600) -> str:
        """
        获取本地文件访问 URL

        注意: 本地存储不支持预签名 URL,返回相对路径
        """
        return f"/files/{file_path}"


class S3FileStorage(FileStorageBase):
    """
    S3 兼容对象存储实现

    支持 AWS S3, MinIO, 阿里云 OSS 等
    """

    def __init__(
        self,
        bucket_name: Optional[str] = None,
        endpoint_url: Optional[str] = None,
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        region: Optional[str] = None,
    ):
        """
        初始化 S3 存储

        Args:
            bucket_name: 存储桶名称
            endpoint_url: S3 端点 URL (MinIO 等需要)
            access_key: 访问密钥
            secret_key: 密钥
            region: 区域
        """
        self.bucket_name = bucket_name or settings.S3_BUCKET_NAME
        self.endpoint_url = endpoint_url or settings.S3_ENDPOINT_URL
        self.region = region or settings.S3_REGION

        # 初始化 S3 客户端
        self.s3_client = boto3.client(
            "s3",
            endpoint_url=self.endpoint_url,
            aws_access_key_id=access_key or settings.S3_ACCESS_KEY,
            aws_secret_access_key=secret_key or settings.S3_SECRET_KEY,
            region_name=self.region,
        )

        logger.info(
            "s3_file_storage_initialized",
            bucket=self.bucket_name,
            endpoint=self.endpoint_url,
        )

    async def save(
        self,
        file_content: bytes | BinaryIO,
        file_path: str,
        content_type: Optional[str] = None,
    ) -> str:
        """上传文件到 S3"""
        try:
            extra_args = {}
            if content_type:
                extra_args["ContentType"] = content_type

            if isinstance(file_content, bytes):
                self.s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=file_path,
                    Body=file_content,
                    **extra_args,
                )
            else:
                self.s3_client.upload_fileobj(
                    file_content, self.bucket_name, file_path, ExtraArgs=extra_args
                )

            logger.info("file_uploaded_to_s3", file_path=file_path)
            return file_path

        except ClientError as e:
            logger.error("s3_upload_failed", file_path=file_path, error=str(e))
            raise FileStorageError(f"Failed to upload file to S3: {e}")

    async def get(self, file_path: str) -> bytes:
        """从 S3 下载文件"""
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=file_path)
            content = response["Body"].read()
            return content

        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                raise FileNotFoundError(f"File not found in S3: {file_path}")
            logger.error("s3_download_failed", file_path=file_path, error=str(e))
            raise FileStorageError(f"Failed to download file from S3: {e}")

    async def delete(self, file_path: str) -> bool:
        """从 S3 删除文件"""
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=file_path)
            logger.info("file_deleted_from_s3", file_path=file_path)
            return True

        except ClientError as e:
            logger.error("s3_delete_failed", file_path=file_path, error=str(e))
            raise FileStorageError(f"Failed to delete file from S3: {e}")

    async def exists(self, file_path: str) -> bool:
        """检查文件是否存在于 S3"""
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=file_path)
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return False
            raise FileStorageError(f"Failed to check file existence: {e}")

    def get_public_url(self, file_path: str, expires_in: int = 3600) -> str:
        """
        生成预签名 URL

        Args:
            file_path: 文件路径
            expires_in: 过期时间 (秒),默认 1 小时

        Returns:
            预签名 URL
        """
        try:
            url = self.s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket_name, "Key": file_path},
                ExpiresIn=expires_in,
            )
            return url
        except ClientError as e:
            logger.error(
                "presigned_url_generation_failed", file_path=file_path, error=str(e)
            )
            raise FileStorageError(f"Failed to generate presigned URL: {e}")


def get_file_storage() -> FileStorageBase:
    """
    获取文件存储实例

    根据配置返回本地存储或 S3 存储

    Returns:
        FileStorageBase 实例
    """
    if settings.FILE_STORAGE_TYPE == "s3":
        return S3FileStorage()
    else:
        return LocalFileStorage()
