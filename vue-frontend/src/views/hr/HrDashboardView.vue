<template>
  <div class="page">
    <AppHeader />
    <main class="main">
      <h1 class="page-title">교육 현황 대시보드</h1>
      <p class="page-desc">GET <code>/reports/dashboard</code> — 계열사·직무군 필터</p>

      <div class="filters">
        <div>
          <label class="form-label">company</label>
          <input v-model="company" class="form-input" placeholder="SKT" />
        </div>
        <div>
          <label class="form-label">jobFamily</label>
          <input v-model="jobFamily" class="form-input" placeholder="AI/Data" />
        </div>
        <button type="button" class="btn btn-primary btn-sm" @click="load">조회</button>
      </div>

      <p v-if="usedMock" class="mock-hint">개발 미리보기: 대시보드 수치는 더미입니다.</p>
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
import { useAuthStore } from '@/store/auth.js'
import { MOCK_DASHBOARD } from '@/data/devMock.js'

const auth = useAuthStore()
const company = ref('SKT')
const jobFamily = ref('AI/Data')
const loading = ref(true)
const error = ref('')
const usedMock = ref(false)
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

function applyMock() {
  usedMock.value = true
  dash.totalEmployees = MOCK_DASHBOARD.totalEmployees
  dash.avgCompletionRate = MOCK_DASHBOARD.avgCompletionRate
  dash.delayedLearners = MOCK_DASHBOARD.delayedLearners
  dash.topWeaknessAreas = [...MOCK_DASHBOARD.topWeaknessAreas]
  error.value = ''
}

async function load() {
  loading.value = true
  error.value = ''
  usedMock.value = false
  try {
    const res = await reportsApi.dashboard({
      company: company.value,
      jobFamily: jobFamily.value
    })
    const d = res.data?.data
    if (d) {
      dash.totalEmployees = d.totalEmployees
      dash.avgCompletionRate = d.avgCompletionRate
      dash.delayedLearners = d.delayedLearners
      dash.topWeaknessAreas = d.topWeaknessAreas ?? []
    } else if (auth.isDevPreview) {
      applyMock()
    }
  } catch (e) {
    error.value = e.response?.data?.message || e.message || '조회 실패'
    if (auth.isDevPreview) applyMock()
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: var(--color-bg-secondary);
}
.main {
  max-width: 1000px;
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
  margin-bottom: 20px;
}
.page-desc code {
  font-size: 12px;
  background: var(--color-bg-tertiary);
  padding: 2px 6px;
  border-radius: 4px;
}
.filters {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  align-items: flex-end;
  margin-bottom: 24px;
}
.form-label {
  display: block;
  font-size: 13px;
  margin-bottom: 6px;
}
.form-input {
  padding: 10px 12px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  width: 200px;
  font-size: 14px;
}
.btn-sm {
  padding: 10px 18px;
}
.stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}
.stat-card {
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.stat-card.wide {
  grid-column: 1 / -1;
}
.label {
  font-size: 13px;
  color: var(--color-text-secondary);
}
.value {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-primary);
}
.tags {
  font-size: 15px;
  line-height: 1.5;
}
.muted {
  color: var(--color-text-muted);
}
.error {
  color: var(--color-danger);
}
.mock-hint {
  font-size: 13px;
  color: var(--color-text-muted);
  margin-bottom: 12px;
}
</style>
