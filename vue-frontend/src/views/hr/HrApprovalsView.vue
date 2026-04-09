<template>
  <div class="page">
    <AppHeader />
    <main class="main">
      <section class="flow-head">
        <h1 class="page-title">커리큘럼 (생성 → 대기 목록 → 검토/승인)</h1>
        <p class="page-desc">
          1) PDF 업로드로 생성 요청 → 2) 승인 대기 목록에서 선택 → 3) 구성 확인 후 승인·반려·수정·삭제
        </p>
      </section>

      <section class="create-panel" aria-label="1) 커리큘럼 생성">
        <div class="create-head">
          <h2 class="panel-title">1) PDF로 커리큘럼 생성</h2>
          <div class="create-actions">
            <button type="button" class="btn btn-outline btn-sm" :disabled="genLoading" @click="clearGenFile">
              초기화
            </button>
            <button
              type="button"
              class="btn btn-primary btn-sm"
              :disabled="genLoading || !genSelectedFile"
              @click="runGenerateFromPdf"
            >
              {{ genLoading ? '생성 중…' : '생성 요청' }}
            </button>
          </div>
        </div>

        <p class="hint">
          <code>POST /curriculums/generate-from-pdf</code> (multipart, 필드: <code>file</code>) — 버튼을 눌러야 요청이
          전송됩니다.
        </p>

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
            <label class="form-label">계열사 (company)</label>
            <input v-model="genMeta.company" class="form-input" :disabled="genLoading" />
          </div>
          <div>
            <label class="form-label">직무군 (jobFamily)</label>
            <input v-model="genMeta.jobFamily" class="form-input" :disabled="genLoading" />
          </div>
          <div class="span2">
            <label class="form-label">커리큘럼 제목 힌트 (title)</label>
            <input
              v-model="genMeta.title"
              class="form-input"
              placeholder="비우면 파일명을 사용합니다"
              :disabled="genLoading"
            />
          </div>
        </div>

        <p v-if="genOk" class="success">{{ genOk }}</p>
        <p v-if="genErr" class="error">{{ genErr }}</p>
        <pre v-if="genResultJson" class="pre">{{ genResultJson }}</pre>
      </section>

      <header class="page-head">
        <div>
          <h2 class="panel-title">2) 승인 대기 목록</h2>
          <p class="page-desc">
            AI(PDF)가 생성한 커리큘럼은 <code>GET /curriculums?status=PENDING_APPROVAL</code> 등으로 조회한 뒤, 카드를
            선택해 내용을 검토하고 승인·반려·수정·삭제합니다. 승인:
            <code>POST /approvals/curriculums/{id}</code>
          </p>
        </div>
        <button type="button" class="btn btn-outline btn-sm" :disabled="loadingList" @click="loadPendingCurricula">
          {{ loadingList ? '불러오는 중…' : '목록 새로고침' }}
        </button>
      </header>

      <p v-if="usedMockList" class="mock-hint">개발 미리보기: 승인 대기 목록은 더미입니다.</p>
      <p v-if="listErr" class="error banner-err">{{ listErr }}</p>

      <div class="workspace">
        <section class="list-panel" aria-label="승인 대기 커리큘럼 목록">
          <h3 class="panel-title">승인 대기 커리큘럼</h3>
          <p v-if="!loadingList && !curricula.length" class="empty">대기 중인 커리큘럼이 없습니다.</p>
          <ul v-else class="card-list">
            <li v-for="c in curricula" :key="c.curriculumId">
              <button
                type="button"
                class="cur-card"
                :class="{ selected: selectedId === c.curriculumId }"
                @click="selectCurriculum(c)"
              >
                <div class="cur-card-top">
                  <span class="cur-title">{{ c.title || `커리큘럼 #${c.curriculumId}` }}</span>
                  <span class="badge" :class="badgeClass(c.status)">{{ c.status || '—' }}</span>
                </div>
                <p class="cur-summary">{{ c.summary || formatSummary(c) }}</p>
                <div class="cur-meta">
                  <span v-if="c.sourceType === 'PDF_AI'" class="meta-pill">PDF·AI 생성</span>
                  <span v-if="c.createdAt" class="meta-date">{{ formatDate(c.createdAt) }}</span>
                  <span class="meta-id">ID {{ c.curriculumId }}</span>
                </div>
              </button>
            </li>
          </ul>
        </section>

        <section class="detail-panel" aria-label="선택한 커리큘럼 상세">
          <template v-if="!selectedId">
            <p class="placeholder">왼쪽 목록에서 커리큘럼을 선택하면 구성과 내용을 확인할 수 있습니다.</p>
          </template>
          <template v-else>
            <div v-if="loadingDetail" class="muted">상세 불러오는 중…</div>
            <template v-else>
              <div class="detail-head">
                <h3 class="panel-title">3) 검토 · {{ detail.title }}</h3>
                <span class="badge" :class="badgeClass(detail.status)">{{ detail.status || '—' }}</span>
              </div>

              <div v-if="!editMode" class="module-block">
                <h3 class="sub">주차·모듈 구성</h3>
                <ul class="modules">
                  <li v-for="m in detail.modules" :key="m.moduleId ?? m.week + '-' + m.title" class="mod-row">
                    <span class="week">{{ m.week }}주차</span>
                    <span class="mod-title">{{ m.title }}</span>
                  </li>
                  <li v-if="!detail.modules?.length" class="muted">모듈 정보 없음</li>
                </ul>
              </div>

              <div v-else class="edit-block">
                <label class="form-label">제목</label>
                <input v-model="draftTitle" class="form-input" />
                <label class="form-label">모듈 (JSON 배열 — moduleId, week, title)</label>
                <textarea v-model="draftModulesJson" class="form-input area" rows="12" spellcheck="false" />
                <p v-if="editParseErr" class="error">{{ editParseErr }}</p>
              </div>

              <div class="comment-block">
                <label class="form-label">승인/반려 코멘트</label>
                <input v-model="currComment" class="form-input" placeholder="검토 의견을 입력하세요" />
              </div>

              <p v-if="actionErr" class="error">{{ actionErr }}</p>
              <p v-if="actionOk" class="success">{{ actionOk }}</p>

              <div class="actions">
                <template v-if="!editMode">
                  <button type="button" class="btn btn-primary btn-sm" :disabled="actionBusy" @click="doApprove">
                    승인
                  </button>
                  <button type="button" class="btn btn-outline btn-sm" :disabled="actionBusy" @click="doReject">
                    반려
                  </button>
                  <button type="button" class="btn btn-outline btn-sm" :disabled="actionBusy" @click="startEdit">
                    수정
                  </button>
                  <button type="button" class="btn btn-ghost btn-sm danger" :disabled="actionBusy" @click="doDelete">
                    삭제
                  </button>
                </template>
                <template v-else>
                  <button type="button" class="btn btn-primary btn-sm" :disabled="actionBusy" @click="saveEdit">
                    저장
                  </button>
                  <button type="button" class="btn btn-ghost btn-sm" :disabled="actionBusy" @click="cancelEdit">
                    취소
                  </button>
                </template>
              </div>
            </template>
          </template>
        </section>
      </div>

      <details class="extra">
        <summary>목표 승인 · 승인 이력 (기존 API)</summary>
        <section class="card">
          <h2 class="sub">목표 승인</h2>
          <label class="form-label">goalId</label>
          <input v-model="goalId" class="form-input narrow" />
          <label class="form-label">코멘트</label>
          <input v-model="goalComment" class="form-input" />
          <div class="row">
            <button type="button" class="btn btn-primary btn-sm" @click="approveGoal">승인</button>
          </div>
        </section>
        <section class="card">
          <h2 class="sub">승인 이력 조회</h2>
          <label class="form-label">resourceType</label>
          <select v-model="histType" class="form-input narrow">
            <option value="CURRICULUM">CURRICULUM</option>
            <option value="GOAL">GOAL</option>
          </select>
          <label class="form-label">resourceId</label>
          <input v-model="histResourceId" class="form-input narrow" />
          <button type="button" class="btn btn-outline btn-sm" @click="loadHistory">조회</button>
          <pre v-if="historyJson" class="pre">{{ historyJson }}</pre>
        </section>
      </details>

      <p v-if="err" class="error footer-err">{{ err }}</p>
    </main>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import AppHeader from '@/components/AppHeader.vue'
