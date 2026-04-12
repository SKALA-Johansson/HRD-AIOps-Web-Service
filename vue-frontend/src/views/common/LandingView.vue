<template>
  <div class="landing">
    <AppHeader />
    <section class="hero">
      <div class="hero-inner">
        <div class="hero-content fade-in-up">
          <span class="hero-badge">Agentic AI · MSA · RAG</span>
          <h1 class="hero-title">
            신입 맞춤 교육과<br />
            성장 인사이트를 한곳에서
          </h1>
          <div class="hero-actions">
            <template v-if="auth.isAuthenticated">
              <router-link :to="homeLink" class="btn btn-primary btn-lg">홈으로 이동</router-link>
            </template>
            <template v-else>
              <router-link to="/signup" class="btn btn-primary btn-lg">시작하기</router-link>
              <router-link to="/login" class="btn btn-outline btn-lg">로그인</router-link>
            </template>
          </div>
        </div>
        <div class="hero-visual fade-in">
          <img src="@/assets/images/logo/main_logo.png" alt="" class="hero-logo" />
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useAuthStore } from '@/store/auth.js'
import AppHeader from '@/components/AppHeader.vue'

const auth = useAuthStore()

const homeLink = computed(() => {
  if (auth.role === 'HR') return '/hr/dashboard'
  if (auth.role === 'EMPLOYEE') return '/learning'
  return '/'
})
</script>

<style scoped>
.landing {
  min-height: 100vh;
  background: var(--color-bg-secondary);
}
.hero {
  padding: 80px 24px 100px;
}
.hero-inner {
  max-width: 1100px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 48px;
  align-items: center;
}
@media (max-width: 900px) {
  .hero-inner {
    grid-template-columns: 1fr;
  }
}
.hero-badge {
  display: inline-block;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  background: var(--color-primary-light);
  color: var(--color-primary);
  margin-bottom: 16px;
}
.hero-title {
  font-size: clamp(1.75rem, 4vw, 2.25rem);
  font-weight: 700;
  line-height: 1.25;
  margin-bottom: 28px;
  letter-spacing: -0.5px;
}
.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}
.btn-lg {
  padding: 12px 24px;
  font-size: 15px;
}
.hero-visual {
  display: flex;
  justify-content: center;
}
.hero-logo {
  width: min(280px, 80vw);
  height: auto;
  opacity: 0.95;
}
</style>
