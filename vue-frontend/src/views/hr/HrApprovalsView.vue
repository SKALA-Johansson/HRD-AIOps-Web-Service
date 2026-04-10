<template>
  <div class="page">
    <AppHeader />
    <main class="main">
      <section v-if="mode === 'create'" class="panel">
        <header class="head">
          <div>
            <h1 class="page-title">PDF로 커리큘럼 생성</h1>
            <p class="page-desc">
              사원 정보를 입력하고 PDF를 업로드한 뒤 <strong>커리큘럼 생성</strong>을 누르면 생성 요청이 전송되고, 곧바로
              <strong>승인/삭제</strong> 화면으로 전환됩니다. (<code>POST /curriculums/generate-from-pdf</code>)
            </p>
          </div>
          <button
            type="button"
            class="btn btn-primary btn-sm"
            :disabled="genLoading || !genSelectedFile"
            @click="runGenerateFromPdf"
          >
            {{ genLoading ? '생성 중…' : '커리큘럼 생성' }}
          </button>
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
            <input
              v-model="genMeta.employeeNo"
              class="form-input"
              :disabled="genLoading"
              inputmode="numeric"
              placeholder="예: 20260001"
            />
          </div>
          <div>
            <label class="form-label">생년월일(6자리)</label>
            <input
              v-model="genMeta.birthDate6"
              class="form-input"
              :disabled="genLoading"
              inputmode="numeric"
              placeholder="예: 990101"
            />
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

      <section v-else class="panel">
        <header class="head">
          <div>
            <h1 class="page-title">커리큘럼 승인</h1>
            <p class="page-desc">
              생성된 커리큘럼을 확인하고 <strong>승인</strong> 또는 <strong>삭제</strong>를 결정합니다.
              (<code>POST /approvals/curriculums/{id}</code>, <code>DELETE /curriculums/{id}</code>)
            </p>
          </div>
          <div class="actions">
            <button type="button" class="btn btn-outline btn-sm" :disabled="actionBusy" @click="backToCreate">
              다른 PDF로 생성
            </button>
            <button type="button" class="btn btn-primary btn-sm" :disabled="actionBusy" @click="doApprove">승인</button>
            <button type="button" class="btn btn-ghost btn-sm danger" :disabled="actionBusy" @click="doDelete">
              삭제
            </button>
          </div>
        </header>

        <div v-if="loadingDetail" class="muted">불러오는 중…</div>
        <p v-if="actionErr" class="error">{{ actionErr }}</p>
        <p v-if="actionOk" class="success">{{ actionOk }}</p>

        <div v-if="!loadingDetail" class="card">
          <p class="meta">
            curriculumId: <strong>{{ detail.curriculumId }}</strong>
            <span v-if="detail.status">/ status: {{ detail.status }}</span>
          </p>
          <h2 class="title">{{ detail.title || '커리큘럼' }}</h2>
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
import { reactive, ref } from 'vue'
import AppHeader from '@/components/AppHeader.vue'
import { approvalsApi } from '@/api/approvals.js'
import { curriculumsApi } from '@/api/curriculums.js'
import { useAuthStore } from '@/store/auth.js'
import { MOCK_PENDING_CURRICULA } from '@/data/devMock.js'

const auth = useAuthStore()

const mode = ref('create') // 'create' | 'review'

const genFileInput = ref(null)
const genDragOver = ref(false)
const genLoading = ref(false)
const genSelectedFile = ref(null)
const genSelectedName = ref('')
const genErr = ref('')
const genOk = ref('')
const genMeta = reactive({
  name: '',
  employeeNo: '',
  birthDate6: '',
  department: ''
})

const selectedId = ref(null)
const loadingDetail = ref(false)
const detail = reactive({
  curriculumId: null,
  title: '',
  status: '',
  goalId: null,
  modules: []
})

const currComment = ref('검토 완료')
const actionBusy = ref(false)
const actionErr = ref('')
const actionOk = ref('')

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
  if (!ok) {
    genErr.value = 'PDF 파일만 업로드할 수 있습니다.'
    return
  }
  genErr.value = ''
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

function resetDetail() {
  selectedId.value = null
  detail.curriculumId = null
  detail.title = ''
  detail.status = ''
  detail.goalId = null
  detail.modules = []
  actionErr.value = ''
  actionOk.value = ''
}

