<template>
  <div class="page">
    <AppHeader />
    <main class="main">
      <h1 class="page-title">AI 튜터링 가이드</h1>

      <div class="query-row">
        <input v-model="employeeId" class="form-input" placeholder="신입사원 ID (예: 1)" />
        <button type="button" class="btn btn-primary btn-sm" :disabled="loading" @click="fetchGuide">
          {{ loading ? '생성 중…' : '가이드 생성' }}
        </button>
      </div>

      <p v-if="error" class="error">{{ error }}</p>

      <template v-if="guide">
        <section class="card">
          <h2 class="sub">AI 튜터 응답</h2>
          <p class="body">{{ guide }}</p>
        </section>
      </template>
      <p v-else-if="!loading && !error" class="muted">신입사원 ID를 입력하고 가이드 생성 버튼을 누르세요.</p>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import AppHeader from '@/components/AppHeader.vue'
import { tutorApi } from '@/api/tutor.js'

const employeeId = ref('')
const loading = ref(false)
const error = ref('')
const guide = ref('')

async function fetchGuide() {
  if (!employeeId.value.trim()) { error.value = '신입사원 ID를 입력하세요.'; return }
  loading.value = true
  error.value = ''
  guide.value = ''
  try {
    const res = await tutorApi.ask({
      userId: Number(employeeId.value.trim()) || 0,
      curriculumId: '0',
      question: '이 신입사원의 학습 현황을 분석하고 멘토링 가이드를 작성해주세요.'
    })
    const d = res.data?.data ?? res.data
    guide.value = d?.answer ?? d?.response ?? '가이드가 생성되었습니다.'
  } catch (e) {
    error.value = 'AI 튜터링 가이드를 생성하지 못했습니다. 잠시 후 다시 시도해 주세요.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.page { min-height: 100vh; background: var(--color-bg-secondary); }
.main { max-width: 720px; margin: 0 auto; padding: 28px 24px 64px; }
.page-title { font-size: 1.5rem; font-weight: 700; margin-bottom: 20px; }
.query-row { display: flex; gap: 12px; margin-bottom: 20px; }
.form-input { padding: 10px 12px; border: 1px solid var(--color-border); border-radius: var(--radius-md); font-size: 14px; width: 200px; }
.btn-sm { padding: 10px 18px; }
.card { background: var(--color-bg-primary); border: 1px solid var(--color-border); border-radius: var(--radius-lg); padding: 20px; margin-bottom: 16px; }
.sub { font-size: 16px; margin-bottom: 12px; }
.body { font-size: 14px; line-height: 1.7; color: var(--color-text-secondary); white-space: pre-wrap; }
.muted { color: var(--color-text-muted); font-size: 14px; }
.error { color: var(--color-danger); margin-bottom: 12px; }
</style>
