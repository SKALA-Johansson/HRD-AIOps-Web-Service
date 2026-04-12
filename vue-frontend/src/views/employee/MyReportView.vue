<template>
  <div class="page">
    <AppHeader />
    <main class="main">
      <h1 class="page-title">성장 리포트</h1>

      <!-- ── 탭 ─────────────────────────────────────── -->
      <div class="tabs">
        <button
          class="tab"
          :class="{ active: tab === 'overall' }"
          @click="tab = 'overall'"
        >전체 리포트</button>
        <button
          class="tab"
          :class="{ active: tab === 'weekly' }"
          @click="tab = 'weekly'; loadWeekly()"
        >주차별 성장 리포트</button>
      </div>

      <!-- ── 전체 리포트 ─────────────────────────────── -->
      <template v-if="tab === 'overall'">
        <div v-if="loading" class="muted state">불러오는 중…</div>
        <p v-else-if="error" class="error">{{ error }}</p>
        <div v-else-if="report" class="card">
          <p class="meta">reportId: {{ report.reportId }}</p>
          <h2 class="sub">강점</h2>
          <ul class="bullet-list">
            <li v-for="(s, i) in report.strengths || []" :key="'s' + i">{{ s }}</li>
          </ul>
          <h2 class="sub">보완</h2>
          <ul class="bullet-list">
            <li v-for="(w, i) in report.weaknesses || []" :key="'w' + i">{{ w }}</li>
          </ul>
          <h2 class="sub">성취 지표</h2>
          <pre class="pre">{{ metrics }}</pre>
        </div>
        <div v-else class="muted state">리포트 데이터가 없습니다.</div>
      </template>

      <!-- ── 주차별 성장 리포트 ──────────────────────── -->
      <template v-if="tab === 'weekly'">
        <div v-if="weeklyLoading" class="muted state">리포트 불러오는 중…</div>
        <p v-else-if="weeklyError" class="error">{{ weeklyError }}</p>
        <div v-else-if="!weeklyReports.length" class="empty-state">
          <div class="empty-icon">★</div>
          <p>아직 완료된 주차 리포트가 없습니다.</p>
          <p class="muted">주차의 모든 모듈 퀴즈를 완료하면 AI가 성장 리포트를 자동으로 생성합니다.</p>
        </div>
        <div v-else class="weekly-list">
          <div
            v-for="rpt in weeklyReports"
            :key="rpt.reportId"
            class="weekly-card"
          >
            <div class="weekly-header" @click="toggleReport(rpt.reportId)">
              <div class="weekly-header-main">
                <div class="weekly-title-row">
                  <span class="week-badge">{{ rpt.weekTitle }}</span>
                  <span v-if="rpt.score != null" class="week-score">평균 {{ Math.round(rpt.score) }}점</span>
                </div>
                <p class="weekly-summary">{{ rpt.summary }}</p>
              </div>
              <span class="toggle-icon">{{ expanded[rpt.reportId] ? '▲' : '▼' }}</span>
            </div>

            <div v-if="expanded[rpt.reportId]" class="weekly-body">
              <div v-if="rpt.strengths?.length" class="report-section">
                <h3 class="report-section-title">강점</h3>
                <ul class="bullet-list">
                  <li v-for="(s, i) in rpt.strengths" :key="i">{{ s }}</li>
                </ul>
              </div>
              <div v-if="rpt.weaknesses?.length" class="report-section">
                <h3 class="report-section-title">개선 필요</h3>
                <ul class="bullet-list">
                  <li v-for="(w, i) in rpt.weaknesses" :key="i">{{ w }}</li>
                </ul>
              </div>
              <div v-if="rpt.recommendations?.length" class="report-section">
                <h3 class="report-section-title">권장 학습</h3>
                <ul class="bullet-list">
                  <li v-for="(r, i) in rpt.recommendations" :key="i">{{ r }}</li>
                </ul>
              </div>
              <div v-if="rpt.detail" class="report-section">
                <h3 class="report-section-title">상세 리포트</h3>
                <div class="report-detail" v-html="renderMarkdown(rpt.detail)" />
              </div>
              <p class="report-date">생성일: {{ formatDate(rpt.createdAt) }}</p>
            </div>
          </div>
        </div>
      </template>
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute } from 'vue-router'
import AppHeader from '@/components/AppHeader.vue'
import { reportsApi } from '@/api/reports.js'
import { tutorApi } from '@/api/tutor.js'
import { useAuthStore } from '@/store/auth.js'

const auth = useAuthStore()
const route = useRoute()

const tab = ref('weekly')  // 기본: 주차별 리포트

// ── 전체 리포트 ──────────────────────────────────────
const userId = ref('1')
const loading = ref(false)
const error = ref('')
const report = ref(null)

function sanitizeMetrics(metricsObj) {
  const src = metricsObj && typeof metricsObj === 'object' ? metricsObj : {}
  const out = {}
  Object.entries(src).forEach(([key, value]) => {
    const lower = String(key).toLowerCase()
    if (lower.includes('api') || lower.includes('endpoint') || lower.includes('url')) return
    out[key] = value
  })
  return out
}

const metrics = computed(() =>
  report.value?.achievementMetrics
    ? JSON.stringify(sanitizeMetrics(report.value.achievementMetrics), null, 2)
    : ''
)

async function loadOverall() {
  loading.value = true
  error.value = ''
  report.value = null
  try {
    const res = await reportsApi.userReport(userId.value)
    report.value = res.data?.data ?? null
  } catch {
    error.value = '성장 리포트를 불러오지 못했습니다.'
  } finally {
    loading.value = false
  }
}

