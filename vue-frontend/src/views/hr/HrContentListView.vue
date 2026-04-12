<template>
  <div class="page">
    <AppHeader />
    <main class="main">
      <div class="head-row">
        <div>
          <h1 class="page-title">교육 콘텐츠 관리</h1>
        </div>
      </div>

      <section class="upload-card" aria-label="필수 교육 자료 업로드">
        <div class="upload-head">
          <div>
            <h2 class="upload-title">필수 교육 자료 업로드 (PDF)</h2>
            <p class="upload-desc">PDF를 선택한 뒤 <strong>업로드</strong>를 누르면 업로드 요청을 전송합니다.</p>
          </div>
          <div class="upload-actions">
            <button type="button" class="btn btn-outline btn-sm" :disabled="uploading" @click="clearUpload">초기화</button>
            <button type="button" class="btn btn-primary btn-sm" :disabled="uploading || !selectedFile" @click="submitUpload">
              {{ uploading ? '업로드 중…' : '업로드' }}
            </button>
          </div>
        </div>

        <div class="upload-grid">
          <div class="span2">
            <label class="form-label">PDF 파일</label>
            <div class="file-row">
              <input ref="fileInput" type="file" accept=".pdf,application/pdf" class="sr-only" :disabled="uploading" @change="onFileInput" />
              <button type="button" class="btn btn-outline btn-sm" :disabled="uploading" @click="fileInput?.click()">파일 선택</button>
              <span class="file-name">{{ selectedFile ? selectedFile.name : '선택된 파일 없음' }}</span>
            </div>
          </div>
        </div>

        <p v-if="uploadOk" class="success">{{ uploadOk }}</p>
        <p v-if="uploadErr" class="error">{{ uploadErr }}</p>
      </section>

      <div v-if="loading" class="muted">불러오는 중…</div>
      <p v-else-if="error" class="error">{{ error }}</p>
      <table v-else class="table">
        <thead>
          <tr>
            <th>ID</th>
            <th>제목</th>
            <th>유형</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in rows" :key="row.contentId">
            <td>{{ row.contentId }}</td>
            <td>{{ row.title }}</td>
            <td>{{ row.type }}</td>
            <td>
              <router-link :to="`/hr/contents/${row.contentId}/edit`" class="link">수정</router-link>
            </td>
          </tr>
          <tr v-if="!rows.length">
            <td colspan="4" class="muted">등록된 콘텐츠가 없습니다.</td>
          </tr>
        </tbody>
      </table>
    </main>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import AppHeader from '@/components/AppHeader.vue'
import { contentsApi } from '@/api/contents.js'

const fileInput = ref(null)
const selectedFile = ref(null)
const uploading = ref(false)
const uploadErr = ref('')
const uploadOk = ref('')

const loading = ref(false)
const error = ref('')
const rows = ref([])

function clearUpload() {
  selectedFile.value = null
  uploadErr.value = ''
  uploadOk.value = ''
  if (fileInput.value) fileInput.value.value = ''
}

function onFileInput(e) {
  const f = e.target?.files?.[0]
  if (!f) return
  const ok = f.type === 'application/pdf' || f.name.toLowerCase().endsWith('.pdf')
  if (!ok) { uploadErr.value = 'PDF 파일만 업로드할 수 있습니다.'; return }
  uploadErr.value = ''
  uploadOk.value = ''
  selectedFile.value = f
}

async function submitUpload() {
  const file = selectedFile.value
  if (!file || uploading.value) return
  uploading.value = true
  uploadErr.value = ''
  uploadOk.value = ''
  try {
    const fd = new FormData()
    fd.append('file', file)
    await contentsApi.uploadDepartmentRequiredPdf(fd)
    uploadOk.value = '업로드가 완료되었습니다.'
    clearUpload()
    await load()
  } catch (e) {
    uploadErr.value = '업로드에 실패했습니다. 잠시 후 다시 시도해 주세요.'
  } finally {
    uploading.value = false
  }
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const res = await contentsApi.list({})
    const d = res.data?.data
    rows.value = Array.isArray(d) ? d : d ? [d] : []
  } catch (e) {
    error.value = '콘텐츠 목록을 불러오지 못했습니다.'
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.page { min-height: 100vh; background: var(--color-bg-secondary); }
.sr-only { position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px; overflow: hidden; clip: rect(0,0,0,0); white-space: nowrap; border: 0; }
.main { max-width: 960px; margin: 0 auto; padding: 28px 24px 64px; }
.head-row { display: flex; justify-content: space-between; align-items: flex-start; gap: 16px; margin-bottom: 8px; }
.page-title { font-size: 1.5rem; font-weight: 700; margin-bottom: 8px; }
.upload-card { background: var(--color-bg-primary); border: 1px solid var(--color-border); border-radius: var(--radius-lg); padding: 16px; margin-top: 16px; margin-bottom: 20px; }
.upload-head { display: flex; justify-content: space-between; align-items: flex-start; gap: 16px; margin-bottom: 12px; }
.upload-title { font-size: 1.05rem; font-weight: 700; margin: 0 0 6px; }
.upload-desc { margin: 0; font-size: 13px; color: var(--color-text-secondary); line-height: 1.4; }
.upload-actions { display: flex; gap: 10px; flex-wrap: wrap; }
.upload-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 10px; }
.span2 { grid-column: 1 / -1; }
.file-row { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.file-name { font-size: 13px; color: var(--color-text-secondary); }
.form-label { display: block; font-size: 13px; margin-bottom: 6px; }
.btn-sm { padding: 10px 16px; font-size: 13px; }
.table { width: 100%; border-collapse: collapse; background: var(--color-bg-primary); border: 1px solid var(--color-border); border-radius: var(--radius-md); overflow: hidden; }
th, td { padding: 12px 14px; text-align: left; border-bottom: 1px solid var(--color-border); font-size: 14px; }
th { background: var(--color-bg-tertiary); font-weight: 600; }
.link { color: var(--color-primary); font-weight: 500; }
.muted { color: var(--color-text-muted); }
.error { color: var(--color-danger); margin-top: 8px; }
.success { color: var(--color-success); margin-top: 8px; }
</style>
