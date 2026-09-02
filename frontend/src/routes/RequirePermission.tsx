import type { ReactNode } from 'react'
import { Navigate } from 'react-router-dom'

import { useAuth } from '@/context/AuthContext'

type Action = 'view' | 'create' | 'edit' | 'delete'

export function RequirePermission({
  functionSlug,
  action,
  redirectTo,
  children,
}: {
  functionSlug: string
  action: Action
  redirectTo: string
  children: ReactNode
}) {
  const { hasPermission } = useAuth()

  if (!hasPermission(functionSlug, action)) {
    return <Navigate to={redirectTo} replace />
  }

  return children
}
