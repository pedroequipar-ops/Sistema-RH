import type { ReactNode } from 'react'
import { Navigate } from 'react-router-dom'

import { useAuth } from '@/context/AuthContext'
import type { Role } from '@/types/auth'

export function RequireRole({
  roles,
  redirectTo,
  children,
}: {
  roles: Role[]
  redirectTo: string
  children: ReactNode
}) {
  const { user } = useAuth()

  if (!user || !roles.includes(user.role)) {
    return <Navigate to={redirectTo} replace />
  }

  return children
}
