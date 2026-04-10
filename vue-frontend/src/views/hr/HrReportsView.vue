<template>
  <div class="page">
    <AppHeader />
    <main class="main">
      <h1 class="page-title">성장 리포트 (HR)</h1>
      <p class="page-desc">
        수강 중인 신입사원 목록에서 선택해 리포트를 열람합니다. (리포트 조회:
        <code>GET /reports/users/{userId}</code>)
      </p>

      <div class="workspace">
        <section class="list-panel" aria-label="수강 중인 신입사원 목록">
          <div class="list-head">
            <h2 class="panel-title">수강 중인 신입사원</h2>
            <button type="button" class="btn btn-outline btn-sm" :disabled="listLoading" @click="loadUsers">
              {{ listLoading ? '불러오는 중…' : '새로고침' }}
            </button>
          </div>
          <input v-model="query" class="search" placeholder="이름 또는 ID 검색" />
          <p v-if="usedMockUsers" class="mock-hint">개발 미리보기: 더미 목록입니다.</p>
          <p v-if="listError" class="error">{{ listError }}</p>
          <ul v-if="filteredUsers.length" class="user-list">
            <li v-for="u in filteredUsers" :key="u.userId">
              <button type="button" class="user-card" :class="{ selected: selectedUserId === u.userId }" @click="selectUser(u)">
                <div class="user-top">
                  <span class="user-name">{{ u.name || '신입' }}</span>
                  <span class="pill">ID {{ u.userId }}</span>
                </div>
                <div class="user-meta">
                  <span v-if="u.completionRate != null" class="meta">진행률 {{ u.completionRate }}%</span>
                  <span v-if="u.status" class="meta">상태 {{ u.status }}</span>
                  <span v-if="u.lastModule" class="meta">최근 {{ u.lastModule }}</span>
                </div>
              </button>
            </li>
          </ul>
          <p v-else-if="!listLoading" class="muted">표시할 신입사원 목록이 없습니다.</p>
        </section>

        <section class="detail-panel" aria-label="선택한 신입사원 성장 리포트">
          <template v-if="!selectedUserId">
            <p class="placeholder">왼쪽에서 신입사원을 선택하면 성장 리포트가 표시됩니다.</p>
          </template>
          <template v-else>
            <div v-if="loading" class="muted">불러오는 중…</div>
            <p v-else-if="error" class="error">{{ error }}</p>
            <div v-else-if="report" class="card">
              <p class="meta">reportId: {{ report.reportId }} / userId: {{ report.userId }}</p>
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
          </template>
        </section>
      </div>
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import AppHeader from '@/components/AppHeader.vue'
import { reportsApi } from '@/api/reports.js'
import { useAuthStore } from '@/store/auth.js'
import { MOCK_TEAM_PROGRESS } from '@/data/devMock.js'

const auth = useAuthStore()

const query = ref('')
const listLoading = ref(false)
const listError = ref('')
const usedMockUsers = ref(false)
const users = ref([])
const selectedUserId = ref(null)

const loading = ref(false)
const error = ref('')
const report = ref(null)

const metrics = computed(() =>
  report.value?.achievementMetrics ? JSON.stringify(report.value.achievementMetrics, null, 2) : ''
)

const filteredUsers = computed(() => {
  const q = query.value.trim().toLowerCase()
  if (!q) return users.value
  return users.value.filter(
    (u) =>
      String(u.userId).includes(q) ||
      String(u.name || '').toLowerCase().includes(q)
  )
})

async function loadUsers() {
  listLoading.value = true
  listError.value = ''
  usedMockUsers.value = false
  try {
    const res = await reportsApi.users({ status: 'IN_PROGRESS' })
    const d = res.data?.data ?? res.data
    const list = Array.isArray(d) ? d : Array.isArray(d?.content) ? d.content : Array.isArray(d?.items) ? d.items : []
    users.value = list
    if (!users.value.length && auth.isDevPreview) {
      users.value = [...MOCK_TEAM_PROGRESS]
      usedMockUsers.value = true
    }
  } catch (e) {
    if (auth.isDevPreview) {
      users.value = [...MOCK_TEAM_PROGRESS]
      usedMockUsers.value = true
      listError.value = ''
    } else {
      listError.value = e.response?.data?.message || e.message || '신입사원 목록을 불러오지 못했습니다.'
      users.value = []
    }
  } finally {
    listLoading.value = false
  }
}

async function loadUserReport(id) {
  loading.value = true
  error.value = ''
  report.value = null
  try {
    const res = await reportsApi.userReport(id)
    report.value = res.data?.data ?? null
  } catch (e) {
    error.value = e.response?.data?.message || e.message || '조회 실패'
  } finally {
    loading.value = false
  }
}

function selectUser(u) {
  if (!u?.userId) return
  selectedUserId.value = u.userId
  loadUserReport(u.userId)
}

onMounted(loadUsers)
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: var(--color-bg-secondary);
}
.main {
  max-width: 1100px;
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
.workspace {
  margin-top: 16px;
  display: grid;
  grid-template-columns: minmax(300px, 380px) 1fr;
  gap: 24px;
  align-items: start;
}
@media (max-width: 900px) {
  .workspace {
    grid-template-columns: 1fr;
  }
}
.list-panel,
.detail-panel {
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 20px;
}
.list-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 10px;
}
.panel-title {
  font-size: 15px;
  font-weight: 800;
  margin: 0;
}
.search {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: 14px;
  margin-bottom: 10px;
  background: var(--color-bg-secondary);
}
.user-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.user-card {
  width: 100%;
  text-align: left;
  padding: 14px 16px;
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  background: var(--color-bg-secondary);
  cursor: pointer;
  transition: var(--transition);
}
.user-card:hover {
  border-color: var(--color-border-hover);
}
.user-card.selected {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 1px var(--color-primary);
  background: var(--color-primary-light);
}
.user-top {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  margin-bottom: 6px;
}
.user-name {
  font-weight: 650;
  color: var(--color-text-primary);
}
.pill {
  font-size: 11px;
  font-weight: 700;
  padding: 3px 8px;
  border-radius: 999px;
  background: var(--color-bg-tertiary);
  color: var(--color-text-secondary);
}
.user-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  font-size: 12px;
  color: var(--color-text-muted);
}
.placeholder {
  font-size: 14px;
  color: var(--color-text-muted);
  margin: 24px 0;
  text-align: center;
  line-height: 1.5;
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
.mock-hint {
  font-size: 13px;
  color: var(--color-text-muted);
  margin: 0 0 10px;
}
</style>
