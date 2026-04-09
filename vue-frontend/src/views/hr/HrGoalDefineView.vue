<template>
  <div class="page">
    <AppHeader />
    <main class="main">
      <h1 class="page-title">PDF로 커리큘럼 생성</h1>
      <p class="page-desc">
        교안 PDF를 선택한 뒤 <strong>생성 버튼</strong>을 누르면 커리큘럼 생성 요청이 전송됩니다. 게이트웨이:
        <code>POST /api/v1/curriculums/generate-from-pdf</code> (multipart, 필드명
        <code>file</code>)
      </p>

      <section
        class="drop-zone"
        :class="{ dragging: dragOver, disabled: loading }"
        @dragenter.prevent="dragOver = true"
        @dragover.prevent="dragOver = true"
        @dragleave.prevent="dragOver = false"
        @drop.prevent="onDrop"
        @click="!loading && fileInput?.click()"
      >
        <input
          ref="fileInput"
          type="file"
          accept=".pdf,application/pdf"
          class="sr-only"
          :disabled="loading"
          @change="onFileInput"
        />
        <p v-if="!selectedName" class="drop-lead">PDF를 끌어다 놓거나 이 영역을 클릭하세요</p>
        <p v-else class="drop-file">
          <span class="file-name">{{ selectedName }}</span>
          <button
            v-if="!loading"
            type="button"
            class="btn-text"
            @click.stop="clearFile"
          >
            선택 취소
          </button>
        </p>
        <p v-if="loading" class="drop-status">커리큘럼 생성 중… (PDF 크기에 따라 수십 초 걸릴 수 있습니다)</p>
      </section>

      <div class="row">
        <button
          type="button"
          class="btn btn-primary"
          :disabled="loading || !selectedFile"
          @click="runGenerate"
        >
          {{ loading ? '생성 중…' : '커리큘럼 생성' }}
        </button>
      </div>

      <section class="card meta-card">
        <p class="meta-hint">선택 사항 — 백엔드에서 메타데이터로 쓸 수 있습니다.</p>
        <label class="form-label">계열사 (company)</label>
        <input v-model="meta.company" class="form-input" :disabled="loading" />
        <label class="form-label">직무군 (jobFamily)</label>
        <input v-model="meta.jobFamily" class="form-input" :disabled="loading" />
        <label class="form-label">커리큘럼 제목 힌트 (title)</label>
        <input
          v-model="meta.title"
          class="form-input"
          placeholder="비우면 파일명을 사용합니다"
          :disabled="loading"
        />
      </section>

      <p v-if="successMsg" class="success">{{ successMsg }}</p>
      <p v-if="err" class="error">{{ err }}</p>
      <pre v-if="resultJson" class="pre">{{ resultJson }}</pre>

      <p v-if="curriculumIdHint" class="next-step">
        승인 절차가 있다면
        <router-link to="/hr/curriculums" class="link">커리큘럼</router-link> 화면에서 진행할 수 있습니다.
        (응답에 포함된 ID: <code>{{ curriculumIdHint }}</code>)
      </p>
    </main>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import AppHeader from '@/components/AppHeader.vue'
import { curriculumsApi } from '@/api/curriculums.js'

const fileInput = ref(null)
const dragOver = ref(false)
const loading = ref(false)
const selectedFile = ref(null)
const selectedName = ref('')
const successMsg = ref('')
const err = ref('')
const resultJson = ref('')
const curriculumIdHint = ref('')

const meta = reactive({
  company: 'SK hynix',
  jobFamily: 'Backend',
  title: ''
})

function clearFile() {
  selectedFile.value = null
  selectedName.value = ''
  if (fileInput.value) fileInput.value.value = ''
  successMsg.value = ''
  err.value = ''
  resultJson.value = ''
  curriculumIdHint.value = ''
}

function pickPdf(file) {
  if (!file) return
  const ok =
    file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf')
  if (!ok) {
    err.value = 'PDF 파일만 업로드할 수 있습니다.'
    return
  }
  err.value = ''
  successMsg.value = ''
  resultJson.value = ''
  curriculumIdHint.value = ''
  selectedFile.value = file
  selectedName.value = file.name
}

function onFileInput(e) {
  const f = e.target?.files?.[0]
  pickPdf(f)
}

function onDrop(e) {
  dragOver.value = false
  const f = e.dataTransfer?.files?.[0]
  pickPdf(f)
}

async function runGenerate() {
  const file = selectedFile.value
  if (!file || loading.value) return
  loading.value = true
  err.value = ''
  successMsg.value = ''
  resultJson.value = ''
  curriculumIdHint.value = ''

  const fd = new FormData()
  fd.append('file', file)
  if (meta.company.trim()) fd.append('company', meta.company.trim())
  if (meta.jobFamily.trim()) fd.append('jobFamily', meta.jobFamily.trim())
  const t = meta.title.trim()
  fd.append('title', t || file.name.replace(/\.pdf$/i, ''))

  try {
    const res = await curriculumsApi.generateFromPdf(fd)
    const data = res.data?.data ?? res.data
    resultJson.value = JSON.stringify(data, null, 2)
    successMsg.value = '커리큘럼 생성 요청이 완료되었습니다.'
    const id =
      data?.curriculumId ??
      data?.id ??
      data?.curriculum?.curriculumId ??
      data?.curriculum?.id
    if (id != null) curriculumIdHint.value = String(id)
  } catch (e) {
    err.value =
      e.response?.data?.message ||
      e.message ||
      '요청에 실패했습니다. 게이트웨이에 generate-from-pdf 엔드포인트가 있는지 확인하세요.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: var(--color-bg-secondary);
}
.main {
  max-width: 640px;
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
  line-height: 1.5;
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
  padding: 28px 20px;
  text-align: center;
  cursor: pointer;
  background: var(--color-bg-primary);
  transition: var(--transition);
  margin-bottom: 20px;
}
.drop-zone:hover:not(.disabled),
.drop-zone.dragging:not(.disabled) {
  border-color: var(--color-primary);
  background: var(--color-primary-light);
}
.drop-zone.disabled {
  cursor: wait;
  opacity: 0.85;
}
.drop-lead {
  font-size: 15px;
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
  font-weight: 600;
  color: var(--color-text-primary);
  word-break: break-all;
}
.btn-text {
  border: none;
  background: none;
  color: var(--color-primary);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  text-decoration: underline;
}
.drop-status {
  margin: 12px 0 0;
  font-size: 13px;
  color: var(--color-primary);
}
.row {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}
.card {
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 20px;
}
.meta-card {
  margin-bottom: 16px;
}
.meta-hint {
  font-size: 13px;
  color: var(--color-text-secondary);
  margin: 0 0 12px;
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
  margin-bottom: 14px;
  font-size: 14px;
}
.success {
  color: var(--color-success);
  margin-bottom: 8px;
  font-size: 14px;
}
.error {
  color: var(--color-danger);
  margin-bottom: 8px;
  font-size: 14px;
}
.pre {
  margin-top: 12px;
  padding: 12px;
  background: var(--color-bg-tertiary);
  border-radius: var(--radius-md);
  font-size: 12px;
  overflow: auto;
  max-height: 280px;
}
.next-step {
  margin-top: 16px;
  font-size: 13px;
  color: var(--color-text-secondary);
  line-height: 1.5;
}
.next-step .link {
  color: var(--color-primary);
  font-weight: 600;
}
.next-step code {
  font-size: 12px;
}
</style>
