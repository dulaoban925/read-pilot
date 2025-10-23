#!/usr/bin/env python3
"""
完整测试摘要生成功能（通过 Celery）
"""

import asyncio
import hashlib
import sys
import time

from sqlalchemy import select


async def test_full_summary_generation():
    """完整测试摘要生成流程"""
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🧪 完整测试摘要生成功能")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print()

    # 测试文档内容
    TEST_DOCUMENT_TEXT = """
# Python 编程语言完整指南

Python 是一种高级编程语言，由 Guido van Rossum 在 1991 年首次发布。它以其简洁的语法和强大的功能而闻名。

## 核心特点

### 1. 易于学习和使用
Python 的语法设计简洁明了，接近自然语言，降低了编程门槛。初学者可以快速上手，专业开发者也能高效编写代码。

### 2. 丰富的标准库
Python 自带"batteries included"理念，提供了大量标准库，涵盖文件操作、网络通信、数据处理等常见需求。

### 3. 跨平台支持
Python 可以在 Windows、macOS、Linux 等多个操作系统上运行，实现"一次编写，到处运行"。

### 4. 强大的社区支持
Python 拥有全球最活跃的开发者社区之一，提供了海量的第三方库和框架，如 Django、Flask、NumPy、Pandas 等。

## 应用领域

### Web 开发
使用 Django、Flask 等框架可以快速构建高性能的 Web 应用。

### 数据科学
NumPy、Pandas、Matplotlib 等库使 Python 成为数据分析和可视化的首选语言。

### 人工智能与机器学习
TensorFlow、PyTorch、scikit-learn 等框架让 Python 在 AI 领域占据主导地位。

### 自动化脚本
Python 简洁的语法使其成为编写自动化脚本和工具的理想选择。

### 游戏开发
Pygame 等库支持 2D 游戏开发。

### 网络爬虫
Beautiful Soup、Scrapy 等工具使网络数据采集变得简单高效。

## 总结

Python 既适合初学者入门编程，也适合专业开发者构建复杂的企业级应用。其强大的生态系统和活跃的社区使其成为最受欢迎的编程语言之一。
"""

    try:
        # 导入所需模块
        from uuid import uuid4

        from app.db.session import get_async_session_context
        from app.models.ai_summary import AISummary
        from app.models.document import Document
        from app.tasks.document_processing import generate_summary_task

        print("1️⃣  创建测试文档...")

        # 创建测试文档
        async with get_async_session_context() as db:
            # 检查是否已存在测试文档
            stmt = select(Document).where(Document.title == "Python 编程语言完整指南 (测试)")
            result = await db.execute(stmt)
            document = result.scalar_one_or_none()

            if document:
                print(f"   ℹ️  使用现有测试文档: {document.id}")
            else:
                document = Document(
                    id=str(uuid4()),
                    user_id="test-user",
                    title="Python 编程语言完整指南 (测试)",
                    file_path="/tmp/test_python_guide.md",
                    file_hash=hashlib.sha256(TEST_DOCUMENT_TEXT.encode()).hexdigest(),
                    file_size=len(TEST_DOCUMENT_TEXT),
                    file_type="md",
                    parsed_content=TEST_DOCUMENT_TEXT,
                    processing_status="completed",
                    is_indexed=False,
                )
                db.add(document)
                await db.commit()
                await db.refresh(document)
                print(f"   ✓ 测试文档已创建: {document.id}")

            document_id = document.id

        print()
        print("2️⃣  触发摘要生成任务...")
        print(f"   文档ID: {document_id}")
        print(f"   深度: detailed")

        # 触发 Celery 任务
        result = generate_summary_task.apply_async(
            args=(document_id, "detailed"), expires=300
        )

        print(f"   ✓ 任务已提交")
        print(f"   任务ID: {result.id}")
        print()

        print("3️⃣  等待任务完成...")
        print("   (最长等待 60 秒)")

        # 等待任务完成
        start_time = time.time()
        max_wait = 60

        while time.time() - start_time < max_wait:
            if result.ready():
                break
            print(f"   ⏳ 等待中... ({int(time.time() - start_time)}s)")
            await asyncio.sleep(2)

        if not result.ready():
            print()
            print(f"   ⚠️  任务未在 {max_wait} 秒内完成")
            print(f"   任务状态: {result.state}")
            return False

        print()
        print(f"   ✓ 任务完成! (耗时: {int(time.time() - start_time)}s)")
        print(f"   任务状态: {result.state}")

        # 检查任务结果
        if result.failed():
            print()
            print(f"   ❌ 任务失败!")
            print(f"   错误: {result.info}")
            return False

        print()
        print("4️⃣  验证数据库中的摘要...")

        # 查询数据库中的摘要
        async with get_async_session_context() as db:
            stmt = select(AISummary).where(AISummary.document_id == document_id)
            result = await db.execute(stmt)
            summary = result.scalar_one_or_none()

            if not summary:
                print("   ❌ 数据库中未找到摘要记录")
                return False

            print(f"   ✓ 摘要记录已找到")
            print(f"   摘要ID: {summary.id}")
            print(f"   类型: {summary.summary_type}")
            print()

            # 显示摘要内容
            print("5️⃣  摘要内容:")
            print()
            print(f"📝 抽象:")
            print(f"   {summary.content.get('abstract', 'N/A')[:200]}...")
            print()

            key_insights = summary.content.get("key_insights", [])
            print(f"💡 关键见解 ({len(key_insights)} 条):")
            for i, insight in enumerate(key_insights[:3], 1):
                print(f"   {i}. {insight}")
            if len(key_insights) > 3:
                print(f"   ... (还有 {len(key_insights) - 3} 条)")
            print()

            main_concepts = summary.content.get("main_concepts", [])
            print(f"🔑 主要概念 ({len(main_concepts)} 个):")
            print(f"   {', '.join(main_concepts[:6])}")
            if len(main_concepts) > 6:
                print(f"   ... (还有 {len(main_concepts) - 6} 个)")
            print()

            # AI 元数据
            if summary.ai_metadata:
                print(f"🤖 AI 元数据:")
                print(f"   模型: {summary.ai_metadata.get('model', 'N/A')}")
                print(f"   深度: {summary.ai_metadata.get('depth', 'N/A')}")
            print()

            # 纯文本版本
            print(f"📄 纯文本版本 (前 300 字符):")
            print(f"   {summary.text[:300]}...")
            print()

        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("✅ 测试通过! 摘要生成功能工作正常")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        return True

    except Exception as e:
        print()
        print(f"❌ 测试失败: {str(e)}")
        print()
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    try:
        success = asyncio.run(test_full_summary_generation())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被中断")
        sys.exit(1)
