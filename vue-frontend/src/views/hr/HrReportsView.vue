<template>
  <div class="page">
    <AppHeader />
    <main class="main">
      <h1 class="page-title">성장 리포트 (HR)</h1>

      <div class="workspace">
        <!-- 왼쪽: 사원 목록 -->
        <section class="list-panel" aria-label="수강 중인 신입사원 목록">
          <div class="list-head">
            <h2 class="panel-title">신입사원 목록</h2>
            <button type="button" class="btn btn-outline btn-sm" :disabled="listLoading" @click="loadUsers">
              {{ listLoading ? '불러오는 중…' : '새로고침' }}
            </button>
          </div>
          <input v-model="query" class="search" placeholder="이름 또는 사원번호 검색" />
          <p v-if="listError" class="error">{{ listError }}</p>
          <ul v-if="filteredUsers.length" class="user-list">
            <li v-for="u in filteredUsers" :key="u.userId">
              <button
                type="button"
                class="user-card"
                :class="{ selected: selectedUserId === u.userId }"
                @click="selectUser(u)"
              >
                <div class="user-top">
                  <span class="user-name">{{ u.name || '신입' }}</span>
                  <span class="pill">사번 {{ u.username || '-' }}</span>
                </div>
                <div class="user-meta">
                  <span v-if="u.completionRate != null" class="meta">진행률 {{ u.completionRate }}%</span>
                  <span v-if="u.status" class="meta">상태 {{ u.status }}</span>
                  <span v-if="u.lastModule" class="meta">최근 {{ u.lastModule }}</span>
                </div>
              </button>
            </li>
          </ul>
          <p v-else-if="!listLoading" class="muted center">표시할 신입사원 목록이 없습니다.</p>
        </section>

        <!-- 오른쪽: 퀴즈 리포트 목록 -->
        <section class="detail-panel" aria-label="선택한 신입사원 퀴즈 리포트">
          <template v-if="!selectedUserId">
            <p class="placeholder">왼쪽에서 신입사원을 선택하면 학습 리포트가 표시됩니다.</p>
          </template>
          <template v-else>
            <div class="detail-head">
              <h2 class="panel-title">{{ selectedUserName }} 학습 리포트</h2>
              <button type="button" class="btn btn-outline btn-sm" :disabled="loading" @click="loadReports(selectedUserId)">
                {{ loading ? '불러오는 중…' : '새로고침' }}
              </button>
            </div>

            <div v-if="loading" class="muted center">불러오는 중…</div>
            <p v-else-if="error" class="error">{{ error }}</p>

            <div v-else-if="!reports.length" class="empty-state">
              <div class="empty-icon">★</div>
              <p>아직 생성된 퀴즈 리포트가 없습니다.</p>
              <p class="muted">퀴즈를 제출하면 AI가 자동으로 리포트를 생성합니다.</p>
            </div>

            <div v-else class="report-list">
              <div v-for="rpt in reports" :key="rpt.reportId" class="report-card">
                <div class="report-header" @click="toggle(rpt.reportId)">
                  <div class="report-header-main">
                    <div class="report-title-row">
                      <span class="module-badge">{{ rpt.moduleTitle }}</span>
                      <span class="type-badge" :class="rpt.reportType">
                        {{ rpt.reportType === 'assignment' ? '과제' : rpt.reportType === 'growth' ? '성장리포트' : '퀴즈' }}
                      </span>
                      <span
                        v-if="rpt.reportType !== 'growth'"
                        class="pass-badge"
                        :class="rpt.passed ? 'pass' : 'fail'"
                      >{{ rpt.passed ? '합격' : '불합격' }}</span>
                      <span v-if="rpt.score != null" class="score-chip">
                        {{ Math.round(rpt.score) }} / {{ Math.round(rpt.maxScore ?? 100) }}점
                      </span>
                    </div>
                    <p class="report-summary">{{ rpt.summary }}</p>
                  </div>
                  <span class="toggle-icon">{{ expanded[rpt.reportId] ? '▲' : '▼' }}</span>
                </div>

                <div v-if="expanded[rpt.reportId]" class="report-body">
                  <div v-if="rpt.strengths?.length" class="report-section">
                    <h3 class="section-label">강점</h3>
                    <ul class="bullet-list">
                      <li v-for="(s, i) in rpt.strengths" :key="i">{{ s }}</li>
                    </ul>
                  </div>
                  <div v-if="rpt.weaknesses?.length" class="report-section">
                    <h3 class="section-label">개선 필요</h3>
                    <ul class="bullet-list">
                      <li v-for="(w, i) in rpt.weaknesses" :key="i">{{ w }}</li>
                    </ul>
                  </div>
                  <div v-if="rpt.recommendations?.length" class="report-section">
                    <h3 class="section-label">권장 학습</h3>
                    <ul class="bullet-list">
                      <li v-for="(r, i) in rpt.recommendations" :key="i">{{ r }}</li>
                    </ul>
                  </div>
                  <div v-if="rpt.detail" class="report-section">
                    <h3 class="section-label">상세 분석</h3>
                    <div class="report-detail" v-html="renderMarkdown(rpt.detail)" />
                  </div>
                  <p class="report-date">생성일: {{ formatDate(rpt.createdAt) }}</p>
                </div>
              </div>
            </div>
          </template>
        </section>
      </div>
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import AppHeader from '@/components/AppHeader.vue'
import { reportsApi } from '@/api/reports.js'
import { tutorApi } from '@/api/tutor.js'

