import { defineStore } from 'pinia'
import { ref } from 'vue'

/** 우하단 AI 튜터 챗 패널 열림 상태 */
export const useTutorDockStore = defineStore('tutorDock', () => {
  const isOpen = ref(false)

  function open() {
    isOpen.value = true
  }

  function close() {
    isOpen.value = false
  }

  function toggle() {
    isOpen.value = !isOpen.value
  }

  return { isOpen, open, close, toggle }
})
