"""File Validation Utility"""
from pathlib import Path
from typing import Optional

from fastapi import HTTPException, UploadFile

from app.core.config import settings

# MIME type mapping for allowed file types
MIME_TYPE_MAPPING = {
    "application/pdf": ".pdf",
    "application/epub+zip": ".epub",
    "text/plain": ".txt",
    "text/markdown": ".md",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
}

# Reverse mapping: extension -> MIME type
EXTENSION_MIME_MAPPING = {v: k for k, v in MIME_TYPE_MAPPING.items()}


def validate_file_size(file: UploadFile, max_size: int = settings.MAX_UPLOAD_SIZE) -> None:
    """
    Validate file size.

    Args:
        file: FastAPI UploadFile object
        max_size: Maximum file size in bytes

    Raises:
        HTTPException: If file size exceeds limit
    """
    # Try to get file size from content-length header
    if hasattr(file, "size") and file.size is not None:
        if file.size > max_size:
            max_mb = max_size / (1024 * 1024)
            raise HTTPException(
                status_code=400,
                detail=f"File size exceeds {max_mb}MB limit"
            )


def validate_file_extension(filename: str) -> str:
    """
    Validate file extension.

    Args:
        filename: Name of the file

    Returns:
        Normalized file extension (e.g., ".pdf")

    Raises:
        HTTPException: If file extension is not allowed
    """
    if not filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required"
        )

    extension = Path(filename).suffix.lower()

    if not extension:
        raise HTTPException(
            status_code=400,
            detail="File must have an extension"
        )

    if extension not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type '{extension}' is not supported. "
                   f"Allowed types: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )

    return extension


def validate_mime_type(content: bytes, extension: str) -> str:
    """
    Validate file MIME type using magic bytes.

    Args:
        content: First bytes of the file (at least 2048 bytes recommended)
        extension: Expected file extension

    Returns:
        Detected MIME type

    Raises:
        HTTPException: If MIME type doesn't match extension
    """
    # Magic bytes detection for common file types
    magic_bytes = content[:8]

    # PDF: %PDF
    if magic_bytes.startswith(b"%PDF"):
        detected_type = "application/pdf"
        expected_ext = ".pdf"

    # EPUB: PK (ZIP archive)
    elif magic_bytes[:2] == b"PK":
        # EPUB is a ZIP file, need deeper inspection
        detected_type = "application/epub+zip"
        expected_ext = ".epub"

    # DOCX: PK (ZIP archive)
    elif magic_bytes[:2] == b"PK" and extension == ".docx":
        detected_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        expected_ext = ".docx"

    # Plain text files (TXT, MD) - no specific magic bytes
    elif extension in [".txt", ".md"]:
        # Check if content is valid UTF-8 text
        try:
            content[:1024].decode("utf-8")
            if extension == ".txt":
                detected_type = "text/plain"
            else:
                detected_type = "text/markdown"
            expected_ext = extension
        except UnicodeDecodeError:
            raise HTTPException(
                status_code=400,
                detail=f"File content is not valid text for {extension} file"
            )

    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unable to detect file type. File may be corrupted."
        )

    # Verify that detected type matches expected extension
    if expected_ext != extension:
        raise HTTPException(
            status_code=400,
            detail=f"File extension '{extension}' does not match file content "
                   f"(detected: {detected_type}). File may be renamed or corrupted."
        )

    return detected_type


async def validate_file(file: UploadFile) -> dict:
    """
    Perform comprehensive file validation.

    Args:
        file: FastAPI UploadFile object

    Returns:
        Dictionary with validation results:
        {
            "filename": str,
            "extension": str,
            "mime_type": str,
            "size": int
        }

    Raises:
        HTTPException: If validation fails
    """
    # Validate filename and extension
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")

    extension = validate_file_extension(file.filename)

    # Validate file size (if available)
    validate_file_size(file)

    # Read first chunk for MIME type validation
    content = await file.read(8192)  # Read first 8KB
    await file.seek(0)  # Reset file pointer

    # Validate MIME type using magic bytes
    mime_type = validate_mime_type(content, extension)

    # Get actual file size
    await file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    await file.seek(0)  # Reset to beginning

    # Final size check
    if file_size > settings.MAX_UPLOAD_SIZE:
        max_mb = settings.MAX_UPLOAD_SIZE / (1024 * 1024)
        raise HTTPException(
            status_code=400,
            detail=f"File size ({file_size / (1024 * 1024):.2f}MB) exceeds {max_mb}MB limit"
        )

    return {
        "filename": file.filename,
        "extension": extension,
        "mime_type": mime_type,
        "size": file_size,
    }


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing dangerous characters.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename
    """
    # Remove path separators and null bytes
    dangerous_chars = ["/", "\\", "\0", "..", "~"]
    sanitized = filename

    for char in dangerous_chars:
        sanitized = sanitized.replace(char, "_")

    # Limit length
    name = Path(sanitized).stem[:200]
    ext = Path(sanitized).suffix
    return name + ext
