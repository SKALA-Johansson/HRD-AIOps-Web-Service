<template>
  <div class="auth-page">
    <div class="auth-toolbar">
      <ThemeToggle />
    </div>
    <div class="auth-card fade-in-up">
      <router-link to="/" class="back-link">← 홈</router-link>
      <h1 class="title">회원가입</h1>
      <p class="desc">역할을 선택하고 가입합니다. (API: POST <code>/auth/signup</code>)</p>

      <form class="form" @submit.prevent="submit">
        <label class="form-label">이름</label>
        <input v-model="form.name" type="text" class="form-input" required />

        <label class="form-label">이메일</label>
        <input v-model="form.email" type="email" class="form-input" required autocomplete="username" />

        <label class="form-label">비밀번호</label>
        <input
          v-model="form.password"
          type="password"
          class="form-input"
          required
          autocomplete="new-password"
        />

        <label class="form-label">역할</label>
        <select v-model="form.role" class="form-input">
          <option value="EMPLOYEE">신입사원 (EMPLOYEE)</option>
          <option value="HR">HR 담당자 (HR)</option>
        </select>

        <p v-if="error" class="error">{{ error }}</p>
        <p v-if="success" class="success">{{ success }}</p>

        <button type="submit" class="btn btn-primary btn-full" :disabled="loading">
          {{ loading ? '처리 중…' : '가입하기' }}
        </button>
      </form>

      <p class="footer-link">
        이미 계정이 있으신가요?
        <router-link to="/login">로그인</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth.js'
import ThemeToggle from '@/components/ThemeToggle.vue'

const form = reactive({
  name: '',
  email: '',
  password: '',
  role: 'EMPLOYEE'
})
const loading = ref(false)
const error = ref('')
const success = ref('')

const auth = useAuthStore()
const router = useRouter()

async function submit() {
  error.value = ''
  success.value = ''
  loading.value = true
  try {
    const res = await auth.signup({
      name: form.name,
      email: form.email,
      password: form.password,
      role: form.role
    })
    success.value = res.data?.message || '가입이 완료되었습니다. 로그인해 주세요.'
    setTimeout(() => router.push('/login'), 800)
  } catch (e) {
    error.value = e.response?.data?.message || e.message || '회원가입에 실패했습니다.'
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
.title {
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: 8px;
}
.desc {
  font-size: 14px;
  color: var(--color-text-secondary);
  margin-bottom: 24px;
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
}
.btn-full {
  width: 100%;
  justify-content: center;
}
.error {
  color: var(--color-danger);
  font-size: 13px;
  margin-bottom: 8px;
}
.success {
  color: var(--color-success);
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
