
'use client'

import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/stores/authStore'
import { logout } from '@/lib/auth'
import { Button } from '@/components/ui/Button'

export default function Header() {
  const router = useRouter()
  const { isAuthenticated, user, clearAuth } = useAuthStore()

  const handleLogout = async () => {
    try {
      await logout()
      clearAuth()
      router.push('/auth/login')
    } catch (error) {
      console.error('Logout failed:', error)
    }
  }

  return (
    <header className="border-b border-gray-200 bg-white">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          {/* Logo */}
          <Link href="/" className="flex items-center space-x-2">
            <span className="text-2xl font-bold text-blue-600">
              ReadPilot
            </span>
          </Link>

          {/* Navigation */}
          {isAuthenticated && (
            <nav className="flex items-center space-x-6">
              <Link
                href="/documents"
                className="text-sm font-medium text-gray-700 hover:text-blue-600 transition-colors"
              >
                我的文档
              </Link>
              <Link
                href="/reading"
                className="text-sm font-medium text-gray-700 hover:text-blue-600 transition-colors"
              >
                阅读中心
              </Link>
            </nav>
          )}

          {/* User Menu */}
          <div className="flex items-center space-x-4">
            {isAuthenticated ? (
              <>
                <span className="text-sm text-gray-700">
                  {user?.username}
                </span>
                <Button variant="outline" size="sm" onClick={handleLogout}>
                  登出
                </Button>
              </>
            ) : (
              <>
                <Link href="/auth/login">
                  <Button variant="ghost" size="sm">
                    登录
                  </Button>
                </Link>
                <Link href="/auth/register">
                  <Button size="sm">注册</Button>
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </header>
  )
}
