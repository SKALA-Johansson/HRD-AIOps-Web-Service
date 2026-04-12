<template>
  <div class="page">
    <AppHeader />
    <main class="main">

      <!-- ── 목록 모드 ── -->
      <section v-if="mode === 'list'" class="panel">
        <header class="head">
          <div>
            <h1 class="page-title">커리큘럼 목록</h1>
            <p class="page-desc">생성된 커리큘럼을 확인하고 승인·삭제를 관리합니다.</p>
          </div>
          <div class="actions">
            <button type="button" class="btn btn-outline btn-sm" :disabled="listLoading" @click="loadList">새로고침</button>
            <button type="button" class="btn btn-primary btn-sm" @click="mode = 'create'">PDF로 생성</button>
          </div>
        </header>

        <!-- 상태 필터 탭 -->
        <div class="filter-tabs">
          <button
            v-for="f in FILTERS"
            :key="f.value"
            type="button"
            class="filter-tab"
            :class="{ active: listFilter === f.value }"
            @click="listFilter = f.value"
          >
            {{ f.label }}
            <span class="cnt">{{ countByStatus(f.value) }}</span>
          </button>
        </div>

        <p v-if="listError" class="error">{{ listError }}</p>
        <div v-if="listLoading" class="muted center">불러오는 중…</div>

        <ul v-else-if="filteredList.length" class="curriculum-list">
          <li
            v-for="c in filteredList"
            :key="c.curriculumId"
            class="curriculum-card"
            @click="openReview(c.curriculumId)"
          >
            <div class="c-top">
              <span class="c-title">{{ c.title }}</span>
              <span class="badge" :class="statusClass(c.status)">{{ statusLabel(c.status) }}</span>
            </div>
            <div class="c-meta">
              <span v-if="c.employeeName" class="meta-item meta-name">👤 {{ c.employeeName }}</span>
              <span v-if="c.department" class="meta-item">{{ c.department }}</span>
              <span class="meta-item">모듈 {{ c.modules?.length ?? 0 }}개</span>
            </div>
          </li>
        </ul>
        <p v-else class="muted center">해당 상태의 커리큘럼이 없습니다.</p>
      </section>

      <!-- ── PDF 생성 모드 ── -->
      <section v-else-if="mode === 'create'" class="panel">
        <header class="head">
          <div>
            <h1 class="page-title">PDF로 커리큘럼 생성</h1>
            <p class="page-desc">
              사원 정보를 입력하고 PDF를 업로드한 뒤 <strong>커리큘럼 생성</strong>을 누르면 생성 요청이 전송되고,
              곧바로 <strong>승인/삭제</strong> 화면으로 전환됩니다.
            </p>
          </div>
          <div class="actions">
            <button type="button" class="btn btn-outline btn-sm" @click="goList">← 목록으로</button>
            <button
              type="button"
              class="btn btn-primary btn-sm"
              :disabled="genLoading || !genSelectedFile"
              @click="runGenerateFromPdf"
            >
              {{ genLoading ? '생성 중…' : '커리큘럼 생성' }}
            </button>
          </div>
        </header>

        <section
          class="drop-zone"
          :class="{ dragging: genDragOver, disabled: genLoading }"
          @dragenter.prevent="genDragOver = true"
          @dragover.prevent="genDragOver = true"
          @dragleave.prevent="genDragOver = false"
          @drop.prevent="onGenDrop"
          @click="!genLoading && genFileInput?.click()"
        >
          <input
            ref="genFileInput"
            type="file"
            accept=".pdf,application/pdf"
            class="sr-only"
            :disabled="genLoading"
            @change="onGenFileInput"
          />
          <p v-if="!genSelectedName" class="drop-lead">PDF를 끌어다 놓거나 이 영역을 클릭하세요</p>
          <p v-else class="drop-file">
            <span class="file-name">{{ genSelectedName }}</span>
            <button v-if="!genLoading" type="button" class="btn-text" @click.stop="clearGenFile">선택 취소</button>
          </p>
          <p v-if="genLoading" class="drop-status">커리큘럼 생성 중… (PDF 크기에 따라 수십 초 걸릴 수 있습니다)</p>
        </section>

        <div class="meta-grid">
          <div>
            <label class="form-label">사원 이름</label>
            <input v-model="genMeta.name" class="form-input" :disabled="genLoading" placeholder="예: 김신입" />
          </div>
          <div>
            <label class="form-label">사원 번호</label>
            <input v-model="genMeta.employeeNo" class="form-input" :disabled="genLoading" inputmode="numeric" placeholder="예: 20260001" />
          </div>
          <div>
            <label class="form-label">생년월일(6자리)</label>
            <input v-model="genMeta.birthDate6" class="form-input" :disabled="genLoading" inputmode="numeric" placeholder="예: 990101" />
          </div>
          <div class="span2">
            <label class="form-label">부서</label>
            <select v-model="genMeta.department" class="form-input" :disabled="genLoading">
              <option value="">선택</option>
              <option value="AI">AI</option>
              <option value="BACKEND">BACKEND</option>
              <option value="FRONTEND">FRONTEND</option>
              <option value="DATA">DATA</option>
              <option value="DEVOPS">DEVOPS</option>
            </select>
          </div>
        </div>

        <p v-if="genErr" class="error">{{ genErr }}</p>
        <p v-if="genOk" class="success">{{ genOk }}</p>
      </section>

      <!-- ── 승인/삭제 모드 ── -->
      <section v-else class="panel">
        <header class="head">
          <div>
            <h1 class="page-title">커리큘럼 상세</h1>
          </div>
          <div class="actions">
            <button type="button" class="btn btn-outline btn-sm" @click="goList">← 목록으로</button>
            <button type="button" class="btn btn-primary btn-sm" :disabled="actionBusy || waitingGeneration" @click="doApprove">승인</button>
            <button type="button" class="btn btn-ghost btn-sm danger" :disabled="actionBusy || waitingGeneration" @click="doDelete">삭제</button>
          </div>
        </header>

        <div v-if="waitingGeneration" class="generating-box" role="status" aria-live="polite">
          <div class="spinner" />
          <p class="gen-title">커리큘럼을 생성하고 있어요</p>
          <p class="gen-desc">AI가 PDF를 분석해 보유 역량을 제외한 맞춤 모듈을 만들고 있습니다. 보통 20~60초 걸립니다.</p>
        </div>
        <div v-else-if="loadingDetail" class="muted center">불러오는 중…</div>
        <p v-if="actionErr" class="error">{{ actionErr }}</p>
        <p v-if="actionOk" class="success">{{ actionOk }}</p>

        <div v-if="!waitingGeneration && !loadingDetail" class="card">
          <div class="card-header-row">
            <h2 class="title">{{ detail.title || '커리큘럼' }}</h2>
            <span class="badge" :class="statusClass(detail.status)">{{ statusLabel(detail.status) }}</span>
          </div>
          <div v-if="detail.employeeName || detail.department" class="detail-meta">
            <span v-if="detail.employeeName" class="meta-item meta-name">👤 {{ detail.employeeName }}</span>
            <span v-if="detail.department" class="meta-item">{{ detail.department }}</span>
          </div>
          <!-- 역량 분석 결과 -->
          <template v-if="detail.existingSkills?.length || detail.skillAnalysis">
            <h3 class="sub">역량 분석 결과</h3>
            <div class="skill-analysis-box">
              <div v-if="detail.existingSkills?.length" class="skill-tags">
                <span class="skill-label">보유 역량</span>
                <span v-for="sk in detail.existingSkills" :key="sk" class="skill-tag">{{ sk }}</span>
              </div>
              <table v-if="detail.skillAnalysis?.decisions?.length" class="decision-table">
                <thead>
                  <tr>
                    <th>모듈</th>
                    <th>판단</th>
                    <th>근거</th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="d in detail.skillAnalysis.decisions"
                    :key="d.module_title"
                    :class="decisionRowClass(d.action)"
                  >
                    <td>{{ d.module_title }}</td>
                    <td><span class="decision-badge" :class="decisionBadgeClass(d.action)">{{ decisionLabel(d.action) }}</span></td>
                    <td>{{ d.reason }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </template>

          <h3 class="sub">주차·모듈 구성</h3>
          <ul class="modules">
            <li v-for="m in detail.modules" :key="m.moduleId ?? m.week + '-' + m.title" class="mod-row">
              <span class="week">{{ m.week }}주차</span>
              <span class="mod-title">{{ m.title }}</span>
            </li>
            <li v-if="!detail.modules?.length" class="muted">모듈 정보 없음</li>
          </ul>
        </div>

        <div class="comment-block">
          <label class="form-label">승인 코멘트 (선택)</label>
          <input v-model="currComment" class="form-input" placeholder="예: 검토 완료" :disabled="actionBusy" />
        </div>
      </section>

    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import AppHeader from '@/components/AppHeader.vue'
import { curriculumsApi } from '@/api/curriculums.js'

const FILTERS = [
  { label: '전체', value: 'ALL' },
  { label: '승인', value: 'APPROVED' },
  { label: '검토 대기', value: 'DRAFT' },
  { label: '생성 중', value: 'GENERATING' },
]

const mode = ref('list') // 'list' | 'create' | 'review'

// ── 목록 ──
const listLoading = ref(false)
const listError = ref('')
const listFilter = ref('ALL')
const curricula = ref([])

const filteredList = computed(() => {
  if (listFilter.value === 'ALL') return curricula.value
  return curricula.value.filter(c => (c.status ?? '').toUpperCase() === listFilter.value)
})

function countByStatus(status) {
  if (status === 'ALL') return curricula.value.length
  return curricula.value.filter(c => (c.status ?? '').toUpperCase() === status).length
}

function statusLabel(s) {
  const m = { APPROVED: '승인', DRAFT: '검토 대기', GENERATING: '생성 중', REJECTED: '반려' }
  return m[(s ?? '').toUpperCase()] ?? s ?? '-'
}

function statusClass(s) {
  const m = { APPROVED: 'badge-green', DRAFT: 'badge-yellow', GENERATING: 'badge-blue', REJECTED: 'badge-red' }
  return m[(s ?? '').toUpperCase()] ?? 'badge-gray'
}

async function loadList() {
  listLoading.value = true
  listError.value = ''
  try {
    const res = await curriculumsApi.list({})
    const d = res.data?.data ?? res.data
    curricula.value = Array.isArray(d) ? d : []
  } catch (e) {
    listError.value = '커리큘럼 목록을 불러오지 못했습니다.'
  } finally {
    listLoading.value = false
  }
}

function goList() {
  mode.value = 'list'
  clearGenFile()
  resetDetail()
  loadList()
}

async function openReview(id) {
  resetDetail()
  mode.value = 'review'
  await loadDetailById(id)
}

// ── PDF 생성 ──
const genFileInput = ref(null)
const genDragOver = ref(false)
const genLoading = ref(false)
const genSelectedFile = ref(null)
const genSelectedName = ref('')
const genErr = ref('')
const genOk = ref('')
const genMeta = reactive({ name: '', employeeNo: '', birthDate6: '', department: '' })

function clearGenFile() {
  genSelectedFile.value = null
  genSelectedName.value = ''
  genErr.value = ''
  genOk.value = ''
  if (genFileInput.value) genFileInput.value.value = ''
}

function pickGenPdf(file) {
  if (!file) return
  const ok = file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf')
  if (!ok) { genErr.value = 'PDF 파일만 업로드할 수 있습니다.'; return }
  genErr.value = ''
  genSelectedFile.value = file
  genSelectedName.value = file.name
}

function onGenFileInput(e) { pickGenPdf(e.target?.files?.[0]) }
function onGenDrop(e) { genDragOver.value = false; pickGenPdf(e.dataTransfer?.files?.[0]) }

// ── 승인/삭제 ──
const selectedId = ref(null)
const loadingDetail = ref(false)
const waitingGeneration = ref(false)
const detail = reactive({ curriculumId: null, title: '', status: '', goalId: null, employeeName: '', department: '', modules: [], existingSkills: [], skillAnalysis: null })
const currComment = ref('검토 완료')
const actionBusy = ref(false)
const actionErr = ref('')
const actionOk = ref('')

function resetDetail() {
  selectedId.value = null
  waitingGeneration.value = false
  detail.curriculumId = null
  detail.title = ''
  detail.status = ''
  detail.goalId = null
  detail.modules = []
  detail.existingSkills = []
  detail.skillAnalysis = null
  actionErr.value = ''
  actionOk.value = ''
}

function applyDetail(obj) {
  detail.curriculumId = obj.curriculumId ?? obj.id ?? selectedId.value
  detail.title = obj.title ?? ''
  detail.status = obj.status ?? ''
  detail.goalId = obj.goalId ?? null
  detail.employeeName = obj.employeeName ?? ''
  detail.department = obj.department ?? ''
  detail.modules = Array.isArray(obj.modules) ? [...obj.modules] : []
  detail.existingSkills = Array.isArray(obj.existingSkills) ? obj.existingSkills : []
  detail.skillAnalysis = obj.skillAnalysis ?? null
}

function decisionLabel(action) {
  const m = { INCLUDE: '필수 포함', EXCLUDE: '제외', ADVANCED: '심화 전환' }
  return m[action] ?? action
}

function decisionBadgeClass(action) {
  const m = { INCLUDE: 'badge-green', EXCLUDE: 'badge-red', ADVANCED: 'badge-yellow' }
  return m[action] ?? 'badge-gray'
}

function decisionRowClass(action) {
  const m = { EXCLUDE: 'row-excluded', ADVANCED: 'row-advanced' }
  return m[action] ?? ''
}

async function loadDetailById(id) {
  if (id == null) return
  selectedId.value = id
  loadingDetail.value = true
  actionErr.value = ''
  actionOk.value = ''
  try {
    const res = await curriculumsApi.get(id)
    const d = res.data?.data ?? res.data
    if (d && typeof d === 'object') applyDetail(d)
  } catch (e) {
    actionErr.value = '커리큘럼 정보를 불러오지 못했습니다.'
  } finally {
    loadingDetail.value = false
  }
}

async function runGenerateFromPdf() {
  const file = genSelectedFile.value
  if (!file || genLoading.value) return
  genLoading.value = true
  genErr.value = ''
  genOk.value = ''
  try {
    const fd = new FormData()
    fd.append('file', file)
    if (genMeta.name.trim()) fd.append('name', genMeta.name.trim())
    if (genMeta.employeeNo.trim()) fd.append('employeeNo', genMeta.employeeNo.trim())
    if (genMeta.birthDate6.trim()) fd.append('birthDate6', genMeta.birthDate6.trim())
    if (genMeta.department.trim()) fd.append('department', genMeta.department.trim())
    const autoTitle = [genMeta.department, genMeta.name, genMeta.employeeNo && `(${genMeta.employeeNo})`]
      .filter(Boolean).join(' ').trim()
    fd.append('title', autoTitle || file.name.replace(/\.pdf$/i, ''))

    const res = await curriculumsApi.generateFromPdf(fd)
    const data = res.data?.data ?? res.data
    const id = data?.curriculumId ?? data?.id ?? data?.curriculum?.curriculumId ?? data?.curriculum?.id
    if (id == null) throw new Error('응답에 curriculumId가 없습니다.')

    resetDetail()
    mode.value = 'review'
    waitingGeneration.value = true

    const MAX_POLLS = 36
    let completed = false
    for (let i = 0; i < MAX_POLLS; i++) {
      await new Promise(r => setTimeout(r, 5000))
      try {
        const pollRes = await curriculumsApi.get(id)
        const d = pollRes.data?.data ?? pollRes.data
        if (d && typeof d === 'object') {
          applyDetail(d)
          selectedId.value = id
          const st = (d.status ?? '').toUpperCase()
          if (st !== 'GENERATING') {
            waitingGeneration.value = false
            completed = true
            break
          }
        }
      } catch (_) { /* 폴링 중 일시 오류는 무시 */ }
    }
    if (!completed) {
      actionErr.value = '생성 시간이 길어지고 있어요. 목록에서 확인해 주세요.'
      waitingGeneration.value = false
    }
  } catch (e) {
    const msg = e.response?.data?.detail || e.response?.data?.message || e.message || ''
    genErr.value = `커리큘럼 생성에 실패했습니다. ${msg}`
    waitingGeneration.value = false
  } finally {
    genLoading.value = false
  }
}

async function doApprove() {
  const id = selectedId.value
  if (id == null) return
  actionBusy.value = true
  actionErr.value = ''
  actionOk.value = ''
  try {
    await curriculumsApi.approve(id, { action: 'APPROVE', comment: currComment.value || '' })
    actionOk.value = '승인 처리되었습니다.'
    detail.status = 'APPROVED'
  } catch (e) {
    actionErr.value = '승인 처리에 실패했습니다.'
  } finally {
    actionBusy.value = false
  }
}

async function doDelete() {
  const id = selectedId.value
  if (id == null) return
  if (!window.confirm(`커리큘럼을 삭제할까요?`)) return
  actionBusy.value = true
  actionErr.value = ''
  actionOk.value = ''
  try {
    await curriculumsApi.remove(id)
    actionOk.value = '삭제되었습니다.'
    goList()
  } catch (e) {
    actionErr.value = '삭제에 실패했습니다.'
  } finally {
    actionBusy.value = false
  }
}

onMounted(loadList)
</script>

<style scoped>
.page { min-height: 100vh; background: var(--color-bg-secondary); }
.main { max-width: 980px; margin: 0 auto; padding: 28px 24px 64px; }
.panel { background: var(--color-bg-primary); border: 1px solid var(--color-border); border-radius: var(--radius-lg); padding: 22px; }
.head { display: flex; align-items: flex-start; justify-content: space-between; gap: 12px; flex-wrap: wrap; margin-bottom: 16px; }
.actions { display: flex; gap: 10px; flex-wrap: wrap; }
.page-title { font-size: 1.5rem; font-weight: 700; margin: 0 0 6px; }
.page-desc { font-size: 14px; color: var(--color-text-secondary); line-height: 1.55; margin: 0; }

/* 필터 탭 */
.filter-tabs { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 16px; }
.filter-tab {
  padding: 6px 14px;
  border: 1px solid var(--color-border);
  border-radius: 999px;
  font-size: 13px;
  font-weight: 500;
  background: var(--color-bg-secondary);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: var(--transition);
  display: flex;
  align-items: center;
  gap: 6px;
}
.filter-tab.active, .filter-tab:hover { border-color: var(--color-primary); color: var(--color-primary); background: var(--color-primary-light); }
.cnt { font-size: 11px; font-weight: 700; background: var(--color-bg-tertiary); padding: 1px 6px; border-radius: 999px; }

/* 커리큘럼 카드 목록 */
.curriculum-list { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 10px; }
.curriculum-card {
  padding: 16px 18px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-bg-secondary);
  cursor: pointer;
  transition: var(--transition);
}
.curriculum-card:hover { border-color: var(--color-primary); background: var(--color-primary-light); }
.c-top { display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-bottom: 6px; }
.c-title { font-weight: 650; color: var(--color-text-primary); font-size: 14px; }
.c-meta { display: flex; gap: 12px; font-size: 12px; color: var(--color-text-muted); flex-wrap: wrap; }
.meta-name { color: var(--color-text-secondary); font-weight: 600; }
.detail-meta { display: flex; gap: 12px; font-size: 13px; margin-bottom: 12px; flex-wrap: wrap; }

