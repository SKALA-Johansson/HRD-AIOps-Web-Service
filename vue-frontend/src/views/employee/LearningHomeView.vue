<template>
  <div class="page">
    <AppHeader />

    <div class="search-strip">
      <div class="search-inner">
        <span class="search-icon" aria-hidden="true">⌕</span>
        <input
          v-model="query"
          type="search"
          class="search-input"
          placeholder="주차·과정명으로 검색"
          autocomplete="off"
        />
      </div>
    </div>

    <main class="main">
      <section class="hero" aria-label="소개">
        <div class="hero-slide">
          <div class="hero-text">
            <p class="hero-kicker">Smart HRD AIOps</p>
            <h1 class="hero-title">
              주차별 온보딩 로드맵을<br />
              위에서 아래로 확인하세요
            </h1>
            <p class="hero-desc">
              배정된 교육은 주차 단위로 정리됩니다. 항목을 누르면 학습 콘텐츠 또는 커리큘럼 상세로 이동합니다.
            </p>
          </div>
          <div class="hero-art">
            <div class="hero-progress">
              <div class="hero-progress-title">나의 학습 진도</div>
              <div class="hero-progress-grid">
                <div class="hero-progress-card">
                  <div class="hero-progress-label">전체 진행률</div>
                  <div class="hero-progress-value">
                    {{ progressLoading ? '—' : progress.completionRate ?? '—' }}<span style="font-size: 12px">%</span>
                  </div>
                </div>
                <div class="hero-progress-card">
                  <div class="hero-progress-label">완료 모듈</div>
                  <div class="hero-progress-value" style="font-size: 16px">
                    {{ progressLoading ? '—' : progress.completedModules ?? '—' }} /
                    {{ progressLoading ? '—' : progress.totalModules ?? '—' }}
                  </div>
                </div>
              </div>
              <div v-if="progressError" class="hero-progress-note">진도를 불러오지 못했습니다.</div>
            </div>
          </div>
        </div>
      </section>

      <section class="section" aria-labelledby="roadmap-title">
        <h2 id="roadmap-title" class="section-title">나의 주차별 교육 일정</h2>

        <div v-if="loading" class="muted state">불러오는 중…</div>
        <p v-else-if="error" class="error state">{{ error }}</p>

        <ol v-else-if="filteredRoadmap.length" class="roadmap" aria-label="주차별 로드맵">
          <li v-for="block in filteredRoadmap" :key="block.week" class="week-block">
            <div class="week-rail" aria-hidden="true">
              <span class="week-dot">{{ block.week }}</span>
              <span class="week-line" />
            </div>
            <div class="week-body">
              <div class="week-header">
                <h3 class="week-label">{{ block.week }}주차</h3>
                <p v-if="block.headline" class="week-headline">{{ block.headline }}</p>
                <div class="week-hover" aria-hidden="true">
                  <span class="mini-pill strong">완료 {{ weekStats(block).done }}/{{ weekStats(block).total }}</span>
                  <span class="mini-pill">진행 중 {{ weekStats(block).inProgress }}</span>
                  <span class="mini-pill">예정 {{ weekStats(block).upcoming }}</span>
                  <span class="mini-pill" :class="{ strong: weekStats(block).submitted }"
                    >과제 제출 {{ weekStats(block).submitted ? '있음' : '없음' }}</span
                  >
                </div>
              </div>
              <ul class="item-list">
                <li v-for="it in block.items" :key="it.key" class="item-row">
                  <router-link
                    v-if="it.href"
                    :to="it.href"
                    class="item-card is-link"
                    :class="`status-${it.status}`"
                  >
                    <div class="item-main">
                      <span class="item-title">{{ it.title }}</span>
                      <span v-if="it.detail" class="item-detail">{{ it.detail }}</span>
                    </div>
                    <span class="status-pill" :data-status="it.status">{{ statusLabel(it.status) }}</span>
                    <div class="hover-tip" aria-hidden="true">
                      <div>상태: <strong>{{ statusLabel(it.status) }}</strong></div>
                      <div v-if="it.moduleId != null">
                        과제 제출: <strong>{{ hasSubmittedForModule(it.moduleId) ? '제출됨' : '미제출' }}</strong>
                      </div>
                      <div v-else>과제 제출: <strong>해당 없음</strong></div>
                    </div>
                  </router-link>
                  <div v-else class="item-card" :class="`status-${it.status}`">
                    <div class="item-main">
                      <span class="item-title">{{ it.title }}</span>
                      <span v-if="it.detail" class="item-detail">{{ it.detail }}</span>
                    </div>
                    <span class="status-pill" :data-status="it.status">{{ statusLabel(it.status) }}</span>
                    <div class="hover-tip" aria-hidden="true">
                      <div>상태: <strong>{{ statusLabel(it.status) }}</strong></div>
                      <div>과제 제출: <strong>해당 없음</strong></div>
                    </div>
                  </div>
                </li>
              </ul>
            </div>
          </li>
        </ol>

        <p v-else-if="!loading && !error" class="empty muted">
          {{ emptyMessage }}
        </p>
      </section>
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import AppHeader from '@/components/AppHeader.vue'
import { learningApi } from '@/api/learning.js'

