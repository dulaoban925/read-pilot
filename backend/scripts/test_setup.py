"""Test script to verify Phase 1 infrastructure setup"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))


async def test_database_init():
    """Test database initialization"""
    print("=" * 60)
    print("Testing Database Initialization")
    print("=" * 60)

    try:
        from app.db.session import init_db, close_db

        print("✓ Database modules imported successfully")

        # Initialize database
        await init_db()
        print("✓ Database tables created successfully")

        # Close connection
        await close_db()
        print("✓ Database connection closed successfully")

        return True
    except Exception as e:
        print(f"✗ Database initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_redis_connection():
    """Test Redis connection"""
    print("\n" + "=" * 60)
    print("Testing Redis Connection")
    print("=" * 60)

    try:
        from app.core.cache import cache_manager

        print("✓ Cache manager imported successfully")

        # Connect to Redis
        await cache_manager.connect()
        print("✓ Connected to Redis successfully")

        # Test write
        await cache_manager.set("test_key", "test_value", expire=60)
        print("✓ Write to Redis successful")

        # Test read
        value = await cache_manager.get("test_key")
        if value == "test_value":
            print(f"✓ Read from Redis successful: {value}")
        else:
            print(f"✗ Read failed, expected 'test_value', got '{value}'")
            return False

        # Test exists
        exists = await cache_manager.exists("test_key")
        if exists:
            print("✓ Key exists check successful")
        else:
            print("✗ Key exists check failed")
            return False

        # Test delete
        deleted = await cache_manager.delete("test_key")
        print(f"✓ Delete from Redis successful (deleted {deleted} keys)")

        # Test JSON operations
        test_data = {"name": "ReadPilot", "version": "0.1.0"}
        await cache_manager.set_json("test_json", test_data, expire=60)
        print("✓ JSON write successful")

        retrieved_data = await cache_manager.get_json("test_json")
        if retrieved_data == test_data:
            print(f"✓ JSON read successful: {retrieved_data}")
        else:
            print(f"✗ JSON read failed, expected {test_data}, got {retrieved_data}")
            return False

        # Cleanup
        await cache_manager.delete("test_json")
        await cache_manager.close()
        print("✓ Redis connection closed successfully")

        return True
    except Exception as e:
        print(f"✗ Redis connection failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_file_storage():
    """Test file storage functionality"""
    print("\n" + "=" * 60)
    print("Testing File Storage")
    print("=" * 60)

    try:
        from app.utils.file_storage import file_storage
        from app.core.config import settings
        import os

        print("✓ File storage module imported successfully")

        # Create test file
        test_content = b"This is a test file for ReadPilot"
        test_filename = "test_document.txt"

        # Save file
        file_info = await file_storage.save_file(test_content, test_filename)
        print(f"✓ File saved successfully")
        print(f"  - File hash: {file_info['file_hash']}")
        print(f"  - File path: {file_info['file_path']}")

        # Check if file exists
        exists = file_storage.file_exists(file_info['file_hash'])
        if exists:
            print("✓ File exists check successful")
        else:
            print("✗ File exists check failed")
            return False

        # Get file path
        file_path = file_storage.get_file_path(file_info['file_hash'])
        if file_path and os.path.exists(file_path):
            print(f"✓ File path retrieval successful: {file_path}")
        else:
            print("✗ File path retrieval failed")
            return False

        # Get storage stats
        stats = file_storage.get_storage_stats()
        print(f"✓ Storage stats retrieved:")
        print(f"  - Total files: {stats['total_files']}")
        print(f"  - Total size: {stats['total_size_mb']:.2f} MB")

        # Cleanup
        file_storage.delete_file(file_info['file_hash'])
        print("✓ Test file deleted successfully")

        return True
    except Exception as e:
        print(f"✗ File storage test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_file_validation():
    """Test file validation"""
    print("\n" + "=" * 60)
    print("Testing File Validation")
    print("=" * 60)

    try:
        from app.utils.file_validation import validate_file, ValidationResult

        print("✓ File validation module imported successfully")

        # Test valid PDF file (mock)
        test_pdf_content = b"%PDF-1.4\n%\xE2\xE3\xCF\xD3\n"  # PDF magic bytes
        result = validate_file(test_pdf_content, "test.pdf", len(test_pdf_content))

        if result.is_valid:
            print("✓ PDF validation successful")
            print(f"  - File type: {result.file_type}")
            print(f"  - MIME type: {result.mime_type}")
        else:
            print(f"✗ PDF validation failed: {result.error_message}")
            return False

        # Test file size limit
        large_content = b"x" * (51 * 1024 * 1024)  # 51MB
        result = validate_file(large_content, "large.pdf", len(large_content))

        if not result.is_valid and "size" in result.error_message.lower():
            print("✓ File size limit validation successful")
        else:
            print("✗ File size limit validation failed")
            return False

        # Test invalid extension
        result = validate_file(b"test content", "test.exe", 12)

        if not result.is_valid and "extension" in result.error_message.lower():
            print("✓ Invalid extension validation successful")
        else:
            print("✗ Invalid extension validation failed")
            return False

        print("✓ All validation tests passed")
        return True
    except Exception as e:
        print(f"✗ File validation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("ReadPilot Phase 1 Infrastructure Test Suite")
    print("=" * 60 + "\n")

    results = []

    # Test database (will fail if dependencies not installed)
    db_result = await test_database_init()
    results.append(("Database", db_result))

    # Test Redis (will fail if Redis not running)
    redis_result = await test_redis_connection()
    results.append(("Redis", redis_result))

    # Test file storage
    storage_result = await test_file_storage()
    results.append(("File Storage", storage_result))

    # Test file validation
    validation_result = await test_file_validation()
    results.append(("File Validation", validation_result))

    # Print summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{name:20s} : {status}")

    total = len(results)
    passed = sum(1 for _, result in results if result)

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! Phase 1 infrastructure is ready.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
