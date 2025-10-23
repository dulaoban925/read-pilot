
'use client'

import { useState, useRef } from 'react'
import { useUploadDocument } from '@/lib/hooks/useDocuments'
import { useDocumentStore } from '@/stores/documentStore'
import { Button } from '../ui/Button'

const ALLOWED_TYPES = [
  'application/pdf',
  'application/epub+zip',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'text/plain',
  'text/markdown',
]

const MAX_FILE_SIZE = 50 * 1024 * 1024 // 50MB

interface DocumentUploaderProps {
  onUploadSuccess?: () => void
}

export default function DocumentUploader({
  onUploadSuccess,
}: DocumentUploaderProps) {
  const [isDragging, setIsDragging] = useState(false)
  const [error, setError] = useState<string>('')
  const fileInputRef = useRef<HTMLInputElement>(null)

  const uploadMutation = useUploadDocument()
  const { addDocument } = useDocumentStore()

  const validateFile = (file: File): string | null => {
    // 检查文件类型
    const fileExt = file.name.split('.').pop()?.toLowerCase()
    const allowedExts = ['pdf', 'epub', 'docx', 'txt', 'md']

    if (!fileExt || !allowedExts.includes(fileExt)) {
      return '不支持的文件类型。支持: PDF, EPUB, DOCX, TXT, Markdown'
    }

    // 检查文件大小
    if (file.size > MAX_FILE_SIZE) {
      return `文件大小超过限制 (最大 50MB)`
    }

    return null
  }

  const handleFile = async (file: File) => {
    setError('')

    // 验证文件
    const validationError = validateFile(file)
    if (validationError) {
      setError(validationError)
      return
    }

    try {
      // mutateAsync 返回的 result 直接是 Document 对象
      const document = await uploadMutation.mutateAsync({
        file,
        title: file.name.replace(/\.[^/.]+$/, ''), // 移除扩展名
      })

      addDocument(document)
      onUploadSuccess?.()
    } catch (err: any) {
      // 使用统一的错误格式
      setError(err.message || err.detail || '上传失败，请重试')
    }
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)

    const files = Array.from(e.dataTransfer.files)
    if (files.length > 0) {
      await handleFile(files[0])
    }
  }

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (files && files.length > 0) {
      await handleFile(files[0])
    }
    // 重置input
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const handleClick = () => {
    fileInputRef.current?.click()
  }

  return (
    <div className="w-full">
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={handleClick}
        className={`
          relative border-2 border-dashed rounded-lg p-8
          transition-all cursor-pointer
          ${
            isDragging
              ? 'border-blue-500 bg-blue-50'
              : 'border-gray-300 hover:border-blue-400 hover:bg-gray-50'
          }
          ${uploadMutation.isPending ? 'opacity-50 pointer-events-none' : ''}
        `}
      >
        <input
          ref={fileInputRef}
          type="file"
          className="hidden"
          accept=".pdf,.epub,.docx,.txt,.md"
          onChange={handleFileSelect}
          disabled={uploadMutation.isPending}
        />

        <div className="text-center">
          {uploadMutation.isPending ? (
            <>
              <div className="text-4xl mb-4">⏳</div>
              <p className="text-lg font-medium text-gray-900 mb-2">
                正在上传...
              </p>
              <p className="text-sm text-gray-500">
                文档上传后将自动开始处理
              </p>
            </>
          ) : (
            <>
              <div className="text-4xl mb-4">📤</div>
              <p className="text-lg font-medium text-gray-900 mb-2">
                {isDragging ? '释放以上传' : '拖拽文件到这里或点击上传'}
              </p>
              <p className="text-sm text-gray-500 mb-4">
                支持 PDF, EPUB, DOCX, TXT, Markdown (最大 50MB)
              </p>
              <Button variant="outline" size="sm" onClick={(e) => e.stopPropagation()}>
                选择文件
              </Button>
            </>
          )}
        </div>
      </div>

      {error && (
        <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-md">
          <p className="text-sm text-red-600">{error}</p>
        </div>
      )}
    </div>
  )
}
