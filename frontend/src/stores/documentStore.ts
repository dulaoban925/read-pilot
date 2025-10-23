
import { create } from 'zustand'
import type { Document } from '@/types/api'

interface DocumentState {
  // 状态
  documents: Document[]
  currentDocument: Document | null
  isLoading: boolean
  uploadProgress: number

  // 操作
  setDocuments: (documents: Document[]) => void
  addDocument: (document: Document) => void
  updateDocument: (documentId: string, updates: Partial<Document>) => void
  removeDocument: (documentId: string) => void
  setCurrentDocument: (document: Document | null) => void
  setLoading: (loading: boolean) => void
  setUploadProgress: (progress: number) => void
  clearDocuments: () => void
}

export const useDocumentStore = create<DocumentState>((set) => ({
  // 初始状态
  documents: [],
  currentDocument: null,
  isLoading: false,
  uploadProgress: 0,

  // 设置文档列表
  setDocuments: (documents: Document[]) => {
    set({ documents })
  },

  // 添加文档
  addDocument: (document: Document) => {
    set((state) => ({
      documents: [document, ...state.documents],
    }))
  },

  // 更新文档
  updateDocument: (documentId: string, updates: Partial<Document>) => {
    set((state) => ({
      documents: state.documents.map((doc) =>
        doc.id === documentId ? { ...doc, ...updates } : doc
      ),
      currentDocument:
        state.currentDocument?.id === documentId
          ? { ...state.currentDocument, ...updates }
          : state.currentDocument,
    }))
  },

  // 移除文档
  removeDocument: (documentId: string) => {
    set((state) => ({
      documents: state.documents.filter((doc) => doc.id !== documentId),
      currentDocument:
        state.currentDocument?.id === documentId
          ? null
          : state.currentDocument,
    }))
  },

  // 设置当前文档
  setCurrentDocument: (document: Document | null) => {
    set({ currentDocument: document })
  },

  // 设置加载状态
  setLoading: (loading: boolean) => {
    set({ isLoading: loading })
  },

  // 设置上传进度
  setUploadProgress: (progress: number) => {
    set({ uploadProgress: progress })
  },

  // 清空文档
  clearDocuments: () => {
    set({
      documents: [],
      currentDocument: null,
      uploadProgress: 0,
    })
  },
}))
