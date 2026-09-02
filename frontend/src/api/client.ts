import axios from 'axios'

import { getAuthSession, setAuthSession } from '@/lib/session'

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
})

apiClient.interceptors.request.use((config) => {
  const session = getAuthSession()
  if (session?.access) {
    config.headers.Authorization = `Bearer ${session.access}`
  }
  if (session?.companyId) {
    config.headers['X-Company-ID'] = session.companyId
  }
  return config
})

let refreshPromise: Promise<string> | null = null

async function refreshAccessToken(refresh: string) {
  const { data } = await axios.post(`${import.meta.env.VITE_API_URL}/v1/auth/token/refresh/`, {
    refresh,
  })
  return data.access as string
}

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config
    const session = getAuthSession()

    if (error.response?.status === 401 && session?.refresh && !original._retry) {
      original._retry = true
      try {
        refreshPromise ??= refreshAccessToken(session.refresh)
        const access = await refreshPromise
        refreshPromise = null
        setAuthSession({ ...session, access })
        original.headers.Authorization = `Bearer ${access}`
        return apiClient(original)
      } catch {
        refreshPromise = null
        setAuthSession(null)
        window.location.assign('/login')
      }
    }

    return Promise.reject(error)
  },
)
