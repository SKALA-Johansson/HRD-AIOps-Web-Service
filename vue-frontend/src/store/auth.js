import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/auth.js'

const STORAGE_ACCESS = 'shrd_access_token'
const STORAGE_REFRESH = 'shrd_refresh_token'
const STORAGE_USER = 'shrd_user'

/** 개발 서버에서만 사용 — 운영 빌드에서는 무시됨 */
export const DEV_PREVIEW_TOKEN = '__DEV_PREVIEW__'

function readTokenSafe() {
  const t = sessionStorage.getItem(STORAGE_ACCESS)
  if (!import.meta.env.DEV && t === DEV_PREVIEW_TOKEN) {
    sessionStorage.removeItem(STORAGE_ACCESS)
    sessionStorage.removeItem(STORAGE_REFRESH)
    sessionStorage.removeItem(STORAGE_USER)
    return null
  }
  return t
}

export const useAuthStore = defineStore('auth', () => {
  const accessToken = ref(readTokenSafe() || null)
  const refreshToken = ref(sessionStorage.getItem(STORAGE_REFRESH) || null)
  const user = ref(JSON.parse(sessionStorage.getItem(STORAGE_USER) || 'null'))

  const isAuthenticated = computed(() => !!accessToken.value)
  const isDevPreview = computed(
    () => import.meta.env.DEV && accessToken.value === DEV_PREVIEW_TOKEN
  )
  const role = computed(() => user.value?.role ?? null)
  const isEmployee = computed(() => role.value === 'EMPLOYEE')
  const isHr = computed(() => role.value === 'HR')

  function persist() {
    if (accessToken.value) sessionStorage.setItem(STORAGE_ACCESS, accessToken.value)
    else sessionStorage.removeItem(STORAGE_ACCESS)
    if (refreshToken.value) sessionStorage.setItem(STORAGE_REFRESH, refreshToken.value)
    else sessionStorage.removeItem(STORAGE_REFRESH)
    if (user.value) sessionStorage.setItem(STORAGE_USER, JSON.stringify(user.value))
    else sessionStorage.removeItem(STORAGE_USER)
  }

  /**
   * DB·백엔드 없이 UI만 볼 때 (npm run dev 전용)
   * @param {'EMPLOYEE' | 'HR'} previewRole
   */
  function startDevPreview(previewRole) {
    if (!import.meta.env.DEV) return
    const mockNames = {
      EMPLOYEE: '개발 미리보기(신입)',
      HR: '개발 미리보기(HR)'
    }
    accessToken.value = DEV_PREVIEW_TOKEN
    refreshToken.value = null
    user.value = {
      userId: previewRole === 'EMPLOYEE' ? 1 : 900,
      name: mockNames[previewRole] || '개발 미리보기',
      role: previewRole
    }
    persist()
  }

  function endDevPreview() {
    accessToken.value = null
    refreshToken.value = null
    user.value = null
    persist()
  }

  async function login(email, password) {
    const res = await authApi.login({ email, password })
    const payload = res.data?.data
    if (!payload?.accessToken) {
      throw new Error(res.data?.message || '로그인 응답이 올바르지 않습니다.')
    }
    accessToken.value = payload.accessToken
    refreshToken.value = payload.refreshToken ?? null
    user.value = payload.user ?? null
    persist()
  }

  async function signup(body) {
    return authApi.signup(body)
  }

  function logout(redirect = true) {
    accessToken.value = null
    refreshToken.value = null
    user.value = null
    persist()
    if (redirect) {
      window.location.href = '/login'
    }
  }

  function afterProfileRefresh(profileUser) {
    if (profileUser && user.value) {
      user.value = { ...user.value, ...profileUser }
      persist()
    }
  }

  return {
    accessToken,
    refreshToken,
    user,
    isAuthenticated,
    isDevPreview,
    role,
    isEmployee,
    isHr,
    login,
    signup,
    logout,
    startDevPreview,
    endDevPreview,
    afterProfileRefresh,
    persist
  }
})
