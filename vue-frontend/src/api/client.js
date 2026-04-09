import axios from 'axios'
import { useAuthStore, DEV_PREVIEW_TOKEN } from '@/store/auth.js'

/** Spring Cloud Gateway 기준: /api/v1 */
export const api = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' }
})

api.interceptors.request.use((config) => {
  const auth = useAuthStore()
  if (auth.accessToken) {
    config.headers.Authorization = `Bearer ${auth.accessToken}`
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
      /** 개발 미리보기 중에는 API 실패만 표시하고 로그인으로 보내지 않음 */
      if (auth.accessToken === DEV_PREVIEW_TOKEN && import.meta.env.DEV) {
        return Promise.reject(err)
      }
      auth.logout(false)
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

export default api