import { approvalsApi } from '@/api/approvals.js'
import { curriculumsApi } from '@/api/curriculums.js'
import { useAuthStore } from '@/store/auth.js'
import { MOCK_PENDING_CURRICULA } from '@/data/devMock.js'

const auth = useAuthStore()

const genFileInput = ref(null)
const genDragOver = ref(false)
const genLoading = ref(false)
const genSelectedFile = ref(null)
const genSelectedName = ref('')
const genErr = ref('')
const genOk = ref('')
const genResultJson = ref('')
const genMeta = reactive({
  company: 'SK hynix',
  jobFamily: 'Backend',
  title: ''
})

const loadingList = ref(false)
const loadingDetail = ref(false)
const usedMockList = ref(false)
const listErr = ref('')
const curricula = ref([])

const selectedId = ref(null)
const detail = reactive({
  curriculumId: null,
  title: '',
  status: '',
  summary: '',
  sourceType: '',
  createdAt: '',
  goalId: null,
  modules: []
})

const currComment = ref('검토 완료 — 커리큘럼 구성이 교육 목표와 부합합니다.')
const editMode = ref(false)
const draftTitle = ref('')
const draftModulesJson = ref('')
const editParseErr = ref('')

const actionBusy = ref(false)
const actionErr = ref('')
const actionOk = ref('')

