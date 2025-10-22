"""File Storage Utility"""
import hashlib
from pathlib import Path
from typing import BinaryIO

from fastapi import UploadFile

from app.core.config import settings


class FileStorage:
    """File storage manager for handling document uploads"""

    def __init__(self, base_path: str = settings.UPLOAD_DIR):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def _compute_hash(self, content: bytes) -> str:
        """
        Compute SHA-256 hash of file content.

        Args:
            content: File content as bytes

        Returns:
            Hexadecimal hash string
        """
        return hashlib.sha256(content).hexdigest()

    def _get_file_path(self, file_hash: str, extension: str) -> Path:
        """
        Get file path using hash-based directory structure.

        Args:
            file_hash: SHA-256 hash of file
            extension: File extension (e.g., ".pdf")

        Returns:
            Path object for the file
        """
        # Use first 2 characters of hash for directory sharding
        shard_dir = self.base_path / file_hash[:2]
        shard_dir.mkdir(exist_ok=True)

        return shard_dir / f"{file_hash}{extension}"

    async def save_file(self, file: UploadFile) -> dict:
        """
        Save uploaded file to local storage.

        Args:
            file: FastAPI UploadFile object

        Returns:
            Dictionary with file information:
            {
                "file_hash": str,
                "file_path": str,
                "file_size": int,
                "file_name": str
            }
        """
        # Read file content
        content = await file.read()
        file_size = len(content)

        # Compute hash
        file_hash = self._compute_hash(content)

        # Get file extension
        file_name = file.filename or "document"
        extension = Path(file_name).suffix or ".bin"

        # Get storage path
        file_path = self._get_file_path(file_hash, extension)

        # Check if file already exists (deduplication)
        if not file_path.exists():
            # Write file to disk
            with open(file_path, "wb") as f:
                f.write(content)

        return {
            "file_hash": file_hash,
            "file_path": str(file_path),
            "file_size": file_size,
            "file_name": file_name,
        }

    def get_file_path(self, file_hash: str, extension: str = "") -> Path:
        """
        Get path to a stored file.

        Args:
            file_hash: SHA-256 hash of file
            extension: File extension (optional, will search if not provided)

        Returns:
            Path object for the file

        Raises:
            FileNotFoundError: If file doesn't exist
        """
        if extension:
            file_path = self._get_file_path(file_hash, extension)
            if file_path.exists():
                return file_path
        else:
            # Search for file with any extension
            shard_dir = self.base_path / file_hash[:2]
            if shard_dir.exists():
                for file_path in shard_dir.glob(f"{file_hash}.*"):
                    return file_path

        raise FileNotFoundError(f"File with hash {file_hash} not found")

    def delete_file(self, file_hash: str, extension: str = "") -> bool:
        """
        Delete a stored file.

        Args:
            file_hash: SHA-256 hash of file
            extension: File extension (optional)

        Returns:
            True if file was deleted, False if not found
        """
        try:
            file_path = self.get_file_path(file_hash, extension)
            file_path.unlink()
            return True
        except FileNotFoundError:
            return False

    def file_exists(self, file_hash: str, extension: str = "") -> bool:
        """
        Check if a file exists in storage.

        Args:
            file_hash: SHA-256 hash of file
            extension: File extension (optional)

        Returns:
            True if file exists
        """
        try:
            self.get_file_path(file_hash, extension)
            return True
        except FileNotFoundError:
            return False

    def get_storage_stats(self) -> dict:
        """
        Get storage statistics.

        Returns:
            Dictionary with storage statistics:
            {
                "total_files": int,
                "total_size": int,  # in bytes
                "shard_count": int
            }
        """
        total_files = 0
        total_size = 0

        for shard_dir in self.base_path.iterdir():
            if shard_dir.is_dir():
                for file_path in shard_dir.iterdir():
                    if file_path.is_file():
                        total_files += 1
                        total_size += file_path.stat().st_size

        return {
            "total_files": total_files,
            "total_size": total_size,
            "shard_count": len(list(self.base_path.iterdir())),
        }


# Global storage instance
file_storage = FileStorage()
