import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/auth.js'

const STORAGE_ACCESS = 'shrd_access_token'
const STORAGE_REFRESH = 'shrd_refresh_token'
const STORAGE_USER = 'shrd_user'

export const useAuthStore = defineStore('auth', () => {
  const accessToken = ref(sessionStorage.getItem(STORAGE_ACCESS) || null)
  const refreshToken = ref(sessionStorage.getItem(STORAGE_REFRESH) || null)
  const user = ref(JSON.parse(sessionStorage.getItem(STORAGE_USER) || 'null'))

  const isAuthenticated = computed(() => !!accessToken.value)
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

  async function login(username, password) {
    const res = await authApi.login({ username, password })
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
    role,
    isEmployee,
    isHr,
    login,
    signup,
    logout,
    afterProfileRefresh,
    persist
  }
})