/* 배지 */
.badge { font-size: 11px; font-weight: 700; padding: 3px 8px; border-radius: 999px; white-space: nowrap; }
.badge-green { background: #d1fae5; color: #065f46; }
.badge-yellow { background: #fef3c7; color: #92400e; }
.badge-blue { background: #dbeafe; color: #1e40af; }
.badge-red { background: #fee2e2; color: #991b1b; }
.badge-gray { background: var(--color-bg-tertiary); color: var(--color-text-muted); }

/* 상세 카드 */
.card { margin-top: 14px; background: var(--color-bg-secondary); border: 1px solid var(--color-border); border-radius: var(--radius-lg); padding: 18px; }
.card-header-row { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; }
.title { font-size: 1.1rem; font-weight: 800; margin: 0; }
.sub { font-size: 14px; font-weight: 700; margin: 0 0 10px; }
.modules { list-style: none; margin: 0; padding: 0; }
.mod-row { display: flex; gap: 12px; padding: 10px 0; border-bottom: 1px solid var(--color-border); font-size: 14px; }
.week { min-width: 56px; color: var(--color-text-muted); font-size: 13px; }
.mod-title { color: var(--color-text-primary); font-weight: 650; }
.comment-block { margin-top: 16px; }

/* PDF 드롭존 */
.sr-only { position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px; overflow: hidden; clip: rect(0,0,0,0); white-space: nowrap; border: 0; }
.drop-zone {
  border: 2px dashed var(--color-border);
  border-radius: var(--radius-lg);
  padding: 18px 16px;
  text-align: center;
  cursor: pointer;
  background: var(--color-bg-secondary);
  transition: var(--transition);
  margin: 14px 0 12px;
}
.drop-zone:hover:not(.disabled), .drop-zone.dragging:not(.disabled) { border-color: var(--color-primary); background: var(--color-primary-light); }
.drop-zone.disabled { cursor: wait; opacity: 0.9; }
.drop-lead { font-size: 14px; color: var(--color-text-secondary); margin: 0; }
.drop-file { margin: 0; display: flex; flex-direction: column; align-items: center; gap: 8px; }
.file-name { font-weight: 650; color: var(--color-text-primary); word-break: break-all; }
.btn-text { border: none; background: none; color: var(--color-primary); font-size: 13px; font-weight: 650; cursor: pointer; text-decoration: underline; }
.drop-status { margin: 10px 0 0; font-size: 13px; color: var(--color-primary); }
.meta-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 8px; }
.meta-grid .span2 { grid-column: 1 / -1; }
@media (max-width: 720px) { .meta-grid { grid-template-columns: 1fr; } }
.form-label { display: block; font-size: 13px; margin-bottom: 6px; }
.form-input { width: 100%; padding: 10px 12px; border: 1px solid var(--color-border); border-radius: var(--radius-md); font-size: 14px; box-sizing: border-box; }

.generating-box {
  margin-top: 14px;
  padding: 22px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  background: var(--color-bg-secondary);
  text-align: center;
}
.spinner {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  border: 3px solid var(--color-border);
  border-top-color: var(--color-primary);
  margin: 0 auto 10px;
  animation: spin 0.9s linear infinite;
}
.gen-title { margin: 0 0 6px; font-size: 16px; font-weight: 700; color: var(--color-text-primary); }
.gen-desc { margin: 0; font-size: 13px; color: var(--color-text-secondary); }
@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }

.success { color: var(--color-success); margin-top: 10px; }
.error { color: var(--color-danger); margin-top: 10px; }
.muted { color: var(--color-text-muted); font-size: 14px; }
.center { text-align: center; margin-top: 20px; }
.danger { color: var(--color-danger) !important; }

/* 역량 분석 */
.skill-analysis-box { margin-bottom: 18px; display: flex; flex-direction: column; gap: 12px; }
.skill-tags { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }
.skill-label { font-size: 12px; font-weight: 700; color: var(--color-text-secondary); margin-right: 4px; }
.skill-tag { font-size: 12px; padding: 3px 10px; background: #dbeafe; color: #1e40af; border-radius: 999px; font-weight: 600; }
.decision-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.decision-table th { text-align: left; padding: 8px 10px; background: var(--color-bg-tertiary); color: var(--color-text-secondary); font-weight: 700; border-bottom: 1px solid var(--color-border); }
.decision-table td { padding: 8px 10px; border-bottom: 1px solid var(--color-border); vertical-align: top; }
.row-excluded td { color: var(--color-text-muted); }
.row-advanced td { font-style: italic; }
.decision-badge { font-size: 11px; font-weight: 700; padding: 2px 7px; border-radius: 999px; white-space: nowrap; }
</style>
