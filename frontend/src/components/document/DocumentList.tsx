
'use client'

import { useDocuments, useDeleteDocument } from '@/lib/hooks/useDocuments'
import { useDocumentStore } from '@/stores/documentStore'
import DocumentCard from './DocumentCard'
import { Button } from '../ui/Button'

interface DocumentListProps {
  page?: number
  pageSize?: number
}

export default function DocumentList({
  page = 1,
  pageSize = 20,
}: DocumentListProps) {
  const { data, isLoading, error } = useDocuments(page, pageSize)
  const deleteMutation = useDeleteDocument()
  const { removeDocument } = useDocumentStore()

  const handleDelete = async (documentId: string) => {
    try {
      await deleteMutation.mutateAsync(documentId)
      removeDocument(documentId)
    } catch (error) {
      console.error('删除失败:', error)
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p className="mt-4 text-sm text-gray-600">加载中...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
        <p className="text-red-600">加载失败，请刷新重试</p>
      </div>
    )
  }

  if (!data || data.items.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="text-6xl mb-4">📚</div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">
          还没有文档
        </h3>
        <p className="text-gray-500">上传您的第一个文档开始智能阅读</p>
      </div>
    )
  }

  return (
    <div>
      {/* 文档网格 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {data.items.map((document) => (
          <DocumentCard
            key={document.id}
            document={document}
            onDelete={handleDelete}
          />
        ))}
      </div>

      {/* 分页 */}
      {data.total_pages > 1 && (
        <div className="flex items-center justify-center gap-2 mt-8">
          <Button
            variant="outline"
            size="sm"
            disabled={page === 1}
            onClick={() => {
              // 这里需要通过路由或状态管理来改变页码
              window.location.href = `?page=${page - 1}`
            }}
          >
            上一页
          </Button>
          <span className="text-sm text-gray-600">
            第 {page} / {data.total_pages} 页
          </span>
          <Button
            variant="outline"
            size="sm"
            disabled={page >= data.total_pages}
            onClick={() => {
              window.location.href = `?page=${page + 1}`
            }}
          >
            下一页
          </Button>
        </div>
      )}

      {/* 总数统计 */}
      <p className="text-center text-sm text-gray-500 mt-4">
        共 {data.total} 个文档
      </p>
    </div>
  )
}
