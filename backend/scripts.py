"""
Scripts for Poetry command shortcuts
使用方法:
    poetry run dev      # 开发模式 (热重载)
    poetry run prod     # 生产模式
    poetry run test     # 运行测试
    poetry run lint     # 代码检查
    poetry run format   # 代码格式化
"""
import subprocess
import sys


def dev():
    """启动开发服务器 (热重载)"""
    subprocess.run([
        "uvicorn", "app.main:app",
        "--reload",
        "--host", "0.0.0.0",
        "--port", "8000"
    ])


def prod():
    """启动生产服务器"""
    subprocess.run([
        "uvicorn", "app.main:app",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--workers", "4"
    ])


def test():
    """运行测试"""
    subprocess.run(["pytest", "app/tests/", "-v"])


def lint():
    """代码检查"""
    print("🔍 Running Ruff linter...")
    result = subprocess.run(["ruff", "check", "app/"])
    if result.returncode == 0:
        print("✅ No linting errors found!")
    return result.returncode


def format():
    """代码格式化"""
    print("🎨 Formatting code with Ruff...")
    subprocess.run(["ruff", "format", "app/"])
    print("✅ Code formatted!")


def db_init():
    """初始化数据库"""
    print("🗄️  Initializing database...")
    subprocess.run(["alembic", "init", "alembic"])


def db_migrate():
    """创建数据库迁移"""
    message = input("Migration message: ")
    subprocess.run(["alembic", "revision", "--autogenerate", "-m", message])


def db_upgrade():
    """应用数据库迁移"""
    print("⬆️  Upgrading database...")
    subprocess.run(["alembic", "upgrade", "head"])
