#!/usr/bin/env python3
"""
直接测试 AI Service 的摘要生成功能 (不通过 Celery)
"""

import asyncio
import os
import sys

# 禁用代理以避免 SSL 证书问题
os.environ['HTTP_PROXY'] = ''
os.environ['HTTPS_PROXY'] = ''
os.environ['http_proxy'] = ''
os.environ['https_proxy'] = ''


async def test_ai_service():
    """测试 AI Service"""
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🧪 测试 AI Service 摘要生成")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print()

    # 测试文本
    test_text = """
# Python 编程语言

Python 是一种高级编程语言,以其简洁的语法和强大的功能而闻名。

## 主要特点
1. 易于学习和使用
2. 丰富的标准库
3. 跨平台支持
4. 强大的社区支持

## 应用领域
- Web 开发
- 数据科学
- 人工智能
- 自动化脚本

Python 适合初学者入门,也适合专业开发。
"""

    try:
        from app.services.ai_service import get_ai_service

        print("1️⃣  初始化 AI Service...")
        ai_service = get_ai_service()
        print(f"   ✓ 已初始化")
        print(f"   主提供商: {ai_service.primary_provider_name}")
        print(f"   可用提供商: {list(ai_service.providers.keys())}")
        print()

        print("2️⃣  生成简要摘要...")
        brief_summary = await ai_service.generate_summary(
            text=test_text,
            depth="brief"
        )

        print("   ✓ 简要摘要生成成功!")
        print(f"   模型: {brief_summary.get('model')}")
        print(f"   抽象: {brief_summary.get('abstract')[:100]}...")
        print(f"   关键见解数: {len(brief_summary.get('key_insights', []))}")
        print(f"   主要概念数: {len(brief_summary.get('main_concepts', []))}")

        if brief_summary.get('key_insights'):
            print(f"\n   💡 关键见解:")
            for insight in brief_summary['key_insights'][:2]:
                print(f"      • {insight}")

        if brief_summary.get('main_concepts'):
            print(f"\n   🔑 主要概念: {', '.join(brief_summary['main_concepts'][:5])}")
        print()

        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("✅ 测试通过! AI Service 工作正常")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        return True

    except Exception as e:
        print()
        print(f"❌ 错误: {str(e)}")
        print()

        # 检查常见问题
        import traceback
        traceback.print_exc()

        print("\n可能的原因:")
        print("  1. OpenAI API Key 未配置或无效")
        print("  2. API 配额已用尽 (Rate Limit)")
        print("  3. 网络连接问题")
        print()
        print("解决方法:")
        print("  - 检查 .env 文件中的 OPENAI_API_KEY")
        print("  - 访问 https://platform.openai.com/account/usage 查看配额")
        print("  - 确保网络可以访问 api.openai.com")
        return False


if __name__ == "__main__":
    try:
        success = asyncio.run(test_ai_service())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被中断")
        sys.exit(1)
