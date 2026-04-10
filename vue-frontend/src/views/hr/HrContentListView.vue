<template>
  <div class="page">
    <AppHeader />
    <main class="main">
      <div class="head-row">
        <div>
          <h1 class="page-title">교육 콘텐츠 관리</h1>
          <p class="page-desc">GET <code>/contents</code> — Content Management Service</p>
        </div>
      </div>

      <section class="upload-card" aria-label="필수 교육 자료 업로드">
        <div class="upload-head">
          <div>
            <h2 class="upload-title">필수 교육 자료 업로드 (PDF)</h2>
            <p class="upload-desc">
              PDF를 선택한 뒤 <strong>업로드</strong>를 누르면 업로드 요청을 전송합니다.
            </p>
          </div>
          <div class="upload-actions">
            <button type="button" class="btn btn-outline btn-sm" :disabled="uploading" @click="clearUpload">
              초기화
            </button>
            <button
              type="button"
              class="btn btn-primary btn-sm"
              :disabled="uploading || !selectedFile"
              @click="submitUpload"
            >
              {{ uploading ? '업로드 중…' : '업로드' }}
            </button>
          </div>
        </div>

        <div class="upload-grid">
          <div class="span2">
            <label class="form-label">PDF 파일</label>
            <div class="file-row">
              <input
                ref="fileInput"
                type="file"
                accept=".pdf,application/pdf"
                class="sr-only"
                :disabled="uploading"
                @change="onFileInput"
              />
              <button type="button" class="btn btn-outline btn-sm" :disabled="uploading" @click="fileInput?.click()">
                파일 선택
              </button>
              <span class="file-name">{{ selectedFile ? selectedFile.name : '선택된 파일 없음' }}</span>
            </div>
          </div>
        </div>

        <p v-if="uploadOk" class="success">{{ uploadOk }}</p>
        <p v-if="uploadErr" class="error">{{ uploadErr }}</p>
        <p v-if="usedMockUpload" class="mock-hint">개발 미리보기: 업로드는 세션에만 저장되었습니다.</p>

        <details v-if="mockItems.length" class="mock-list">
          <summary>업로드 기록 (이 브라우저 세션)</summary>
          <ul class="mock-ul">
            <li v-for="it in mockItems" :key="it.id" class="mock-li">
              <span class="mock-file">{{ it.fileName }}</span>
              <span class="mock-date">{{ it.uploadedAt }}</span>
            </li>
          </ul>
        </details>
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
            <td colspan="4" class="muted">데이터 없음 (백엔드 응답 형식에 맞게 조정)</td>
          </tr>
        </tbody>
      </table>
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import AppHeader from '@/components/AppHeader.vue'
import { contentsApi } from '@/api/contents.js'
import { useAuthStore } from '@/store/auth.js'

const auth = useAuthStore()

const UPLOAD_KEY = 'shrd_required_pdfs_v1'

const fileInput = ref(null)
const selectedFile = ref(null)
const uploading = ref(false)
const uploadErr = ref('')
const uploadOk = ref('')
const usedMockUpload = ref(false)

const mockItems = computed(() => {
  try {
    const raw = sessionStorage.getItem(UPLOAD_KEY)
    const parsed = raw ? JSON.parse(raw) : []
    return Array.isArray(parsed) ? parsed : []
  } catch {
    return []
  }
})

const loading = ref(false)
const error = ref('')
const rows = ref([])

function clearUpload() {
  selectedFile.value = null
  uploadErr.value = ''
  uploadOk.value = ''
  usedMockUpload.value = false
  if (fileInput.value) fileInput.value.value = ''
}

function onFileInput(e) {
  const f = e.target?.files?.[0]
  if (!f) return
  const ok = f.type === 'application/pdf' || f.name.toLowerCase().endsWith('.pdf')
  if (!ok) {
    uploadErr.value = 'PDF 파일만 업로드할 수 있습니다.'
    return
  }
  uploadErr.value = ''
  uploadOk.value = ''
  usedMockUpload.value = false
  selectedFile.value = f
}

