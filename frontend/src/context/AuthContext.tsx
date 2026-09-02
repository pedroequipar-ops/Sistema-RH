import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from 'react'

import { fetchMe, login as loginRequest } from '@/api/auth'
import { getAuthSession, setAuthSession } from '@/lib/session'
import type { CurrentUser } from '@/types/auth'

type AuthContextValue = {
  user: CurrentUser | null
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  hasPermission: (functionSlug: string, action: 'view' | 'create' | 'edit' | 'delete') => boolean
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<CurrentUser | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const session = getAuthSession()
    if (!session) {
      setIsLoading(false)
      return
    }
    fetchMe(session.access)
      .then(setUser)
      .catch(() => setAuthSession(null))
      .finally(() => setIsLoading(false))
  }, [])

  const login = useCallback(async (email: string, password: string) => {
    const tokens = await loginRequest(email, password)
    const me = await fetchMe(tokens.access)
    setAuthSession({ access: tokens.access, refresh: tokens.refresh, companyId: me.company_id })
    setUser(me)
  }, [])

  const logout = useCallback(() => {
    setAuthSession(null)
    setUser(null)
  }, [])

  const hasPermission = useCallback(
    (functionSlug: string, action: 'view' | 'create' | 'edit' | 'delete') => {
      if (!user) return false
      if (user.is_superuser) return true
      const grant = user.function_permissions.find((p) => p.function === functionSlug)
      if (!grant) return false
      return grant[`can_${action}`]
    },
    [user],
  )

  return (
    <AuthContext.Provider value={{ user, isLoading, login, logout, hasPermission }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) throw new Error('useAuth precisa estar dentro de um AuthProvider.')
  return context
}