const loading = ref(true)
const error = ref('')
const rawItems = ref([])
const query = ref('')

const progressLoading = ref(true)
const progressError = ref('')
const progress = reactive({
  completionRate: null,
  completedModules: null,
  totalModules: null
})

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
  return !!readSubmissions()[String(moduleId)]
}

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

function hasModulesInList(list) {
  return list.some((c) => Array.isArray(c.modules) && c.modules.length > 0)
}

function normalizeStatus(s) {
  const x = String(s || '').toLowerCase()
  if (/완료|done|complete|completed|수료/i.test(x)) return 'done'
  if (/진행|progress|ing|진행 중/i.test(x)) return 'in_progress'
  return 'upcoming'
}

function itemHref(curriculumId, moduleId) {
  if (moduleId != null && moduleId !== '') return `/learning/modules/${moduleId}`
  if (curriculumId != null) return `/curriculums/${curriculumId}`
  return null
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
  return buildFromCurriculaFlatWeeks(list)
})

const filteredRoadmap = computed(() => {
  const q = query.value.trim().toLowerCase()
  if (!q) return roadmap.value
  return roadmap.value
    .map((block) => ({
      ...block,
      items: block.items.filter(
        (it) =>
          it.title.toLowerCase().includes(q) ||
          (it.detail && it.detail.toLowerCase().includes(q)) ||
          String(block.week).includes(q)
      )
    }))
    .filter((block) => block.items.length > 0)
})

const emptyMessage = computed(() =>
  query.value.trim()
    ? '검색과 일치하는 주차·과정이 없습니다.'
    : '아직 배정된 커리큘럼이 없습니다.'
)

function statusLabel(s) {
  const m = { done: '완료', in_progress: '진행 중', upcoming: '예정' }
  return m[s] || '예정'
}

