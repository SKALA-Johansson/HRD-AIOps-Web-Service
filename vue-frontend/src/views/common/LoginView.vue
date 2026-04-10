<template>
  <div class="auth-page">
    <div class="auth-toolbar">
      <ThemeToggle />
    </div>
    <div class="auth-card fade-in-up">
      <router-link to="/" class="back-link">← 홈</router-link>
      <h1 class="title">로그인</h1>
      <p class="desc">이메일과 비밀번호로 로그인합니다. (API: POST <code>/auth/login</code>)</p>

      <form class="form" @submit.prevent="submit">
        <label class="form-label">이메일</label>
        <input v-model="email" type="email" class="form-input" required autocomplete="username" />

        <label class="form-label">비밀번호</label>
        <input
          v-model="password"
          type="password"
          class="form-input"
          required
          autocomplete="current-password"
        />

        <p v-if="error" class="error">{{ error }}</p>

        <button type="submit" class="btn btn-primary btn-full" :disabled="loading">
          {{ loading ? '처리 중…' : '로그인' }}
        </button>
      </form>

      <p class="footer-link">
        계정이 없으신가요?
        <router-link to="/signup">회원가입</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth.js'
import ThemeToggle from '@/components/ThemeToggle.vue'

const email = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()

async function submit() {
  error.value = ''
  loading.value = true
  try {
    await auth.login(email.value, password.value)
    const redir = route.query.redirect
    if (typeof redir === 'string' && redir.startsWith('/')) {
      router.replace(redir)
      return
    }
    if (auth.role === 'HR') router.replace('/hr/dashboard')
    else router.replace('/learning')
  } catch (e) {
    error.value = e.response?.data?.message || e.message || '로그인에 실패했습니다.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  position: relative;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 32px 16px;
  background: linear-gradient(160deg, var(--color-primary-light) 0%, var(--color-bg-secondary) 45%);
  transition: background 0.2s ease;
}
.auth-toolbar {
  position: absolute;
  top: 16px;
  right: 16px;
  z-index: 2;
}
.auth-card {
  width: 100%;
  max-width: 420px;
  background: var(--color-bg-primary);
  border-radius: var(--radius-xl);
  padding: 32px;
  box-shadow: var(--shadow-lg);
  border: 1px solid var(--color-border);
}
.back-link {
  font-size: 13px;
  color: var(--color-text-secondary);
  display: inline-block;
  margin-bottom: 16px;
}
.back-link:hover {
  color: var(--color-primary);
}
.title {
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: 8px;
}
.desc {
  font-size: 14px;
  color: var(--color-text-secondary);
  margin-bottom: 24px;
  line-height: 1.5;
}
.desc code {
  font-size: 12px;
  background: var(--color-bg-tertiary);
  padding: 2px 6px;
  border-radius: 4px;
}
.form-label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  margin-bottom: 6px;
}
.form-input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: 14px;
  margin-bottom: 16px;
}
.form-input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px var(--color-primary-light);
}
.btn-full {
  width: 100%;
  justify-content: center;
  margin-top: 8px;
}
.error {
  color: var(--color-danger);
  font-size: 13px;
  margin-bottom: 8px;
}
.footer-link {
  margin-top: 20px;
  font-size: 14px;
  color: var(--color-text-secondary);
  text-align: center;
}
.footer-link a {
  color: var(--color-primary);
  font-weight: 500;
}
</style>
