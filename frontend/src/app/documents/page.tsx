
'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/stores/authStore'
import DocumentUploader from '@/components/document/DocumentUploader'
import DocumentList from '@/components/document/DocumentList'
import { Button } from '@/components/ui/Button'

export default function DocumentsPage() {
  const router = useRouter()
  const { isAuthenticated } = useAuthStore()
  const [showUploader, setShowUploader] = useState(false)

  // 检查认证
  if (typeof window !== 'undefined' && !isAuthenticated) {
    router.push('/auth/login')
    return null
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* 页面标题 */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">我的文档</h1>
          <p className="mt-2 text-gray-600">
            管理您的文档并使用AI增强阅读体验
          </p>
        </div>
        <Button
          onClick={() => setShowUploader(!showUploader)}
          size="lg"
        >
          {showUploader ? '收起上传' : '+ 上传文档'}
        </Button>
      </div>

      {/* 上传区域 */}
      {showUploader && (
        <div className="mb-8">
          <DocumentUploader
            onUploadSuccess={() => {
              setShowUploader(false)
            }}
          />
        </div>
      )}

      {/* 文档列表 */}
      <DocumentList />
    </div>
  )
}
