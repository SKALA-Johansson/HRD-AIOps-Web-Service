<template>
  <div class="page">
    <AppHeader />
    <main class="main">
      <h1 class="page-title">커리큘럼 생성 및 사원 등록</h1>

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
          <button v-if="!loading" type="button" class="btn-text" @click.stop="clearFile">선택 취소</button>
        </p>
        <p v-if="loading" class="drop-status">사원 등록 및 커리큘럼 생성 중…</p>
      </section>

      <section class="card meta-card">
        <p class="meta-hint">사원 정보를 입력하세요. 비밀번호는 생년월일(6자리)로 설정됩니다.</p>
        <label class="form-label">사원 이름 <span class="required">*</span></label>
        <input v-model="form.name" class="form-input" placeholder="홍길동" :disabled="loading" required />
        <label class="form-label">사원번호 (아이디) <span class="required">*</span></label>
        <input v-model="form.username" class="form-input" placeholder="예: EMP001" :disabled="loading" required />
        <label class="form-label">생년월일 6자리 (비밀번호) <span class="required">*</span></label>
        <input v-model="form.birthDate" class="form-input" placeholder="예: 990101" maxlength="6" inputmode="numeric" :disabled="loading" required />
        <label class="form-label">부서 <span class="required">*</span></label>
        <select v-model="form.department" class="form-input" :disabled="loading" required>
          <option value="">선택</option>
          <option value="AI / 데이터 부서">AI / 데이터 부서</option>
          <option value="백엔드 개발 부서">백엔드 개발 부서</option>
          <option value="프론트엔드 개발 부서">프론트엔드 개발 부서</option>
          <option value="영업 부서">영업 부서</option>
        </select>
      </section>

      <div class="row">
        <button
          type="button"
          class="btn btn-primary"
          :disabled="loading || !selectedFile || !form.name || !form.username || !form.birthDate || !form.department"
          @click="runRegister"
        >
          {{ loading ? '등록 중…' : '사원 등록 및 커리큘럼 생성' }}
        </button>
      </div>

      <p v-if="successMsg" class="success">{{ successMsg }}</p>
      <p v-if="err" class="error">{{ err }}</p>
      <pre v-if="resultJson" class="pre">{{ resultJson }}</pre>
    </main>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import AppHeader from '@/components/AppHeader.vue'
import { profilesApi } from '@/api/profiles.js'

const fileInput = ref(null)
const dragOver = ref(false)
const loading = ref(false)
const selectedFile = ref(null)
const selectedName = ref('')
const successMsg = ref('')
const err = ref('')
const resultJson = ref('')

const form = reactive({
  name: '',
  username: '',
  birthDate: '',
  department: ''
})

function clearFile() {
  selectedFile.value = null
  selectedName.value = ''
  if (fileInput.value) fileInput.value.value = ''
  successMsg.value = ''
  err.value = ''
  resultJson.value = ''
}

function pickPdf(file) {
  if (!file) return
  const ok = file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf')
  if (!ok) { err.value = 'PDF 파일만 업로드할 수 있습니다.'; return }
  err.value = ''
  successMsg.value = ''
  resultJson.value = ''
  selectedFile.value = file
  selectedName.value = file.name
}

function onFileInput(e) { pickPdf(e.target?.files?.[0]) }
function onDrop(e) { dragOver.value = false; pickPdf(e.dataTransfer?.files?.[0]) }

async function runRegister() {
  const file = selectedFile.value
  if (!file || loading.value) return
  loading.value = true
  err.value = ''
  successMsg.value = ''
  resultJson.value = ''

  const fd = new FormData()
  fd.append('file', file)
  fd.append('name', form.name.trim())
  fd.append('username', form.username.trim())
  fd.append('birthDate', form.birthDate.trim())
  fd.append('department', form.department)

  try {
    const res = await profilesApi.register(fd)
    const data = res.data?.data ?? res.data
    resultJson.value = JSON.stringify(data, null, 2)
    if (data?.curriculumRequested) {
      successMsg.value = '사원 등록이 완료되었습니다. 보유 역량을 반영해 커리큘럼 생성을 시작했습니다.'
    } else {
      err.value = '사원 등록은 완료됐지만 커리큘럼 생성 요청에 실패했습니다. 잠시 후 다시 시도해 주세요.'
    }
  } catch (e) {
    err.value = '사원 등록에 실패했습니다. 잠시 후 다시 시도해 주세요.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.page { min-height: 100vh; background: var(--color-bg-secondary); }
.main { max-width: 640px; margin: 0 auto; padding: 28px 24px 64px; }
.page-title { font-size: 1.5rem; font-weight: 700; margin-bottom: 20px; }
.sr-only { position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px; overflow: hidden; clip: rect(0,0,0,0); white-space: nowrap; border: 0; }
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
.drop-zone:hover:not(.disabled), .drop-zone.dragging:not(.disabled) { border-color: var(--color-primary); background: var(--color-primary-light); }
.drop-zone.disabled { cursor: wait; opacity: 0.85; }
.drop-lead { font-size: 15px; color: var(--color-text-secondary); margin: 0; }
.drop-file { margin: 0; display: flex; flex-direction: column; align-items: center; gap: 8px; }
.file-name { font-weight: 600; color: var(--color-text-primary); word-break: break-all; }
.btn-text { border: none; background: none; color: var(--color-primary); font-size: 13px; font-weight: 600; cursor: pointer; text-decoration: underline; }
.drop-status { margin: 12px 0 0; font-size: 13px; color: var(--color-primary); }
.row { display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 16px; }
.card { background: var(--color-bg-primary); border: 1px solid var(--color-border); border-radius: var(--radius-lg); padding: 20px; }
.meta-card { margin-bottom: 16px; }
.meta-hint { font-size: 13px; color: var(--color-text-secondary); margin: 0 0 12px; }
.form-label { display: block; font-size: 13px; margin-bottom: 6px; }
.required { color: var(--color-danger); }
.form-input { width: 100%; padding: 10px 12px; border: 1px solid var(--color-border); border-radius: var(--radius-md); margin-bottom: 14px; font-size: 14px; }
.success { color: var(--color-success); margin-bottom: 8px; font-size: 14px; }
.error { color: var(--color-danger); margin-bottom: 8px; font-size: 14px; }
.pre { margin-top: 12px; padding: 12px; background: var(--color-bg-tertiary); border-radius: var(--radius-md); font-size: 12px; overflow: auto; max-height: 280px; }
</style>
