import axios from 'axios'

import { apiClient } from '@/api/client'
import type { CurrentUser } from '@/types/auth'

type LoginResponse = {
  access: string
  refresh: string
}

export async function login(email: string, password: string) {
  const { data } = await axios.post<LoginResponse>(
    `${import.meta.env.VITE_API_URL}/v1/auth/token/`,
    { email, password },
  )
  return data
}

export async function fetchMe(access: string) {
  const { data } = await axios.get<CurrentUser>(
    `${import.meta.env.VITE_API_URL}/v1/auth/me/`,
    { headers: { Authorization: `Bearer ${access}` } },
  )
  return data
}

export async function fetchMeAuthenticated() {
  const { data } = await apiClient.get<CurrentUser>('/v1/auth/me/')
  return data
}