const goalId = ref('101')
const goalComment = ref('적절한 목표입니다.')
const histType = ref('CURRICULUM')
const histResourceId = ref('301')
const historyJson = ref('')
const err = ref('')

function clearGenFile() {
  genSelectedFile.value = null
  genSelectedName.value = ''
  genErr.value = ''
  genOk.value = ''
  genResultJson.value = ''
  if (genFileInput.value) genFileInput.value.value = ''
}

function pickGenPdf(file) {
  if (!file) return
  const ok = file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf')
  if (!ok) {
    genErr.value = 'PDF 파일만 업로드할 수 있습니다.'
    return
  }
  genErr.value = ''
  genOk.value = ''
  genResultJson.value = ''
  genSelectedFile.value = file
  genSelectedName.value = file.name
}

function onGenFileInput(e) {
  const f = e.target?.files?.[0]
  pickGenPdf(f)
}

function onGenDrop(e) {
  genDragOver.value = false
  const f = e.dataTransfer?.files?.[0]
  pickGenPdf(f)
}

async function runGenerateFromPdf() {
  const file = genSelectedFile.value
  if (!file || genLoading.value) return
  genLoading.value = true
  genErr.value = ''
  genOk.value = ''
  genResultJson.value = ''
  try {
    const fd = new FormData()
    fd.append('file', file)
    if (genMeta.company.trim()) fd.append('company', genMeta.company.trim())
    if (genMeta.jobFamily.trim()) fd.append('jobFamily', genMeta.jobFamily.trim())
    const t = genMeta.title.trim()
    fd.append('title', t || file.name.replace(/\.pdf$/i, ''))

    const res = await curriculumsApi.generateFromPdf(fd)
    const data = res.data?.data ?? res.data
    genResultJson.value = JSON.stringify(data, null, 2)
    genOk.value = '생성 요청이 접수되었습니다. 아래 대기 목록에서 결과를 확인하세요.'
    await loadPendingCurricula()
  } catch (e) {
    genErr.value =
      e.response?.data?.message ||
      e.message ||
      '요청에 실패했습니다. 게이트웨이에 generate-from-pdf 엔드포인트가 있는지 확인하세요.'
  } finally {
    genLoading.value = false
  }
}

