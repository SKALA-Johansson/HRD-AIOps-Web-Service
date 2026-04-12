<template>
  <header class="app-header">
    <div class="header-inner">
      <router-link :to="homeLink" class="logo">
        <img src="@/assets/images/logo/main_logo.png" alt="" class="logo-img" />
        <span class="logo-text">Smart HRD AIOps</span>
      </router-link>

      <nav v-if="auth.isAuthenticated" class="nav-links">
        <template v-if="auth.role === 'EMPLOYEE'">
          <router-link to="/learning" class="nav-link" active-class="active">학습</router-link>
          <router-link to="/learning/progress" class="nav-link" active-class="active">진도</router-link>
        </template>
        <template v-else-if="auth.role === 'HR'">
          <router-link to="/hr/dashboard" class="nav-link" active-class="active">대시보드</router-link>
          <router-link to="/hr/curriculums" class="nav-link" active-class="active">커리큘럼</router-link>
          <router-link to="/hr/contents" class="nav-link" active-class="active">콘텐츠</router-link>
          <router-link to="/hr/team-progress" class="nav-link" active-class="active">팀 진도</router-link>
          <router-link to="/hr/reports" class="nav-link" active-class="active">리포트</router-link>
        </template>
      </nav>

      <div class="header-actions">
        <ThemeToggle />
        <template v-if="auth.isAuthenticated">
          <span class="user-name" :title="auth.user?.name">{{ auth.user?.name || '사용자' }}</span>
          <span class="badge badge-blue role-badge">{{ roleLabel }}</span>
          <button type="button" class="btn btn-ghost btn-sm" @click="onLogout">로그아웃</button>
        </template>
        <template v-else>
          <router-link to="/login" class="btn btn-ghost btn-sm">로그인</router-link>
          <router-link to="/signup" class="btn btn-primary btn-sm">회원가입</router-link>
        </template>
      </div>
    </div>
  </header>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth.js'
import ThemeToggle from '@/components/ThemeToggle.vue'

const auth = useAuthStore()
const router = useRouter()

const roleLabel = computed(() => {
  const m = { EMPLOYEE: '신입', HR: 'HR' }
  return m[auth.role] || auth.role || ''
})

const homeLink = computed(() => {
  if (!auth.isAuthenticated) return '/'
  if (auth.role === 'HR') return '/hr/dashboard'
  if (auth.role === 'EMPLOYEE') return '/learning'
  return '/'
})

function onLogout() {
  auth.logout(false)
  router.push('/')
}
</script>

<style scoped>
.app-header {
  position: sticky;
  top: 0;
  z-index: 100;
  background: var(--color-header-bg);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--color-border);
  transition: var(--transition);
}
.header-inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
  height: 64px;
  display: flex;
  align-items: center;
  gap: 24px;
}
.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}
.logo-img {
  width: 36px;
  height: 36px;
  object-fit: contain;
  border-radius: 8px;
}
.logo-text {
  font-size: 17px;
  font-weight: 700;
  color: var(--color-text-primary);
  letter-spacing: -0.3px;
}
.nav-links {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  flex: 1;
}
.nav-link {
  padding: 6px 12px;
  border-radius: var(--radius-md);
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text-secondary);
  transition: var(--transition);
}
.nav-link:hover,
.nav-link.active {
  color: var(--color-primary);
  background: var(--color-primary-light);
}
.header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-left: auto;
}
.btn-sm {
  padding: 7px 14px;
  font-size: 13px;
}
.user-name {
  font-size: 13px;
  color: var(--color-text-secondary);
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.role-badge {
  font-size: 11px;
}
</style>
