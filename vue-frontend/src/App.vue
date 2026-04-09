<template>
  <router-view />
  <TutorChatDock v-if="showTutorDock" />
</template>

<script setup>
import { computed } from 'vue'
import { useAuthStore } from '@/store/auth.js'
import TutorChatDock from '@/components/TutorChatDock.vue'

const auth = useAuthStore()
const showTutorDock = computed(() => auth.isAuthenticated && auth.role === 'EMPLOYEE')
</script>
