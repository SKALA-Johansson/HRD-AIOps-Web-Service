<template>
  <button
    type="button"
    class="theme-toggle btn btn-ghost btn-sm"
    :aria-pressed="theme.mode === 'dark'"
    :aria-label="theme.mode === 'dark' ? '라이트 모드로 전환' : '다크 모드로 전환'"
    :title="theme.mode === 'dark' ? '라이트 모드' : '다크 모드'"
    @click="theme.toggle()"
  >
    <span class="icon" aria-hidden="true">{{ theme.mode === 'dark' ? '☀' : '☽' }}</span>
  </button>
</template>

<script setup>
import { useThemeStore } from '@/store/theme.js'

const theme = useThemeStore()
</script>

<style scoped>
.theme-toggle {
  min-width: 40px;
  padding: 7px 10px;
  font-size: 16px;
  line-height: 1;
}
.icon {
  display: block;
  opacity: 0.9;
}
</style>
