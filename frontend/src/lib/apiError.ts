import { isAxiosError } from 'axios'

export function getApiErrorMessage(error: unknown, fallback = 'Ocorreu um erro inesperado.') {
  if (!isAxiosError(error)) return fallback
  const data = error.response?.data
  if (!data) return fallback
  if (typeof data === 'string') return data
  if (typeof data.detail === 'string') return data.detail
  const firstKey = Object.keys(data)[0]
  if (firstKey) {
    const value = data[firstKey]
    const message = Array.isArray(value) ? value[0] : value
    if (typeof message === 'string') return message
  }
  return fallback
}