// ── 주차별 성장 리포트 ───────────────────────────────
const weeklyLoading = ref(false)
const weeklyError = ref('')
const weeklyReports = ref([])
const expanded = reactive({})

async function loadWeekly() {
  weeklyLoading.value = true
  weeklyError.value = ''
  weeklyReports.value = []
  try {
    const uid = auth.user?.userId || auth.user?.username || userId.value
    const curriculumId = route.query.curriculum_id || null
    const res = await tutorApi.getWeeklyReports(String(uid), curriculumId)
    weeklyReports.value = res.data?.data ?? []
    // 첫 번째 항목 자동 펼치기
    if (weeklyReports.value.length) {
      expanded[weeklyReports.value[0].reportId] = true
    }
  } catch {
    weeklyError.value = '주차 리포트를 불러오지 못했습니다.'
  } finally {
    weeklyLoading.value = false
  }
}

function toggleReport(id) {
  expanded[id] = !expanded[id]
}

function renderMarkdown(text) {
  if (!text) return ''
  return text
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/^### (.+)$/gm, '<h3>$1</h3>')
    .replace(/^## (.+)$/gm, '<h2>$1</h2>')
    .replace(/^# (.+)$/gm, '<h1>$1</h1>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/^- (.+)$/gm, '<li>$1</li>')
    .replace(/(<li>.*<\/li>\n?)+/g, (m) => `<ul>${m}</ul>`)
    .replace(/\n\n+/g, '</p><p>')
    .replace(/\n/g, '<br>')
}

function formatDate(iso) {
  if (!iso) return ''
  return new Date(iso).toLocaleDateString('ko-KR', {
    year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit',
  })
}

onMounted(() => {
  if (auth.user?.userId) userId.value = String(auth.user.userId)
  // 탭에 맞게 자동 로드
  loadWeekly()
})
</script>

<style scoped>
.page { min-height: 100vh; background: var(--color-bg-secondary); }
.main { max-width: 760px; margin: 0 auto; padding: 28px 24px 64px; }
.page-title { font-size: 1.5rem; font-weight: 700; margin-bottom: 20px; }

/* 탭 */
.tabs { display: flex; gap: 4px; margin-bottom: 24px; border-bottom: 2px solid var(--color-border); }
.tab {
  padding: 10px 18px;
  font-size: 14px;
  font-weight: 500;
  background: none;
  border: none;
  cursor: pointer;
  color: var(--color-text-secondary);
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
  transition: var(--transition);
}
.tab:hover { color: var(--color-text-primary); }
.tab.active { color: var(--color-primary); border-bottom-color: var(--color-primary); font-weight: 700; }

/* 전체 리포트 */
.card { background: var(--color-bg-primary); border: 1px solid var(--color-border); border-radius: var(--radius-lg); padding: 24px; }
.meta { font-size: 13px; color: var(--color-text-muted); margin-bottom: 12px; }
.sub { font-size: 15px; margin: 16px 0 8px; font-weight: 600; }
.pre { background: var(--color-bg-tertiary); padding: 12px; border-radius: var(--radius-md); font-size: 13px; overflow: auto; }

/* 빈 상태 */
.empty-state { text-align: center; padding: 48px 24px; }
.empty-icon { font-size: 48px; color: #d1d5db; margin-bottom: 12px; }
.empty-state p { font-size: 15px; font-weight: 500; margin-bottom: 4px; }
.empty-state .muted { font-size: 13px; }

/* 주차별 리포트 목록 */
.weekly-list { display: flex; flex-direction: column; gap: 12px; }
.weekly-card { background: var(--color-bg-primary); border: 1px solid var(--color-border); border-radius: var(--radius-lg); overflow: hidden; }
.weekly-header {
  display: flex; align-items: flex-start; justify-content: space-between; gap: 12px;
  padding: 18px 20px;
  cursor: pointer;
  user-select: none;
  transition: background var(--transition);
}
.weekly-header:hover { background: var(--color-bg-secondary); }
.weekly-header-main { flex: 1; }
.weekly-title-row { display: flex; align-items: center; gap: 10px; margin-bottom: 6px; }
.week-badge {
  font-size: 12px; font-weight: 700; color: var(--color-primary);
  background: var(--color-primary-light); padding: 3px 10px; border-radius: 999px;
}
.week-score { font-size: 13px; color: var(--color-text-secondary); }
.weekly-summary { font-size: 13px; color: var(--color-text-secondary); margin: 0; line-height: 1.5; }
.toggle-icon { font-size: 12px; color: var(--color-text-muted); flex-shrink: 0; margin-top: 4px; }

.weekly-body { padding: 4px 20px 20px; border-top: 1px solid var(--color-border); }
.report-section { margin-top: 16px; }
.report-section-title { font-size: 13px; font-weight: 700; color: var(--color-text-secondary); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 8px; }
.bullet-list { padding-left: 20px; margin: 0; display: flex; flex-direction: column; gap: 4px; font-size: 14px; line-height: 1.55; }
.report-detail { font-size: 14px; line-height: 1.7; color: var(--color-text-primary); }
.report-detail :deep(h1),
.report-detail :deep(h2),
.report-detail :deep(h3) { font-weight: 700; margin: 12px 0 6px; }
.report-detail :deep(code) { background: var(--color-bg-tertiary); padding: 2px 5px; border-radius: 4px; font-size: 13px; }
.report-detail :deep(ul) { padding-left: 18px; margin: 6px 0; }
.report-detail :deep(strong) { font-weight: 700; }
.report-date { font-size: 12px; color: var(--color-text-muted); margin-top: 16px; }

/* 공통 */
.state { padding: 40px 0; text-align: center; }
.muted { color: var(--color-text-muted); }
.error { color: var(--color-danger); }
</style>