function applyDetailFromObject(obj) {
  detail.curriculumId = obj.curriculumId ?? obj.id ?? selectedId.value
  detail.title = obj.title ?? ''
  detail.status = obj.status ?? ''
  detail.goalId = obj.goalId ?? null
  detail.modules = Array.isArray(obj.modules) ? [...obj.modules] : []
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
    if (d && typeof d === 'object') applyDetailFromObject(d)
  } catch {
    if (auth.isDevPreview) {
      const fromMock = MOCK_PENDING_CURRICULA.find((x) => String(x.curriculumId) === String(id))
      if (fromMock) {
        applyDetailFromObject(fromMock)
      } else {
        applyDetailFromObject({
          curriculumId: id,
          title: `더미 커리큘럼 #${id} (개발 미리보기)`,
          status: 'PENDING_APPROVAL',
          modules: [
            { moduleId: 9001, week: 1, title: '오리엔테이션 · 환경 설정' },
            { moduleId: 9002, week: 2, title: '기초 실습 · 과제' },
            { moduleId: 9003, week: 3, title: '심화 · 미니 프로젝트' }
          ]
        })
      }
    }
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
      .filter(Boolean)
      .join(' ')
      .trim()
    fd.append('title', autoTitle || file.name.replace(/\.pdf$/i, ''))

    const res = await curriculumsApi.generateFromPdf(fd)
    const data = res.data?.data ?? res.data
    const id = data?.curriculumId ?? data?.id ?? data?.curriculum?.curriculumId ?? data?.curriculum?.id
    if (id == null) throw new Error('응답에 curriculumId가 없습니다.')

    resetDetail()
    mode.value = 'review'
    await loadDetailById(id)
  } catch (e) {
    if (auth.isDevPreview) {
      genOk.value = '개발 미리보기: 생성 요청을 시뮬레이션했습니다. (승인 화면으로 전환)'
      resetDetail()
      mode.value = 'review'
      await loadDetailById(401)
    } else {
      genErr.value =
        e.response?.data?.message ||
        e.message ||
        '요청에 실패했습니다. 게이트웨이에 generate-from-pdf 엔드포인트가 있는지 확인하세요.'
    }
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
    await approvalsApi.approveCurriculum(id, { action: 'APPROVE', comment: currComment.value || '' })
    actionOk.value = '승인 처리되었습니다.'
  } catch (e) {
    if (auth.isDevPreview) actionOk.value = '개발 미리보기: 승인 처리 시뮬레이션'
    else actionErr.value = e.response?.data?.message || e.message || '승인에 실패했습니다.'
  } finally {
    actionBusy.value = false
  }
}

async function doDelete() {
  const id = selectedId.value
  if (id == null) return
  if (!window.confirm(`커리큘럼 ${id}를 삭제할까요?`)) return
  actionBusy.value = true
  actionErr.value = ''
  actionOk.value = ''
  try {
    await curriculumsApi.remove(id)
    actionOk.value = '삭제되었습니다.'
    backToCreate()
  } catch (e) {
    if (auth.isDevPreview) {
      actionOk.value = '개발 미리보기: 삭제 처리 시뮬레이션'
      backToCreate()
    } else {
      actionErr.value = e.response?.data?.message || e.message || '삭제에 실패했습니다.'
    }
  } finally {
    actionBusy.value = false
  }
}

function backToCreate() {
  mode.value = 'create'
  clearGenFile()
  resetDetail()
}
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: var(--color-bg-secondary);
}
.main {
  max-width: 980px;
  margin: 0 auto;
  padding: 28px 24px 64px;
}
.panel {
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 22px;
}
.head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 12px;
}
.actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}
.page-title {
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0 0 6px;
}
.page-desc {
  font-size: 14px;
  color: var(--color-text-secondary);
  line-height: 1.55;
  margin: 0;
  max-width: 860px;
}
.page-desc code {
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
  margin: 14px 0 12px;
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
  font-size: 14px;
}
.comment-block {
  margin-top: 16px;
}
.card {
  margin-top: 14px;
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 18px;
}
.meta {
  font-size: 13px;
  color: var(--color-text-muted);
  margin: 0 0 8px;
}
.title {
  font-size: 1.1rem;
  font-weight: 800;
  margin: 0 0 12px;
}
.sub {
  font-size: 14px;
  font-weight: 700;
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
  font-weight: 650;
}
.success {
  color: var(--color-success);
  margin-top: 10px;
}
.error {
  color: var(--color-danger);
  margin-top: 10px;
}
.muted {
  color: var(--color-text-muted);
  margin-top: 10px;
}
</style>

