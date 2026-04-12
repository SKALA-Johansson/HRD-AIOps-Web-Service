<template>
  <div class="page">
    <AppHeader />
    <main class="main">
      <h1 class="page-title">성장 리포트</h1>

      <div class="row">
        <div>
          <label class="form-label">userId</label>
          <input v-model="userId" class="form-input narrow" />
        </div>
        <button type="button" class="btn btn-outline btn-sm" @click="load">조회</button>
      </div>

      <div v-if="loading" class="muted">불러오는 중…</div>
      <p v-else-if="error" class="error">{{ error }}</p>
      <div v-else-if="report" class="card">
        <p class="meta">reportId: {{ report.reportId }}</p>
        <h2 class="sub">강점</h2>
        <ul>
          <li v-for="(s, i) in report.strengths || []" :key="'s' + i">{{ s }}</li>
        </ul>
        <h2 class="sub">보완</h2>
        <ul>
          <li v-for="(w, i) in report.weaknesses || []" :key="'w' + i">{{ w }}</li>
        </ul>
        <h2 class="sub">성취 지표</h2>
        <pre class="pre">{{ metrics }}</pre>
      </div>
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import AppHeader from '@/components/AppHeader.vue'
import { reportsApi } from '@/api/reports.js'
import { useAuthStore } from '@/store/auth.js'

const auth = useAuthStore()
const userId = ref('1')
const loading = ref(false)
const error = ref('')
const report = ref(null)

const metrics = computed(() =>
  report.value?.achievementMetrics ? JSON.stringify(report.value.achievementMetrics, null, 2) : ''
)

async function load() {
  loading.value = true
  error.value = ''
  report.value = null
  try {
    const res = await reportsApi.userReport(userId.value)
    report.value = res.data?.data ?? null
  } catch (e) {
    error.value = '성장 리포트를 불러오지 못했습니다.'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  if (auth.user?.userId) userId.value = String(auth.user.userId)
  load()
})
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: var(--color-bg-secondary);
}
.main {
  max-width: 720px;
  margin: 0 auto;
  padding: 28px 24px 64px;
}
.page-title {
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: 8px;
}
.page-desc {
  font-size: 14px;
  color: var(--color-text-secondary);
  margin-bottom: 16px;
}
.page-desc code {
  font-size: 12px;
  background: var(--color-bg-tertiary);
  padding: 2px 6px;
  border-radius: 4px;
}
.form-label {
  display: block;
  font-size: 13px;
  margin-bottom: 6px;
}
.row {
  display: flex;
  align-items: flex-end;
  gap: 12px;
  margin-bottom: 20px;
}
.form-input.narrow {
  max-width: 200px;
  padding: 10px 12px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: 14px;
}
.btn-sm {
  padding: 8px 14px;
  font-size: 13px;
  margin-bottom: 2px;
}
.card {
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 24px;
}
.meta {
  font-size: 13px;
  color: var(--color-text-muted);
  margin-bottom: 12px;
}
.sub {
  font-size: 15px;
  margin: 16px 0 8px;
}
.pre {
  background: var(--color-bg-tertiary);
  padding: 12px;
  border-radius: var(--radius-md);
  font-size: 13px;
  overflow: auto;
}
.muted {
  color: var(--color-text-muted);
}
.error {
  color: var(--color-danger);
}
</style>
