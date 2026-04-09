import { defineStore } from 'pinia'
import { ref } from 'vue'

const STORAGE_KEY = 'shrd_theme'

function readStoredOrSystem() {
  try {
    const s = localStorage.getItem(STORAGE_KEY)
    if (s === 'light' || s === 'dark') return s
  } catch {
    /* ignore */
  }
  if (typeof window !== 'undefined' && window.matchMedia('(prefers-color-scheme: dark)').matches) {
    return 'dark'
  }
  return 'light'
}

export const useThemeStore = defineStore('theme', () => {
  const mode = ref('light')

  function apply() {
    if (typeof document === 'undefined') return
    document.documentElement.setAttribute('data-theme', mode.value)
    try {
      localStorage.setItem(STORAGE_KEY, mode.value)
    } catch {
      /* ignore */
    }
  }

  function init() {
    mode.value = readStoredOrSystem()
    apply()
  }

  function setMode(m) {
    if (m !== 'light' && m !== 'dark') return
    mode.value = m
    apply()
  }

  function toggle() {
    setMode(mode.value === 'dark' ? 'light' : 'dark')
  }

  return { mode, init, setMode, toggle }
})
