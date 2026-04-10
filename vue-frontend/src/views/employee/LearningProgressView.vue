<template>
  <div class="page">
    <AppHeader />
    <main class="main">
      <h1 class="page-title">학습 진도</h1>
      <p class="page-desc">GET <code>/learning/progress/me</code></p>

      <div v-if="loading" class="muted">불러오는 중…</div>
      <template v-else>
        <p v-if="error" class="error">{{ error }}</p>
        <p v-if="usedMock" class="mock-hint">개발 미리보기: 더미 진도 수치입니다.</p>
      </template>
      <div v-if="!loading && showStats" class="stats">
        <div class="stat-card">
          <span class="label">전체 진행률</span>
          <span class="value">{{ data.completionRate ?? '—' }}%</span>
        </div>
        <div class="stat-card">
          <span class="label">완료 모듈</span>
          <span class="value">{{ data.completedModules ?? '—' }} / {{ data.totalModules ?? '—' }}</span>
        </div>
      </div>

      <section v-if="!loading" class="detail">
        <h2 class="sub">주차별 진행 · 과제 제출 상태</h2>
        <p class="hint">
          학습 탭과 동일한 주차 로드맵 기반 표시입니다. 과제 제출은 모듈 화면에서 제출 시 브라우저 세션에 기록됩니다.
        </p>

        <ol v-if="filteredRoadmap.length" class="roadmap">
          <li v-for="block in filteredRoadmap" :key="block.week" class="week-block">
            <div class="week-head">
              <span class="week-no">{{ block.week }}주차</span>
              <span class="mini-pill strong">완료 {{ weekStats(block).done }}/{{ weekStats(block).total }}</span>
              <span class="mini-pill">진행 중 {{ weekStats(block).inProgress }}</span>
              <span class="mini-pill">예정 {{ weekStats(block).upcoming }}</span>
              <span class="mini-pill" :class="{ strong: weekStats(block).submitted }"
                >과제 제출 {{ weekStats(block).submitted ? '있음' : '없음' }}</span
              >
            </div>

            <ul class="item-list">
              <li v-for="it in block.items" :key="it.key" class="item-row">
                <router-link v-if="it.href" :to="it.href" class="item-card is-link" :class="`status-${it.status}`">
                  <div class="item-main">
                    <span class="item-title">{{ it.title }}</span>
                    <span v-if="it.detail" class="item-detail">{{ it.detail }}</span>
                  </div>
                  <div class="item-right">
                    <span class="status-pill" :data-status="it.status">{{ statusLabel(it.status) }}</span>
                    <span v-if="it.moduleId != null" class="submit-pill" :data-on="hasSubmittedForModule(it.moduleId)">
                      {{ hasSubmittedForModule(it.moduleId) ? '과제 제출' : '미제출' }}
                    </span>
                  </div>
                </router-link>
                <div v-else class="item-card" :class="`status-${it.status}`">
                  <div class="item-main">
                    <span class="item-title">{{ it.title }}</span>
                    <span v-if="it.detail" class="item-detail">{{ it.detail }}</span>
                  </div>
                  <div class="item-right">
                    <span class="status-pill" :data-status="it.status">{{ statusLabel(it.status) }}</span>
                  </div>
                </div>
              </li>
            </ul>
          </li>
        </ol>
        <p v-else class="muted">표시할 주차 로드맵이 없습니다.</p>
      </section>
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import AppHeader from '@/components/AppHeader.vue'
import { learningApi } from '@/api/learning.js'
import { useAuthStore } from '@/store/auth.js'
import { MOCK_PROGRESS, sampleCoursesForUser, sampleWeeklyRoadmap } from '@/data/devMock.js'

const auth = useAuthStore()
const loading = ref(true)
const error = ref('')
const usedMock = ref(false)
const data = ref({ completionRate: null, completedModules: null, totalModules: null })

const rawItems = ref([])

const showStats = computed(
  () =>
    data.value.completionRate != null ||
    data.value.completedModules != null ||
    data.value.totalModules != null
)

