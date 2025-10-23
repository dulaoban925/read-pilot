
'use client'

import { use } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { useDocument } from '@/lib/hooks/useDocuments'
import { useSummary } from '@/lib/hooks/useSummary'
import { useGenerateSummary } from '@/lib/hooks/useGenerateSummary'
import { useAuthStore } from '@/stores/authStore'
import { formatFileSize, formatDate } from '@/lib/utils'
import ProcessingStatusBadge from '@/components/document/ProcessingStatusBadge'
import { Button } from '@/components/ui/Button'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import SummaryDisplay from '@/components/document/SummaryDisplay'
import SummaryControls from '@/components/document/SummaryControls'
import LoadingSummary from '@/components/document/LoadingSummary'

interface PageProps {
  params: Promise<{ id: string }>
}

export default function DocumentDetailPage({ params }: PageProps) {
  const { id } = use(params)
  const router = useRouter()
  const { isAuthenticated } = useAuthStore()
  const { data: document, isLoading, error } = useDocument(id)

  // 摘要相关状态
  const { summary, isLoading: isSummaryLoading, refetch: refetchSummary } = useSummary({
    documentId: id,
    enabled: !!document && document.processing_status === 'completed',
  })
  const { generateSummary, isGenerating, isError: isGenerateError, error: generateError } = useGenerateSummary()

  // 生成摘要处理
  const handleGenerateSummary = async (depth: 'brief' | 'detailed') => {
    const result = await generateSummary({ documentId: id, depth })
    if (result) {
      // 等待几秒后重新获取摘要
      setTimeout(() => {
        refetchSummary()
      }, 3000)
    }
  }

  // 检查认证
  if (typeof window !== 'undefined' && !isAuthenticated) {
    router.push('/auth/login')
    return null
  }

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="flex items-center justify-center py-12">
          <div className="text-center">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <p className="mt-4 text-sm text-gray-600">加载中...</p>
          </div>
        </div>
      </div>
    )
  }

  if (error || !document) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
          <p className="text-red-600">文档不存在或加载失败</p>
          <Link href="/documents" className="mt-4 inline-block">
            <Button variant="outline">返回文档库</Button>
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      {/* 面包屑导航 */}
      <nav className="mb-6">
        <Link
          href="/documents"
          className="text-sm text-blue-600 hover:text-blue-700"
        >
          ← 返回文档库
        </Link>
      </nav>

      {/* 文档信息卡片 */}
      <Card className="mb-6">
        <CardHeader>
          <div className="flex items-start justify-between">
            <div>
              <CardTitle className="text-2xl">{document.title}</CardTitle>
              <div className="mt-2 flex items-center gap-3">
                <ProcessingStatusBadge status={document.processing_status} />
                <span className="text-sm text-gray-500">
                  上传于 {formatDate(document.created_at)}
                </span>
              </div>
            </div>
          </div>
        </CardHeader>

        <CardContent>
          {/* 文档元数据 */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div>
              <p className="text-sm text-gray-500 mb-1">文件类型</p>
              <p className="font-medium text-gray-900">
                {document.file_type.toUpperCase()}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-500 mb-1">文件大小</p>
              <p className="font-medium text-gray-900">
                {formatFileSize(document.file_size)}
              </p>
            </div>
            {document.page_count && (
              <div>
                <p className="text-sm text-gray-500 mb-1">页数</p>
                <p className="font-medium text-gray-900">
                  {document.page_count} 页
                </p>
              </div>
            )}
            {document.word_count && (
              <div>
                <p className="text-sm text-gray-500 mb-1">字数</p>
                <p className="font-medium text-gray-900">
                  {document.word_count.toLocaleString()} 字
                </p>
              </div>
            )}
          </div>

          {/* 作者信息 */}
          {document.author && (
            <div className="mb-6">
              <p className="text-sm text-gray-500 mb-1">作者</p>
              <p className="font-medium text-gray-900">{document.author}</p>
            </div>
          )}

          {/* 处理错误信息 */}
          {document.processing_error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
              <p className="text-sm font-medium text-red-900 mb-1">
                处理失败
              </p>
              <p className="text-sm text-red-600">
                {document.processing_error}
              </p>
            </div>
          )}

          {/* 操作按钮 */}
          <div className="flex gap-3">
            {document.processing_status === 'completed' && (
              <>
                <Button>开始阅读</Button>
                <Button variant="outline">生成摘要</Button>
                <Button variant="outline">问答对话</Button>
              </>
            )}
            {document.processing_status === 'processing' && (
              <div className="text-sm text-gray-600">
                文档正在处理中，请稍候...
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* 索引状态 */}
      {document.is_indexed && (
        <Card className="mb-6">
          <CardContent className="py-4">
            <div className="flex items-center gap-2 text-sm text-green-700">
              <span>✅</span>
              <span>文档已完成向量化索引，可进行语义搜索和AI问答</span>
            </div>
          </CardContent>
        </Card>
      )}

      {/* 摘要区域 */}
      {document.processing_status === 'completed' && (
        <div className="mb-6">
          {/* 摘要控制 */}
          <div className="mb-4">
            <SummaryControls
              isGenerating={isGenerating}
              hasSummary={!!summary}
              currentDepth={summary?.depth_level}
              onGenerate={handleGenerateSummary}
              onRegenerate={handleGenerateSummary}
            />
          </div>

          {/* 错误提示 */}
          {isGenerateError && generateError && (
            <div className="mb-4 bg-red-50 border border-red-200 rounded-lg p-4">
              <p className="text-sm text-red-600">{generateError.message}</p>
            </div>
          )}

          {/* 摘要内容 */}
          {isGenerating || isSummaryLoading ? (
            <LoadingSummary />
          ) : summary ? (
            <SummaryDisplay summary={summary} />
          ) : null}
        </div>
      )}
    </div>
  )
}