function normalizeListPayload(res) {
  const d = res.data?.data ?? res.data
  if (Array.isArray(d)) return d
  if (Array.isArray(d?.content)) return d.content
  if (Array.isArray(d?.items)) return d.items
  return []
}

function formatSummary(c) {
  const n = c.modules?.length ?? c.moduleCount
  if (n) return `모듈 ${n}개`
  return '요약 없음'
}

function formatDate(iso) {
  if (!iso) return ''
  try {
    const d = new Date(iso)
    return Number.isNaN(d.getTime()) ? String(iso) : d.toLocaleString('ko-KR')
  } catch {
    return String(iso)
  }
}

function badgeClass(status) {
  const s = (status || '').toUpperCase()
  if (s.includes('PENDING') || s === 'DRAFT') return 'badge-warn'
  if (s.includes('APPROVE')) return 'badge-ok'
  if (s.includes('REJECT')) return 'badge-bad'
  return 'badge-neutral'
}

async function loadPendingCurricula() {
  loadingList.value = true
  listErr.value = ''
  usedMockList.value = false
  selectedId.value = null
  resetDetail()
  try {
    const res = await curriculumsApi.list({ status: 'PENDING_APPROVAL' })
    let rows = normalizeListPayload(res)
    if (!rows.length) {
      const res2 = await curriculumsApi.list({ approvalStatus: 'PENDING' })
      rows = normalizeListPayload(res2)
    }
    curricula.value = rows
    if (!rows.length && auth.isDevPreview) {
      curricula.value = [...MOCK_PENDING_CURRICULA]
      usedMockList.value = true
    }
  } catch (e) {
    if (auth.isDevPreview) {
      curricula.value = [...MOCK_PENDING_CURRICULA]
      usedMockList.value = true
      listErr.value = ''
    } else {
      listErr.value = e.response?.data?.message || e.message || '목록을 불러오지 못했습니다.'
      curricula.value = []
    }
  } finally {
    loadingList.value = false
  }
}

function resetDetail() {
  detail.curriculumId = null
  detail.title = ''
  detail.status = ''
  detail.summary = ''
  detail.sourceType = ''
  detail.createdAt = ''
  detail.goalId = null
  detail.modules = []
  editMode.value = false
  draftTitle.value = ''
  draftModulesJson.value = ''
  editParseErr.value = ''
  actionErr.value = ''
  actionOk.value = ''
}

function applyDetailFromObject(obj) {
  detail.curriculumId = obj.curriculumId ?? obj.id
  detail.title = obj.title ?? ''
  detail.status = obj.status ?? ''
  detail.summary = obj.summary ?? ''
  detail.sourceType = obj.sourceType ?? ''
  detail.createdAt = obj.createdAt ?? ''
  detail.goalId = obj.goalId ?? null
  detail.modules = Array.isArray(obj.modules) ? [...obj.modules] : []
}

async function selectCurriculum(c) {
  const id = c.curriculumId ?? c.id
  if (id == null) return
  selectedId.value = id
  actionErr.value = ''
  actionOk.value = ''
  editMode.value = false
  applyDetailFromObject(c)
  loadingDetail.value = true
  try {
    const res = await curriculumsApi.get(id)
    const d = res.data?.data ?? res.data
    if (d && typeof d === 'object') {
      applyDetailFromObject({ ...c, ...d, curriculumId: d.curriculumId ?? d.id ?? id })
    }
  } catch {
    /* 목록에 모듈이 있으면 그대로 사용 */
    if (!detail.modules?.length && auth.isDevPreview) {
      const fromMock = MOCK_PENDING_CURRICULA.find((x) => String(x.curriculumId) === String(id))
      if (fromMock) applyDetailFromObject(fromMock)
    }
  } finally {
    loadingDetail.value = false
  }
}