const query = ref('')
const listLoading = ref(false)
const listError = ref('')
const users = ref([])
const selectedUserId = ref(null)

const loading = ref(false)
const error = ref('')
const reports = ref([])
const expanded = reactive({})

const selectedUserName = computed(() => {
  const u = users.value.find((u) => String(u.userId) === String(selectedUserId.value))
  return u?.name || u?.username || '사원'
})

const filteredUsers = computed(() => {
  const q = query.value.trim().toLowerCase()
  if (!q) return users.value
  return users.value.filter(
    (u) =>
      String(u.username || '').toLowerCase().includes(q) ||
      String(u.name || '').toLowerCase().includes(q) ||
      String(u.userId || '').includes(q)
  )
})

async function loadUsers() {
  listLoading.value = true
  listError.value = ''
  try {
    const res = await reportsApi.users({})
    const d = res.data?.data ?? res.data
    users.value = Array.isArray(d) ? d : Array.isArray(d?.content) ? d.content : []
  } catch {
    listError.value = '신입사원 목록을 불러오지 못했습니다.'
    users.value = []
  } finally {
    listLoading.value = false
  }
}

async function loadReports(userId) {
  loading.value = true
  error.value = ''
  reports.value = []
  try {
    const res = await tutorApi.getHrQuizReports(String(userId))
    reports.value = res.data?.data ?? []
    // 첫 번째 자동 펼치기
    if (reports.value.length) {
      expanded[reports.value[0].reportId] = true
    }
  } catch {
    error.value = '퀴즈 리포트를 불러오지 못했습니다.'
  } finally {
    loading.value = false
  }
}

function selectUser(u) {
  if (!u?.userId) return
  selectedUserId.value = u.userId
  loadReports(u.userId)
}