function applyMock() {
  usedMock.value = true
  data.value = { ...MOCK_PROGRESS }
  error.value = ''
}

const SUBMISSION_STORAGE_KEY = 'shrd_submissions_v1'

function readSubmissions() {
  try {
    return JSON.parse(sessionStorage.getItem(SUBMISSION_STORAGE_KEY) || '{}')
  } catch {
    return {}
  }
}

function hasSubmittedForModule(moduleId) {
  if (moduleId == null) return false
  const all = readSubmissions()
  return !!all[String(moduleId)]
}

function normalizeStatus(s) {
  const x = String(s || '').toLowerCase()
  if (/완료|done|complete|approved|수료/i.test(x)) return 'done'
  if (/진행|progress|ing|진행 중/i.test(x)) return 'in_progress'
  if (/draft|임시/i.test(x)) return 'upcoming'
  return 'upcoming'
}

function itemHref(curriculumId, moduleId) {
  if (moduleId != null && moduleId !== '') return `/learning/modules/${moduleId}`
  if (curriculumId != null) return `/curriculums/${curriculumId}`
  return null
}

function hasModulesInList(list) {
  return list.some((c) => Array.isArray(c.modules) && c.modules.length > 0)
}

function focusHeadline(items) {
  const t = items.map((i) => i.detail).find(Boolean)
  return t ? `핵심 과정: ${t}` : ''
}

function buildFromCurriculaWithModules(list) {
  const map = new Map()
  for (const c of list) {
    const cid = c.curriculumId ?? c.id
    const ctitle = c.title || `커리큘럼 ${cid}`
    for (const m of c.modules || []) {
      const w = Number(m.week) || 1
      if (!map.has(w)) map.set(w, { week: w, headline: '', items: [] })
      map.get(w).items.push({
        title: m.title || '모듈',
        detail: ctitle,
        moduleId: m.moduleId,
        curriculumId: cid,
        status: normalizeStatus(m.status || c.status),
        href: itemHref(cid, m.moduleId),
        key: `${cid}-${m.moduleId ?? m.title}`
      })
    }
  }
  return [...map.entries()]
    .sort((a, b) => a[0] - b[0])
    .map(([, block]) => ({ ...block, headline: block.headline || focusHeadline(block.items) }))
}

function buildFromCurriculaFlatWeeks(list) {
  return list.map((c, i) => {
    const cid = c.curriculumId ?? c.id
    const w = i + 1
    return {
      week: w,
      headline: `${w}주차 · 배정 과정`,
      items: [
        {
          title: c.title || `과정 ${w}`,
          detail: [c.company, c.status].filter(Boolean).join(' · ') || '상세에서 주차·모듈 확인',
          curriculumId: cid,
          moduleId: null,
          status: normalizeStatus(c.status),
          href: itemHref(cid, null),
          key: `c-${cid}`
        }
      ]
    }
  })
}

const roadmap = computed(() => {
  const list = rawItems.value
  if (!list.length) return []
  if (hasModulesInList(list)) return buildFromCurriculaWithModules(list)
  if (auth.isDevPreview) {
    return sampleWeeklyRoadmap(auth.user?.name).map((block) => ({
      ...block,
      items: block.items.map((it) => ({
        ...it,
        status: it.status || 'upcoming',
        href: itemHref(it.curriculumId, it.moduleId),
        key: `${it.curriculumId}-${it.moduleId ?? it.title}`
      }))
    }))
  }
  return buildFromCurriculaFlatWeeks(list)
})

const filteredRoadmap = computed(() => roadmap.value)

function weekStats(block) {
  const items = Array.isArray(block?.items) ? block.items : []
  const total = items.length
  const done = items.filter((it) => it.status === 'done').length
  const inProgress = items.filter((it) => it.status === 'in_progress').length
  const upcoming = items.filter((it) => it.status === 'upcoming').length
  const modules = items.map((it) => it.moduleId).filter((x) => x != null)
  const submitted = modules.some((m) => hasSubmittedForModule(m))
  return { total, done, inProgress, upcoming, submitted }
}

