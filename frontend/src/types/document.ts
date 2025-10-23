

export type DocumentStatus = 'pending' | 'processing' | 'completed' | 'failed'

export type FileType = 'pdf' | 'epub' | 'docx' | 'txt' | 'md'

export interface DocumentMetadata {
  author?: string
  page_count?: number
  word_count?: number
  file_size: number
  file_type: FileType
}

export interface UploadProgress {
  documentId: string
  progress: number
  status: 'uploading' | 'processing' | 'completed' | 'error'
  error?: string
}
