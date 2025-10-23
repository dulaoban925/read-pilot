
'use client'

import Link from 'next/link'
import { useAuthStore } from '@/stores/authStore'
import { Button } from '@/components/ui/Button'

export default function Home() {
  const { isAuthenticated } = useAuthStore()

  return (
    <div className="min-h-[calc(100vh-64px)] flex items-center justify-center px-4">
      <div className="max-w-4xl mx-auto text-center">
        {/* Hero Section */}
        <div className="mb-12">
          <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6">
            ReadPilot
          </h1>
          <p className="text-xl md:text-2xl text-gray-600 mb-4">
            AI智能阅读助手
          </p>
          <p className="text-lg text-gray-500 max-w-2xl mx-auto">
            使用AI技术增强您的阅读体验。上传文档、生成摘要、智能问答，让阅读更高效。
          </p>
        </div>

        {/* Features */}
        <div className="grid md:grid-cols-3 gap-8 mb-12">
          <div className="p-6 bg-white rounded-lg border border-gray-200">
            <div className="text-4xl mb-4">📚</div>
            <h3 className="text-lg font-semibold mb-2">文档管理</h3>
            <p className="text-gray-600 text-sm">
              支持PDF、EPUB、DOCX、TXT、Markdown等多种格式
            </p>
          </div>
          <div className="p-6 bg-white rounded-lg border border-gray-200">
            <div className="text-4xl mb-4">🤖</div>
            <h3 className="text-lg font-semibold mb-2">AI摘要</h3>
            <p className="text-gray-600 text-sm">
              快速生成文档摘要，提取关键信息和核心观点
            </p>
          </div>
          <div className="p-6 bg-white rounded-lg border border-gray-200">
            <div className="text-4xl mb-4">💬</div>
            <h3 className="text-lg font-semibold mb-2">智能问答</h3>
            <p className="text-gray-600 text-sm">
              基于文档内容的上下文问答，快速找到答案
            </p>
          </div>
        </div>

        {/* CTA Buttons */}
        <div className="flex gap-4 justify-center">
          {isAuthenticated ? (
            <Link href="/documents">
              <Button size="lg">进入文档库</Button>
            </Link>
          ) : (
            <>
              <Link href="/auth/register">
                <Button size="lg">立即开始</Button>
              </Link>
              <Link href="/auth/login">
                <Button variant="outline" size="lg">
                  登录
                </Button>
              </Link>
            </>
          )}
        </div>
      </div>
    </div>
  )
}
