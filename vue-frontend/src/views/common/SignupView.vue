<template>
  <div class="auth-page">
    <div class="auth-toolbar">
      <ThemeToggle />
    </div>
    <div class="auth-card fade-in-up">
      <router-link to="/" class="back-link">← 홈</router-link>
      <h1 class="title">회원가입</h1>

      <form class="form" @submit.prevent="submit">
        <label class="form-label">이름</label>
        <input v-model="form.name" type="text" class="form-input" required />

        <label class="form-label">사원번호 / 아이디</label>
        <input v-model="form.username" type="text" class="form-input" required autocomplete="username" />

        <label class="form-label">비밀번호</label>
        <input
          v-model="form.password"
          type="password"
          class="form-input"
          required
          autocomplete="new-password"
        />

        <label class="form-label">역할</label>
        <div class="role-box">
          <span class="role-pill">HR 담당자 (HR)</span>
          <span class="role-hint">신입사원 계정은 커리큘럼 등록 시 자동 생성/등록될 예정입니다.</span>
        </div>

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
  username: '',
  password: '',
  role: 'HR'
})
const loading = ref(false)
const error = ref('')
const success = ref('')

const auth = useAuthStore()
const router = useRouter()

async function submit() {
  error.value = ''
  success.value = ''
  if (form.role === 'EMPLOYEE') {
    error.value = '신입사원(EMPLOYEE) 회원가입은 현재 비활성화되어 있습니다.'
    return
  }
  loading.value = true
  try {
    const res = await auth.signup({
      name: form.name,
      username: form.username,
      password: form.password,
      role: form.role
    })
    success.value = res.data?.message || '가입이 완료되었습니다. 로그인해 주세요.'
    setTimeout(() => router.push('/login'), 800)
  } catch (e) {
    error.value = '회원가입에 실패했습니다. 잠시 후 다시 시도해 주세요.'
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
.role-box {
  width: 100%;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 10px 12px;
  margin-bottom: 16px;
  background: var(--color-bg-tertiary);
  display: grid;
  gap: 6px;
}
.role-pill {
  display: inline-flex;
  align-items: center;
  width: fit-content;
  padding: 4px 10px;
  border-radius: 999px;
  background: rgba(59, 130, 246, 0.12);
  color: var(--color-text-primary);
  font-size: 12px;
  font-weight: 600;
  border: 1px solid rgba(59, 130, 246, 0.25);
}
.role-hint {
  color: var(--color-text-secondary);
  font-size: 12px;
  line-height: 1.35;
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