function startEdit() {
  editMode.value = true
  draftTitle.value = detail.title
  draftModulesJson.value = JSON.stringify(detail.modules ?? [], null, 2)
  editParseErr.value = ''
}

function cancelEdit() {
  editMode.value = false
  editParseErr.value = ''
}

async function saveEdit() {
  editParseErr.value = ''
  let modules
  try {
    modules = JSON.parse(draftModulesJson.value || '[]')
  } catch {
    editParseErr.value = '모듈 JSON 형식이 올바르지 않습니다.'
    return
  }
  if (!Array.isArray(modules)) {
    editParseErr.value = '모듈은 배열이어야 합니다.'
    return
  }
  actionBusy.value = true
  actionErr.value = ''
  actionOk.value = ''
  const id = selectedId.value
  try {
    await curriculumsApi.update(id, { title: draftTitle.value, modules })
    detail.title = draftTitle.value
    detail.modules = modules
    const idx = curricula.value.findIndex((x) => String(x.curriculumId ?? x.id) === String(id))
    if (idx >= 0) {
      curricula.value[idx] = { ...curricula.value[idx], title: draftTitle.value, modules }
    }
    actionOk.value = '수정 사항이 저장되었습니다.'
    editMode.value = false
  } catch (e) {
    if (auth.isDevPreview) {
      detail.title = draftTitle.value
      detail.modules = modules
      const idx = curricula.value.findIndex((x) => String(x.curriculumId ?? x.id) === String(id))
      if (idx >= 0) {
        curricula.value[idx] = { ...curricula.value[idx], title: draftTitle.value, modules }
      }
      actionOk.value = '개발 미리보기: API 없이 로컬에만 반영했습니다.'
      editMode.value = false
    } else {
      actionErr.value = e.response?.data?.message || e.message || '저장에 실패했습니다.'
    }
  } finally {
    actionBusy.value = false
  }
}

async function doApprove() {
  await submitApproval('APPROVE')
}

async function doReject() {
  await submitApproval('REJECT')
}

async function submitApproval(action) {
  const id = selectedId.value
  if (id == null) return
  actionBusy.value = true
  actionErr.value = ''
  actionOk.value = ''
  try {
    await approvalsApi.approveCurriculum(id, { action, comment: currComment.value })
    actionOk.value = action === 'APPROVE' ? '승인 처리되었습니다.' : '반려 처리되었습니다.'
    if (auth.isDevPreview) {
      curricula.value = curricula.value.filter((x) => String(x.curriculumId ?? x.id) !== String(id))
      selectedId.value = null
      resetDetail()
    } else {
      await loadPendingCurricula()
      if (!curricula.value.some((x) => String(x.curriculumId ?? x.id) === String(id))) {
        selectedId.value = null
        resetDetail()
      }
    }
  } catch (e) {
    if (auth.isDevPreview) {
      actionOk.value = `개발 미리보기: ${action} 요청을 시뮬레이션했습니다.`
      curricula.value = curricula.value.filter((x) => String(x.curriculumId ?? x.id) !== String(id))
      selectedId.value = null
      resetDetail()
    } else {
      actionErr.value = e.response?.data?.message || e.message || '처리에 실패했습니다.'
    }
  } finally {
    actionBusy.value = false
  }
}

