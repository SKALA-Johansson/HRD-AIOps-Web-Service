import axios from 'axios'
import { useAuthStore } from '@/store/auth.js'

/** Spring Cloud Gateway 기준: /api/v1 */
export const api = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' }
})

function readClaimFromJwt(token, claimKey) {
  try {
    const payload = token?.split('.')?.[1]
    if (!payload) return null
    const base64 = payload.replace(/-/g, '+').replace(/_/g, '/')
    const raw = window.atob(base64)
    const bytes = Uint8Array.from(raw, (c) => c.charCodeAt(0))
    const decoded = JSON.parse(new TextDecoder().decode(bytes))
    return decoded?.[claimKey] ?? null
  } catch {
    return null
  }
}

api.interceptors.request.use((config) => {
  const auth = useAuthStore()
  if (auth.accessToken) {
    config.headers.Authorization = `Bearer ${auth.accessToken}`
    const employeeId = readClaimFromJwt(auth.accessToken, 'username')
    if (employeeId) {
      config.headers['X-Employee-Id'] = employeeId
    }
  }
  if (config.data instanceof FormData) {
    delete config.headers['Content-Type']
  }
  return config
})

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      const auth = useAuthStore()
      auth.logout(false)
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

export default api