onMounted(async () => {
  loading.value = true
  error.value = ''
  progressLoading.value = true
  progressError.value = ''

  try {
    const res = await learningApi.myCurriculums()
    const d = res.data?.data
    rawItems.value = Array.isArray(d) ? d : d ? [d] : []
  } catch (e) {
    error.value = '커리큘럼 목록을 불러오지 못했습니다.'
  } finally {
    loading.value = false
  }

  try {
    const res = await learningApi.myProgress()
    const d = res.data?.data
    if (d) {
      progress.completionRate = d.completionRate
      progress.completedModules = d.completedModules
      progress.totalModules = d.totalModules
    }
  } catch (e) {
    progressError.value = '학습 진도를 불러오지 못했습니다.'
  } finally {
    progressLoading.value = false
  }
})
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: var(--color-bg-secondary);
}
.search-strip {
  background: var(--color-bg-primary);
  border-bottom: 1px solid var(--color-border);
  padding: 12px 24px;
}
.search-inner {
  max-width: 800px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 16px;
  border-radius: 999px;
  border: 1px solid var(--color-border);
  background: var(--color-bg-secondary);
}
.search-icon {
  font-size: 18px;
  color: var(--color-text-muted);
  line-height: 1;
}
.search-input {
  flex: 1;
  border: none;
  background: transparent;
  font-size: 15px;
  outline: none;
  font-family: inherit;
}
.search-input::placeholder {
  color: var(--color-text-muted);
}
.main {
  max-width: 800px;
  margin: 0 auto;
  padding: 24px 24px 72px;
}
.hero {
  margin-bottom: 40px;
}
.hero-slide {
  display: grid;
  grid-template-columns: 1.2fr 1fr;
  gap: 24px;
  align-items: center;
  min-height: 200px;
  padding: 28px 32px;
  border-radius: var(--radius-xl);
  background: linear-gradient(120deg, var(--sk-navy-deep) 0%, var(--sk-red) 42%, var(--sk-navy) 100%);
  color: var(--color-hero-text);
  overflow: hidden;
  box-shadow: var(--shadow-lg);
}
@media (max-width: 768px) {
  .hero-slide { grid-template-columns: 1fr; min-height: auto; }
  .hero-art { min-height: 100px; }
}
.hero-kicker {
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.06em;
  opacity: 0.85;
  margin-bottom: 10px;
}
.hero-title {
  font-size: clamp(1.2rem, 3.2vw, 1.65rem);
  font-weight: 700;
  line-height: 1.35;
  margin-bottom: 12px;
}
.hero-desc {
  font-size: 14px;
  opacity: 0.88;
  line-height: 1.55;
}
.hero-art {
  border-radius: var(--radius-lg);
  background:
    radial-gradient(circle at 30% 40%, rgba(255,255,255,0.14) 0%, transparent 50%),
    radial-gradient(circle at 70% 60%, rgba(0,114,198,0.38) 0%, transparent 48%);
  min-height: 140px;
  display: flex;
  align-items: stretch;
}
.hero-progress {
  width: 100%;
  padding: 16px;
  display: grid;
  gap: 10px;
}
.hero-progress-title {
  font-size: 12px;
  font-weight: 700;
  opacity: 0.9;
}
.hero-progress-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}
.hero-progress-card {
  border: 1px solid rgba(255,255,255,0.22);
  background: rgba(255,255,255,0.10);
  border-radius: 14px;
  padding: 12px;
}
.hero-progress-label {
  font-size: 12px;
  opacity: 0.85;
}
.hero-progress-value {
  font-size: 18px;
  font-weight: 800;
  margin-top: 4px;
}
.hero-progress-note {
  font-size: 12px;
  opacity: 0.82;
  line-height: 1.4;
}
.section-title {
  font-size: 1.15rem;
  font-weight: 800;
  letter-spacing: -0.3px;
  margin-bottom: 24px;
  padding-bottom: 12px;
  border-bottom: 2px solid var(--color-primary);
}
.roadmap { list-style: none; margin: 0; padding: 0; }
.week-block {
  display: grid;
  grid-template-columns: 48px 1fr;
  gap: 0 16px;
  margin-bottom: 8px;
}
.week-rail {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 6px;
}
.week-dot {
  flex-shrink: 0;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--color-primary);
  color: #fff;
  font-size: 15px;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: var(--shadow-sm);
}
.week-line {
  flex: 1;
  width: 3px;
  min-height: 24px;
  margin-top: 8px;
  margin-bottom: -8px;
  background: linear-gradient(180deg, var(--color-primary-light) 0%, var(--color-border) 100%);
  border-radius: 2px;
}
.week-block:last-child .week-line { display: none; }
.week-body { padding-bottom: 28px; }
.week-label {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--color-primary);
  margin-bottom: 4px;
}
.week-headline {
  font-size: 17px;
  font-weight: 700;
  color: var(--color-text-primary);
  line-height: 1.35;
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
  gap: 16px;
  padding: 14px 16px;
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  background: var(--color-bg-primary);
  transition: var(--transition);
  text-align: left;
  color: inherit;
  border-left-width: 4px;
  border-left-color: var(--color-border);
  position: relative;
}
.item-card.is-link { cursor: pointer; }
.item-card.is-link:hover { border-color: var(--color-primary); box-shadow: var(--shadow-sm); }
.item-card.status-done { border-left-color: var(--color-success); }
.item-card.status-in_progress { border-left-color: var(--color-primary); }
.item-card.status-upcoming { border-left-color: var(--color-border-hover); }
.item-main { display: flex; flex-direction: column; gap: 4px; min-width: 0; }
.item-title { font-size: 15px; font-weight: 600; line-height: 1.4; }
.item-detail { font-size: 13px; color: var(--color-text-muted); line-height: 1.45; }
.status-pill {
  flex-shrink: 0;
  font-size: 11px;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 20px;
  background: var(--color-bg-tertiary);
  color: var(--color-text-secondary);
}
.status-pill[data-status='done'] { background: var(--color-success-light); color: var(--color-success); }
.status-pill[data-status='in_progress'] { background: var(--color-primary-light); color: var(--color-primary); }
.state { padding: 24px 0; }
.empty { padding: 32px 0; font-size: 14px; line-height: 1.55; }
.muted { color: var(--color-text-muted); }
.error { color: var(--color-danger); }
.week-hover { display: none; margin-top: 8px; gap: 8px; flex-wrap: wrap; }
.week-block:hover .week-hover { display: flex; }
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
.mini-pill.strong { background: var(--color-primary-light); color: var(--color-primary); border-color: var(--color-primary-light); }
.hover-tip {
  position: absolute;
  left: 12px;
  right: 12px;
  top: calc(100% + 8px);
  display: none;
  z-index: 2;
  padding: 10px 12px;
  border-radius: 12px;
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-sm);
  font-size: 12px;
  color: var(--color-text-secondary);
}
.item-card:hover .hover-tip { display: block; }
</style>
