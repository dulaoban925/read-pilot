
import type { DocumentStatus } from '@/types/document'

interface ProcessingStatusBadgeProps {
  status: DocumentStatus
  className?: string
}

export default function ProcessingStatusBadge({
  status,
  className = '',
}: ProcessingStatusBadgeProps) {
  const statusConfig = {
    pending: {
      label: '待处理',
      color: 'bg-gray-100 text-gray-700 border-gray-300',
      icon: '⏳',
    },
    processing: {
      label: '处理中',
      color: 'bg-blue-100 text-blue-700 border-blue-300',
      icon: '⚙️',
    },
    completed: {
      label: '已完成',
      color: 'bg-green-100 text-green-700 border-green-300',
      icon: '✅',
    },
    failed: {
      label: '失败',
      color: 'bg-red-100 text-red-700 border-red-300',
      icon: '❌',
    },
  }

  const config = statusConfig[status]

  return (
    <span
      className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium border ${config.color} ${className}`}
    >
      <span>{config.icon}</span>
      <span>{config.label}</span>
    </span>
  )
}