function writeMockUpload(item) {
  const all = mockItems.value.slice()
  all.unshift(item)
  sessionStorage.setItem(UPLOAD_KEY, JSON.stringify(all.slice(0, 20)))
}

async function submitUpload() {
  const file = selectedFile.value
  if (!file || uploading.value) return
  uploading.value = true
  uploadErr.value = ''
  uploadOk.value = ''
  usedMockUpload.value = false
  try {
    const fd = new FormData()
    fd.append('file', file)
    await contentsApi.uploadDepartmentRequiredPdf(fd)
    uploadOk.value = '업로드가 완료되었습니다.'
    clearUpload()
  } catch (e) {
    if (auth.isDevPreview) {
      usedMockUpload.value = true
      writeMockUpload({
        id: `${Date.now()}_${Math.random().toString(16).slice(2)}`,
        fileName: file.name,
        uploadedAt: new Date().toLocaleString('ko-KR')
      })
      uploadOk.value = '개발 미리보기: 업로드가 완료된 것으로 처리했습니다.'
      clearUpload()
    } else {
      uploadErr.value =
        e.response?.data?.message ||
        e.message ||
        '업로드에 실패했습니다. 백엔드 업로드 API 연결이 필요합니다.'
    }
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
    error.value = e.response?.data?.message || e.message || '조회 실패'
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: var(--color-bg-secondary);
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
.main {
  max-width: 960px;
  margin: 0 auto;
  padding: 28px 24px 64px;
}
.head-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 8px;
}
.page-title {
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: 8px;
}
.page-desc {
  font-size: 14px;
  color: var(--color-text-secondary);
}
.page-desc code {
  font-size: 12px;
  background: var(--color-bg-tertiary);
  padding: 2px 6px;
  border-radius: 4px;
}
.upload-card {
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 16px;
  margin-top: 16px;
}
.upload-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 12px;
}
.upload-title {
  font-size: 1.05rem;
  font-weight: 700;
  margin: 0 0 6px;
}
.upload-desc {
  margin: 0;
  font-size: 13px;
  color: var(--color-text-secondary);
  line-height: 1.4;
}
.upload-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}
.upload-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-top: 10px;
}
.span2 {
  grid-column: 1 / -1;
}
.file-row {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}
.file-name {
  font-size: 13px;
  color: var(--color-text-secondary);
}
.mock-hint {
  margin-top: 6px;
  font-size: 12px;
  color: var(--color-text-muted);
}
.mock-list {
  margin-top: 10px;
}
.mock-ul {
  margin: 10px 0 0;
  padding: 0;
  list-style: none;
  display: grid;
  gap: 8px;
}
.mock-li {
  display: flex;
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
  font-size: 13px;
  color: var(--color-text-secondary);
}
.mock-pill {
  padding: 2px 8px;
  border-radius: 999px;
  border: 1px solid var(--color-border);
  background: var(--color-bg-tertiary);
  color: var(--color-text-primary);
  font-weight: 600;
  font-size: 12px;
}
.mock-file {
  color: var(--color-text-primary);
}
.mock-date {
  color: var(--color-text-muted);
  font-size: 12px;
}
.filters {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin: 20px 0;
}
.form-input {
  padding: 10px 12px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  width: 200px;
  font-size: 14px;
}
.btn-sm {
  padding: 10px 16px;
  font-size: 13px;
}
.table {
  width: 100%;
  border-collapse: collapse;
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  overflow: hidden;
}
th,
td {
  padding: 12px 14px;
  text-align: left;
  border-bottom: 1px solid var(--color-border);
  font-size: 14px;
}
th {
  background: var(--color-bg-tertiary);
  font-weight: 600;
}
.link {
  color: var(--color-primary);
  font-weight: 500;
}
.muted {
  color: var(--color-text-muted);
}
.error {
  color: var(--color-danger);
}
</style>
