<template>
  <div class="page">
    <AppHeader />
    <main class="main">
      <h1 class="page-title">교육 현황 대시보드</h1>

<div v-if="loading" class="muted">불러오는 중…</div>
      <p v-if="error" class="error">{{ error }}</p>
      <div v-if="showDash" class="stats">
        <div class="stat-card">
          <span class="label">전체 인원</span>
          <span class="value">{{ dash.totalEmployees ?? '—' }}</span>
        </div>
        <div class="stat-card">
          <span class="label">평균 이수율</span>
          <span class="value">{{ dash.avgCompletionRate ?? '—' }}%</span>
        </div>
        <div class="stat-card">
          <span class="label">지연 학습자</span>
          <span class="value">{{ dash.delayedLearners ?? '—' }}</span>
        </div>
        <div class="stat-card wide">
          <span class="label">주요 약점 영역</span>
          <span class="tags">{{ (dash.topWeaknessAreas || []).join(', ') || '—' }}</span>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import AppHeader from '@/components/AppHeader.vue'
import { reportsApi } from '@/api/reports.js'

const loading = ref(true)
const error = ref('')
const dash = reactive({
  totalEmployees: null,
  avgCompletionRate: null,
  delayedLearners: null,
  topWeaknessAreas: []
})

const showDash = computed(
  () =>
    dash.totalEmployees != null ||
    dash.avgCompletionRate != null ||
    dash.delayedLearners != null ||
    (Array.isArray(dash.topWeaknessAreas) && dash.topWeaknessAreas.length > 0)
)

async function load() {
  loading.value = true
  error.value = ''
  try {
    const res = await reportsApi.dashboard({})
    const d = res.data?.data
    if (d) {
      dash.totalEmployees = d.totalEmployees
      dash.avgCompletionRate = d.avgCompletionRate
      dash.delayedLearners = d.delayedLearners
      dash.topWeaknessAreas = d.topWeaknessAreas ?? []
    }
  } catch (e) {
    error.value = '대시보드 데이터를 불러오지 못했습니다.'
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.page { min-height: 100vh; background: var(--color-bg-secondary); }
.main { max-width: 1000px; margin: 0 auto; padding: 28px 24px 64px; }
.page-title { font-size: 1.5rem; font-weight: 700; margin-bottom: 20px; }
.stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; }
.stat-card {
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.stat-card.wide { grid-column: 1 / -1; }
.label { font-size: 13px; color: var(--color-text-secondary); }
.value { font-size: 1.5rem; font-weight: 700; color: var(--color-primary); }
.tags { font-size: 15px; line-height: 1.5; }
.muted { color: var(--color-text-muted); }
.error { color: var(--color-danger); }
</style>