async function doDelete() {
  const id = selectedId.value
  if (id == null) return
  if (!window.confirm(`커리큘럼 ${id}를 삭제할까요? 이 작업은 되돌릴 수 없을 수 있습니다.`)) return
  actionBusy.value = true
  actionErr.value = ''
  actionOk.value = ''
  try {
    await curriculumsApi.remove(id)
    actionOk.value = '삭제되었습니다.'
    if (auth.isDevPreview) {
      curricula.value = curricula.value.filter((x) => String(x.curriculumId ?? x.id) !== String(id))
    } else {
      await loadPendingCurricula()
    }
    selectedId.value = null
    resetDetail()
  } catch (e) {
    if (auth.isDevPreview) {
      curricula.value = curricula.value.filter((x) => String(x.curriculumId ?? x.id) !== String(id))
      actionOk.value = '개발 미리보기: 목록에서 제거했습니다.'
      selectedId.value = null
      resetDetail()
    } else {
      actionErr.value = e.response?.data?.message || e.message || '삭제에 실패했습니다.'
    }
  } finally {
    actionBusy.value = false
  }
}

async function approveGoal() {
  err.value = ''
  try {
    await approvalsApi.approveGoal(goalId.value, { action: 'APPROVE', comment: goalComment.value })
  } catch (e) {
    err.value = e.response?.data?.message || e.message
  }
}

async function loadHistory() {
  err.value = ''
  historyJson.value = ''
  try {
    const res = await approvalsApi.list({
      resourceType: histType.value,
      resourceId: histResourceId.value
    })
    historyJson.value = JSON.stringify(res.data?.data ?? res.data, null, 2)
  } catch (e) {
    err.value = e.response?.data?.message || e.message
  }
}

onMounted(() => {
  loadPendingCurricula()
})
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
.flow-head {
  margin-bottom: 18px;
}
.flow-head .page-title {
  margin-bottom: 6px;
}
.flow-head .page-desc {
  margin: 0;
  max-width: 900px;
}
.page-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
  margin-bottom: 12px;
}
.page-title {
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: 8px;
}
.page-desc {
  font-size: 14px;
  color: var(--color-text-secondary);
  line-height: 1.55;
  max-width: 720px;
}
.page-desc code {
  font-size: 12px;
  background: var(--color-bg-tertiary);
  padding: 2px 6px;
  border-radius: 4px;
}

.create-panel {
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 20px;
  margin-bottom: 18px;
}
.create-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 8px;
}
.create-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}
.hint {
  font-size: 13px;
  color: var(--color-text-secondary);
  margin: 0 0 12px;
  line-height: 1.5;
}
.hint code {
  font-size: 12px;
  background: var(--color-bg-tertiary);
  padding: 2px 6px;
  border-radius: 4px;
}
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
.drop-zone {
  border: 2px dashed var(--color-border);
  border-radius: var(--radius-lg);
  padding: 18px 16px;
  text-align: center;
  cursor: pointer;
  background: var(--color-bg-secondary);
  transition: var(--transition);
  margin-bottom: 12px;
}
.drop-zone:hover:not(.disabled),
.drop-zone.dragging:not(.disabled) {
  border-color: var(--color-primary);
  background: var(--color-primary-light);
}
.drop-zone.disabled {
  cursor: wait;
  opacity: 0.9;
}
.drop-lead {
  font-size: 14px;
  color: var(--color-text-secondary);
  margin: 0;
}
.drop-file {
  margin: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}
