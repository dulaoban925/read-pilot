#!/usr/bin/env python3
"""
测试摘要生成功能

此脚本将:
1. 创建测试文档记录
2. 触发摘要生成任务
3. 验证摘要结果
"""

import asyncio
import sys
from uuid import uuid4

from sqlalchemy import select

from app.core.config import settings
from app.db.session import async_session_maker
from app.models.document import Document
from app.models.ai_summary import AISummary
from app.tasks.document_processing import generate_summary_task


# 测试文档内容
TEST_DOCUMENT_TEXT = """
# Python 编程语言简介

Python 是一种高级、解释型、交互式和面向对象的脚本语言。Python 的设计哲学强调代码的可读性和简洁的语法。

## 主要特点

1. **易于学习**: Python 有相对较少的关键字,结构简单,语法清晰,学习起来更加简单。
2. **易于阅读**: Python 代码定义的更清晰,用缩进来组织代码块。
3. **易于维护**: Python 的成功在于它的源代码相当容易维护。
4. **广泛的标准库**: Python 的标准库很庞大,包含了各种模块和函数。
5. **可移植性**: Python 可以运行在多种硬件平台和操作系统上。

## 应用领域

- Web 开发 (Django, Flask)
- 数据科学和机器学习 (NumPy, Pandas, Scikit-learn)
- 人工智能 (TensorFlow, PyTorch)
- 自动化脚本
- 游戏开发
- 桌面应用程序

## 总结

Python 是一门功能强大且易于学习的编程语言,适合初学者入门,也适合专业开发人员使用。
它在数据科学、人工智能、Web 开发等领域都有广泛应用。
"""


async def create_test_document() -> str:
    """创建测试文档"""
    import hashlib

    async with async_session_maker() as db:
        # 计算文件hash
        file_hash = hashlib.sha256(TEST_DOCUMENT_TEXT.encode()).hexdigest()

        # 创建测试文档
        document = Document(
            id=str(uuid4()),
            user_id="test-user-123",  # 测试用户ID
            title="Python 编程语言简介",
            file_path="/tmp/test_python_intro.txt",
            file_hash=file_hash,
            file_type="txt",
            file_size=len(TEST_DOCUMENT_TEXT),
            word_count=len(TEST_DOCUMENT_TEXT.split()),
            processing_status="completed",  # 直接标记为已完成
            parsed_content={"text": TEST_DOCUMENT_TEXT},  # 保存解析后的文本
        )

        db.add(document)
        await db.commit()

        print(f"✅ 创建测试文档: {document.id}")
        print(f"   标题: {document.title}")
        print(f"   字数: {document.word_count}")
        return document.id


async def check_summary(document_id: str) -> bool:
    """检查摘要是否生成成功"""
    async with async_session_maker() as db:
        result = await db.execute(
            select(AISummary).where(AISummary.document_id == document_id)
        )
        summary = result.scalar_one_or_none()

        if summary:
            print(f"\n✅ 摘要生成成功!")
            print(f"   摘要ID: {summary.id}")
            print(f"   深度: {summary.depth_level}")
            print(f"   模型: {summary.model_used}")
            print(f"\n📝 摘要内容:")
            print(f"   抽象: {summary.abstract[:200]}...")
            print(f"   关键见解数: {len(summary.key_insights)}")
            print(f"   主要概念数: {len(summary.main_concepts)}")

            if summary.key_insights:
                print(f"\n💡 关键见解:")
                for i, insight in enumerate(summary.key_insights[:3], 1):
                    print(f"   {i}. {insight}")

            if summary.main_concepts:
                print(f"\n🔑 主要概念:")
                print(f"   {', '.join(summary.main_concepts[:5])}")

            return True
        else:
            print(f"❌ 未找到摘要")
            return False


async def test_summary_generation():
    """测试摘要生成功能"""
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🧪 测试摘要生成功能")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print()

    # 1. 创建测试文档
    print("📄 1. 创建测试文档...")
    document_id = await create_test_document()
    print()

    # 2. 触发摘要生成任务
    print("⚙️  2. 触发摘要生成任务...")
    print(f"   文档ID: {document_id}")

    # 检查 OpenAI API Key
    if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY.startswith("your-"):
        print()
        print("❌ 错误: OPENAI_API_KEY 未配置!")
        print("   请在 .env 文件中设置有效的 API Key")
        return False

    try:
        # 触发异步任务
        task_result = generate_summary_task.apply_async(
            args=[document_id, "detailed"],
            countdown=2  # 2秒后执行
        )

        print(f"   任务ID: {task_result.id}")
        print(f"   状态: {task_result.state}")
        print()

        # 3. 等待任务完成
        print("⏳ 3. 等待任务完成 (最多30秒)...")

        # 等待任务完成
        result = task_result.get(timeout=30)

        print(f"   任务状态: {result.get('status')}")
        print(f"   摘要ID: {result.get('summary_id')}")
        print()

        # 4. 验证摘要
        print("✓ 4. 验证摘要结果...")
        success = await check_summary(document_id)

        print()
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        if success:
            print("✅ 测试通过! 摘要生成功能正常")
        else:
            print("❌ 测试失败! 摘要未生成")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        return success

    except Exception as e:
        print()
        print(f"❌ 错误: {str(e)}")
        print()
        print("可能的原因:")
        print("  1. Celery Worker 未运行")
        print("  2. OpenAI API Key 无效")
        print("  3. 网络连接问题")
        print()
        print("请检查:")
        print("  - Celery Worker: make celery")
        print("  - API Key: backend/.env")
        print("  - 网络: ping api.openai.com")
        return False


if __name__ == "__main__":
    print()
    try:
        success = asyncio.run(test_summary_generation())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被中断")
        sys.exit(1)
