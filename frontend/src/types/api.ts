

// 通用响应类型 - 统一服务端响应结构
export interface ApiResponse<T = any> {
  code: number // 0表示成功，非0表示错误
  message: string // 响应消息
  data: T | null // 响应数据
}

// 分页数据结构
export interface PaginationData<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

// 分页响应
export type PaginatedResponse<T> = ApiResponse<PaginationData<T>>

// 错误响应（兼容旧的错误处理）
export interface ErrorResponse {
  detail: string
  message?: string
}

// 用户类型
export interface User {
  id: string
  email: string
  username: string
  is_active: boolean
  is_verified: boolean
  preferences: Record<string, any>
  total_reading_time: number
  documents_read: number
  questions_asked: number
  notes_created: number
  created_at: string
  updated_at: string
}

// 认证请求/响应
export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  email: string
  username: string
  password: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
  expires_in: number
}

// 文档类型
export interface Document {
  id: string
  user_id: string
  title: string
  file_path: string
  file_hash: string
  file_size: number
  file_type: string
  author?: string
  page_count?: number
  word_count?: number
  processing_status: 'pending' | 'processing' | 'completed' | 'failed'
  processing_error?: string
  is_indexed: boolean
  created_at: string
  updated_at: string
}

// 文档上传响应 - data 字段直接是 Document 对象
// 已废弃：直接使用 Document 类型，message 在 ApiResponse.message 中
export type DocumentUploadResponse = Document

// 聊天会话
export interface ChatSession {
  id: string
  user_id: string
  document_id: string
  title: string
  message_count: number
  last_message_at?: string
  created_at: string
  updated_at: string
}

// 聊天消息
export interface Message {
  id: string
  session_id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  token_count?: number
  model?: string
  sources?: Array<{
    chunk_id: string
    text: string
    page?: number
    relevance: number
  }>
  confidence?: number
  response_metadata?: Record<string, any>
  feedback?: 'helpful' | 'not_helpful' | 'incorrect'
  created_at: string
}

// 摘要
export interface Summary {
  id: string
  document_id: string
  summary_type: 'full' | 'chapter' | 'section' | 'custom'
  content: {
    topic?: string
    core_points?: string[]
    conclusions?: string[]
    highlights?: string[]
  }
  text: string
  ai_metadata?: Record<string, any>
  target_section?: string
  guiding_questions?: string[]
  created_at: string
  updated_at: string
}