.file-name {
  font-weight: 650;
  color: var(--color-text-primary);
  word-break: break-all;
}
.btn-text {
  border: none;
  background: none;
  color: var(--color-primary);
  font-size: 13px;
  font-weight: 650;
  cursor: pointer;
  text-decoration: underline;
}
.drop-status {
  margin: 10px 0 0;
  font-size: 13px;
  color: var(--color-primary);
}
.meta-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-top: 8px;
}
.meta-grid .span2 {
  grid-column: 1 / -1;
}
@media (max-width: 720px) {
  .meta-grid {
    grid-template-columns: 1fr;
  }
}
.mock-hint {
  font-size: 13px;
  color: var(--color-text-muted);
  margin-bottom: 12px;
}
.banner-err {
  margin-bottom: 12px;
}
.workspace {
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
.panel-title {
  font-size: 15px;
  font-weight: 700;
  margin: 0 0 12px;
}
.list-panel,
.detail-panel {
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 20px;
  min-height: 200px;
}
.card-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.cur-card {
  width: 100%;
  text-align: left;
  padding: 14px 16px;
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  background: var(--color-bg-secondary);
  cursor: pointer;
  transition: var(--transition);
}
.cur-card:hover {
  border-color: var(--color-border-hover);
}
.cur-card.selected {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 1px var(--color-primary);
  background: var(--color-primary-light);
}
.cur-card-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 6px;
}
.cur-title {
  font-weight: 600;
  font-size: 14px;
  color: var(--color-text-primary);
  line-height: 1.35;
}
.cur-summary {
  font-size: 13px;
  color: var(--color-text-secondary);
  margin: 0 0 8px;
  line-height: 1.4;
}
.cur-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
  font-size: 12px;
  color: var(--color-text-muted);
}
.meta-pill {
  background: var(--color-bg-tertiary);
  padding: 2px 8px;
  border-radius: 6px;
  font-weight: 500;
}
.badge {
  font-size: 11px;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 6px;
  flex-shrink: 0;
}
.badge-warn {
  background: var(--color-warning-light);
  color: var(--color-warning);
}
.badge-ok {
  background: var(--color-success-light, #dcfce7);
  color: var(--color-success, #15803d);
}
.badge-bad {
  background: var(--color-danger-light, #fee2e2);
  color: var(--color-danger);
}
.badge-neutral {
  background: var(--color-bg-tertiary);
  color: var(--color-text-secondary);
}
.empty {
  font-size: 14px;
  color: var(--color-text-muted);
  margin: 0;
}
.placeholder {
  font-size: 14px;
  color: var(--color-text-muted);
  margin: 24px 0;
  text-align: center;
  line-height: 1.5;
}
.detail-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}
.detail-head .panel-title {
  margin: 0;
  flex: 1;
  min-width: 0;
}
.sub {
  font-size: 14px;
  font-weight: 600;
  margin: 0 0 10px;
}
.modules {
  list-style: none;
  margin: 0;
  padding: 0;
}
.mod-row {
  display: flex;
  gap: 12px;
  padding: 10px 0;
  border-bottom: 1px solid var(--color-border);
  font-size: 14px;
}
.week {
  min-width: 56px;
  color: var(--color-text-muted);
  font-size: 13px;
}
.mod-title {
  color: var(--color-text-primary);
}
.comment-block {
  margin-top: 20px;
}
.form-label {
  display: block;
  font-size: 13px;
  margin-bottom: 6px;
}
.form-input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  margin-bottom: 10px;
  font-size: 14px;
}
.form-input.narrow {
  max-width: 280px;
}
.form-input.area {
  font-family: ui-monospace, monospace;
  font-size: 12px;
  resize: vertical;
}
.actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 16px;
}
.btn-sm {
  padding: 8px 16px;
  font-size: 13px;
}
.danger {
  color: var(--color-danger);
}
.muted {
  color: var(--color-text-muted);
  font-size: 14px;
}
.error {
  color: var(--color-danger);
  font-size: 14px;
}
.success {
  color: var(--color-success);
  font-size: 14px;
  margin-top: 8px;
}
.extra {
  margin-top: 32px;
  padding: 16px;
  border-radius: var(--radius-lg);
  border: 1px dashed var(--color-border);
  background: var(--color-bg-primary);
}
.extra summary {
  cursor: pointer;
  font-weight: 600;
  font-size: 14px;
  margin-bottom: 12px;
}
.card {
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 20px;
  margin-bottom: 16px;
}
.card:last-child {
  margin-bottom: 0;
}
.row {
  margin-top: 8px;
}
.pre {
  margin-top: 12px;
  padding: 12px;
  background: var(--color-bg-tertiary);
  border-radius: var(--radius-md);
  font-size: 12px;
  overflow: auto;
}
.footer-err {
  margin-top: 16px;
}
</style>