function toggle(id) {
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

onMounted(loadUsers)
</script>

<style scoped>
.page { min-height: 100vh; background: var(--color-bg-secondary); }
.main { max-width: 1200px; margin: 0 auto; padding: 28px 24px 64px; }
.page-title { font-size: 1.5rem; font-weight: 700; margin-bottom: 20px; }

.workspace { display: grid; grid-template-columns: minmax(280px, 340px) 1fr; gap: 24px; align-items: start; }
@media (max-width: 900px) { .workspace { grid-template-columns: 1fr; } }

.list-panel, .detail-panel {
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 20px;
}

/* 사원 목록 */
.list-head, .detail-head {
  display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-bottom: 10px;
}
.panel-title { font-size: 15px; font-weight: 800; margin: 0; }
.search {
  width: 100%; padding: 10px 12px;
  border: 1px solid var(--color-border); border-radius: var(--radius-md);
  font-size: 14px; margin-bottom: 10px; background: var(--color-bg-secondary);
}
.user-list { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 10px; }
.user-card {
  width: 100%; text-align: left; padding: 14px 16px;
  border-radius: var(--radius-md); border: 1px solid var(--color-border);
  background: var(--color-bg-secondary); cursor: pointer; transition: var(--transition);
}
.user-card:hover { border-color: var(--color-border-hover); }
.user-card.selected { border-color: var(--color-primary); box-shadow: 0 0 0 1px var(--color-primary); background: var(--color-primary-light); }
.user-top { display: flex; justify-content: space-between; gap: 10px; margin-bottom: 6px; }
.user-name { font-weight: 650; color: var(--color-text-primary); }
.pill { font-size: 11px; font-weight: 700; padding: 3px 8px; border-radius: 999px; background: var(--color-bg-tertiary); color: var(--color-text-secondary); }
.user-meta { display: flex; flex-wrap: wrap; gap: 8px; font-size: 12px; color: var(--color-text-muted); }

/* 빈 상태 */
.empty-state { text-align: center; padding: 40px 16px; }
.empty-icon { font-size: 40px; color: #d1d5db; margin-bottom: 10px; }
.empty-state p { font-size: 15px; font-weight: 500; margin-bottom: 4px; }
.empty-state .muted { font-size: 13px; }

/* 리포트 목록 */
.report-list { display: flex; flex-direction: column; gap: 10px; margin-top: 16px; }
.report-card { border: 1px solid var(--color-border); border-radius: var(--radius-lg); overflow: hidden; }
.report-header {
  display: flex; align-items: flex-start; justify-content: space-between; gap: 12px;
  padding: 16px 18px; cursor: pointer; user-select: none; transition: background var(--transition);
}
.report-header:hover { background: var(--color-bg-secondary); }
.report-header-main { flex: 1; }
.report-title-row { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; margin-bottom: 6px; }
.module-badge {
  font-size: 12px; font-weight: 700; color: var(--color-primary);
  background: var(--color-primary-light); padding: 3px 10px; border-radius: 999px;
}
.pass-badge {
  font-size: 11px; font-weight: 700; padding: 2px 8px; border-radius: 999px;
}
.pass-badge.pass { background: var(--color-success-light); color: #065f46; }
.pass-badge.fail { background: #fff3f3; color: var(--color-danger); }
.type-badge { font-size: 11px; font-weight: 700; padding: 2px 8px; border-radius: 999px; background: var(--color-bg-tertiary); color: var(--color-text-secondary); }
.type-badge.assignment { background: #eff6ff; color: #1d4ed8; }
.type-badge.quiz { background: #f0fdf4; color: #15803d; }
.type-badge.growth { background: #fefce8; color: #a16207; }
.score-chip { font-size: 13px; color: var(--color-text-secondary); }
.report-summary { font-size: 13px; color: var(--color-text-secondary); margin: 0; line-height: 1.5; }
.toggle-icon { font-size: 12px; color: var(--color-text-muted); flex-shrink: 0; margin-top: 4px; }

.report-body { padding: 4px 18px 18px; border-top: 1px solid var(--color-border); }
.report-section { margin-top: 14px; }
.section-label {
  font-size: 12px; font-weight: 700; color: var(--color-text-secondary);
  text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px;
}
.bullet-list { padding-left: 18px; margin: 0; display: flex; flex-direction: column; gap: 3px; font-size: 13px; line-height: 1.55; }
.report-detail { font-size: 13px; line-height: 1.7; color: var(--color-text-primary); }
.report-detail :deep(h1), .report-detail :deep(h2), .report-detail :deep(h3) { font-weight: 700; margin: 10px 0 4px; }
.report-detail :deep(code) { background: var(--color-bg-tertiary); padding: 2px 5px; border-radius: 4px; font-size: 12px; }
.report-detail :deep(ul) { padding-left: 16px; margin: 4px 0; }
.report-detail :deep(strong) { font-weight: 700; }
.report-date { font-size: 12px; color: var(--color-text-muted); margin-top: 14px; }

/* 공통 */
.placeholder { font-size: 14px; color: var(--color-text-muted); margin: 24px 0; text-align: center; line-height: 1.5; }
.center { text-align: center; }
.muted { color: var(--color-text-muted); }
.error { color: var(--color-danger); }
</style>
