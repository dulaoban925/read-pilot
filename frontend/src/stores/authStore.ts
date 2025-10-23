
import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { User, TokenResponse } from '@/types/api'

interface AuthState {
  // 状态
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean

  // 操作
  setAuth: (token: string, user: User) => void
  clearAuth: () => void
  setUser: (user: User) => void
  setLoading: (loading: boolean) => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      // 初始状态
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,

      // 设置认证信息
      setAuth: (token: string, user: User) => {
        // 保存到localStorage
        if (typeof window !== 'undefined') {
          localStorage.setItem('access_token', token)
          localStorage.setItem('user', JSON.stringify(user))
        }

        set({
          token,
          user,
          isAuthenticated: true,
        })
      },

      // 清除认证信息
      clearAuth: () => {
        // 从localStorage清除
        if (typeof window !== 'undefined') {
          localStorage.removeItem('access_token')
          localStorage.removeItem('user')
        }

        set({
          token: null,
          user: null,
          isAuthenticated: false,
        })
      },

      // 更新用户信息
      setUser: (user: User) => {
        if (typeof window !== 'undefined') {
          localStorage.setItem('user', JSON.stringify(user))
        }

        set({ user })
      },

      // 设置加载状态
      setLoading: (loading: boolean) => {
        set({ isLoading: loading })
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
)
