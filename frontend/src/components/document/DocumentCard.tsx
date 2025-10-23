
import Link from 'next/link'
import { formatFileSize, formatRelativeTime } from '@/lib/utils'
import type { Document } from '@/types/api'
import ProcessingStatusBadge from './ProcessingStatusBadge'
import { Button } from '../ui/Button'

interface DocumentCardProps {
  document: Document
  onDelete?: (id: string) => void
}

export default function DocumentCard({
  document,
  onDelete,
}: DocumentCardProps) {
  const fileTypeIcons: Record<string, string> = {
    pdf: '📕',
    epub: '📘',
    docx: '📄',
    txt: '📝',
    md: '📋',
  }

  const icon = fileTypeIcons[document.file_type] || '📄'

  return (
    <div className="group relative bg-white rounded-lg border border-gray-200 hover:border-blue-300 hover:shadow-md transition-all p-4">
      {/* 文档图标和标题 */}
      <Link href={`/documents/${document.id}`}>
        <div className="flex items-start gap-3 mb-3">
          <div className="text-4xl flex-shrink-0">{icon}</div>
          <div className="flex-1 min-w-0">
            <h3 className="text-base font-semibold text-gray-900 truncate group-hover:text-blue-600 transition-colors">
              {document.title}
            </h3>
            <p className="text-sm text-gray-500 mt-1">
              {formatFileSize(document.file_size)} · {document.file_type.toUpperCase()}
            </p>
          </div>
        </div>
      </Link>

      {/* 状态和元数据 */}
      <div className="space-y-2 mb-3">
        <ProcessingStatusBadge status={document.processing_status} />

        {document.processing_status === 'completed' && (
          <div className="flex items-center gap-4 text-sm text-gray-600">
            {document.page_count && (
              <span>📖 {document.page_count} 页</span>
            )}
            {document.word_count && (
              <span>📊 {document.word_count.toLocaleString()} 字</span>
            )}
          </div>
        )}

        {document.processing_error && (
          <p className="text-xs text-red-600 bg-red-50 p-2 rounded">
            {document.processing_error}
          </p>
        )}
      </div>

      {/* 时间和操作 */}
      <div className="flex items-center justify-between pt-3 border-t border-gray-100">
        <span className="text-xs text-gray-500">
          {formatRelativeTime(document.created_at)}
        </span>

        {onDelete && (
          <Button
            variant="ghost"
            size="sm"
            onClick={(e) => {
              e.preventDefault()
              if (window.confirm('确定要删除这个文档吗？')) {
                onDelete(document.id)
              }
            }}
            className="text-red-600 hover:text-red-700 hover:bg-red-50"
          >
            删除
          </Button>
        )}
      </div>
    </div>
  )
}