function statusLabel(s) {
  const m = { done: '완료', in_progress: '진행 중', upcoming: '예정' }
  return m[s] || '예정'
}

onMounted(async () => {
  loading.value = true
  usedMock.value = false
  try {
    const res = await learningApi.myProgress()
    const d = res.data?.data
    if (d) {
      data.value = {
        completionRate: d.completionRate,
        completedModules: d.completedModules,
        totalModules: d.totalModules
      }
    } else if (auth.isDevPreview) {
      applyMock()
    }
  } catch (e) {
    error.value = e.response?.data?.message || e.message || '조회 실패'
    if (auth.isDevPreview) applyMock()
  } finally {
    loading.value = false
  }

  try {
    const res = await learningApi.myCurriculums()
    const d = res.data?.data
    let list = Array.isArray(d) ? d : d ? [d] : []
    if (!list.length && auth.isDevPreview) list = sampleCoursesForUser(auth.user?.name)
    rawItems.value = list
  } catch {
    if (auth.isDevPreview) rawItems.value = sampleCoursesForUser(auth.user?.name)
  }
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
  margin-bottom: 24px;
}
.page-desc code {
  font-size: 12px;
  background: var(--color-bg-tertiary);
  padding: 2px 6px;
  border-radius: 4px;
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
.label {
  font-size: 13px;
  color: var(--color-text-secondary);
}
.value {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-primary);
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

.detail {
  margin-top: 28px;
}
.sub {
  font-size: 16px;
  margin: 0 0 8px;
}
.hint {
  font-size: 13px;
  color: var(--color-text-secondary);
  margin: 0 0 14px;
  line-height: 1.5;
}
.roadmap {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.week-block {
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  background: var(--color-bg-primary);
  padding: 16px 16px;
}
.week-head {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}
.week-no {
  font-weight: 800;
  color: var(--color-text-primary);
  margin-right: 4px;
}
.mini-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 12px;
  background: var(--color-bg-tertiary);
  color: var(--color-text-secondary);
  border: 1px solid var(--color-border);
}
.mini-pill.strong {
  background: var(--color-primary-light);
  color: var(--color-primary);
  border-color: var(--color-primary-light);
}
.item-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.item-card {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 14px;
  padding: 12px 14px;
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  background: var(--color-bg-secondary);
  transition: var(--transition);
  text-align: left;
  color: inherit;
  border-left-width: 4px;
  border-left-color: var(--color-border);
}
.item-card.is-link:hover {
  border-color: var(--color-primary);
  box-shadow: var(--shadow-sm);
}
.item-card.status-done {
  border-left-color: var(--color-success);
}
.item-card.status-in_progress {
  border-left-color: var(--color-primary);
}
.item-card.status-upcoming {
  border-left-color: var(--color-border-hover);
}
.item-main {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}
.item-title {
  font-size: 14px;
  font-weight: 650;
  line-height: 1.4;
}
.item-detail {
  font-size: 12px;
  color: var(--color-text-muted);
  line-height: 1.45;
}
.item-right {
  display: flex;
  flex-direction: column;
  gap: 8px;
  align-items: flex-end;
  flex-shrink: 0;
}
.status-pill {
  font-size: 11px;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 20px;
  background: var(--color-bg-tertiary);
  color: var(--color-text-secondary);
}
.status-pill[data-status='done'] {
  background: var(--color-success-light);
  color: var(--color-success);
}
.status-pill[data-status='in_progress'] {
  background: var(--color-primary-light);
  color: var(--color-primary);
}
.submit-pill {
  font-size: 11px;
  font-weight: 700;
  padding: 4px 10px;
  border-radius: 20px;
  border: 1px solid var(--color-border);
  background: var(--color-bg-primary);
  color: var(--color-text-secondary);
}
.submit-pill[data-on='true'] {
  border-color: var(--color-success-light);
  background: var(--color-success-light);
  color: var(--color-success);
}
</style>
