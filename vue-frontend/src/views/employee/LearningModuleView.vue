<template>
  <div class="page">
    <AppHeader />
    <main class="main">
      <h1 class="page-title">모듈 학습 콘텐츠</h1>
      <p class="page-desc">
        모듈 ID: <strong>{{ moduleId }}</strong> — GET
        <code>/learning/modules/{moduleId}/contents</code>
      </p>

      <p v-if="usedMock" class="mock-hint">개발 미리보기: 콘텐츠는 더미입니다.</p>
      <div v-if="loading" class="muted">불러오는 중…</div>
      <p v-else-if="error" class="error">{{ error }}</p>
      <ul v-else class="content-list">
        <li v-for="item in contents" :key="item.contentId" class="content-row">
          <div>
            <span class="title">{{ item.title }}</span>
            <span class="badge badge-gray">{{ item.type }}</span>
          </div>
          <a v-if="item.url" :href="item.url" target="_blank" rel="noopener" class="btn btn-outline btn-sm">열기</a>
        </li>
        <li v-if="!contents.length" class="muted">콘텐츠가 없습니다.</li>
      </ul>

      <section class="card">
        <h2 class="sub-title">과제 제출</h2>
        <p class="hint">POST <code>/learning/assignments/{assignmentId}/submissions</code></p>
        <label class="form-label">assignmentId</label>
        <input v-model="assignmentId" class="form-input" placeholder="예: 501" />
        <label class="form-label">답안 텍스트</label>
        <textarea v-model="answerText" class="form-input area" rows="4" />
        <button type="button" class="btn btn-primary" :disabled="submitting" @click="submit">
          {{ submitting ? '제출 중…' : '제출' }}
        </button>
        <p v-if="formError" class="error">{{ formError }}</p>
        <p v-if="submitMsg" class="success">{{ submitMsg }}</p>
      </section>
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import AppHeader from '@/components/AppHeader.vue'
import { learningApi } from '@/api/learning.js'
import { useAuthStore } from '@/store/auth.js'
import { mockModuleContents, MOCK_ASSIGNMENT_ID } from '@/data/devMock.js'

const route = useRoute()
const auth = useAuthStore()
const moduleId = computed(() => route.params.moduleId)

const loading = ref(true)
const error = ref('')
const contents = ref([])

const assignmentId = ref('')
const answerText = ref('')
const submitting = ref(false)
const submitMsg = ref('')
const formError = ref('')
const usedMock = ref(false)

const SUBMISSION_STORAGE_KEY = 'shrd_submissions_v1'

function readSubmissions() {
  try {
    return JSON.parse(sessionStorage.getItem(SUBMISSION_STORAGE_KEY) || '{}')
  } catch {
    return {}
  }
}

function writeSubmission(moduleIdValue, assignmentIdValue) {
  const all = readSubmissions()
  all[String(moduleIdValue)] = {
    assignmentId: String(assignmentIdValue),
    submittedAt: new Date().toISOString()
  }
  sessionStorage.setItem(SUBMISSION_STORAGE_KEY, JSON.stringify(all))
}

async function load() {
  loading.value = true
  error.value = ''
  usedMock.value = false
  try {
    const res = await learningApi.moduleContents(moduleId.value)
    const d = res.data?.data
    contents.value = Array.isArray(d) ? d : []
    if (contents.value.length === 0 && auth.isDevPreview) {
      contents.value = mockModuleContents(moduleId.value)
      usedMock.value = true
    }
  } catch (e) {
    error.value = e.response?.data?.message || e.message || '조회 실패'
    if (auth.isDevPreview) {
      contents.value = mockModuleContents(moduleId.value)
      usedMock.value = true
      error.value = ''
    }
  } finally {
    loading.value = false
  }
}

async function submit() {
  if (!assignmentId.value) {
    submitMsg.value = ''
    formError.value = 'assignmentId를 입력하세요.'
    return
  }
  submitting.value = true
  submitMsg.value = ''
  formError.value = ''
  try {
    await learningApi.submitAssignment(assignmentId.value, {
      answerText: answerText.value,
      attachmentUrls: []
    })
    submitMsg.value = '제출되었습니다.'
    writeSubmission(moduleId.value, assignmentId.value)
  } catch (e) {
    formError.value = e.response?.data?.message || e.message || '제출 실패'
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  if (auth.isDevPreview) {
    assignmentId.value = MOCK_ASSIGNMENT_ID
  }
  load()
})
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: var(--color-bg-secondary);
}
.main {
  max-width: 800px;
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
.content-list {
  list-style: none;
  margin-bottom: 32px;
}
.content-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  margin-bottom: 8px;
}
.title {
  font-weight: 600;
  margin-right: 8px;
}
.btn-sm {
  padding: 6px 12px;
  font-size: 13px;
}
.card {
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 20px;
}
.sub-title {
  font-size: 16px;
  margin-bottom: 8px;
}
.hint {
  font-size: 13px;
  color: var(--color-text-secondary);
  margin-bottom: 12px;
}
.hint code {
  font-size: 12px;
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
  margin-bottom: 12px;
  font-size: 14px;
}
.form-input.area {
  resize: vertical;
}
.success {
  margin-top: 12px;
  color: var(--color-success);
  font-size: 14px;
}
.muted {
  color: var(--color-text-muted);
}
.error {
  color: var(--color-danger);
  margin-bottom: 8px;
}
.mock-hint {
  font-size: 13px;
  color: var(--color-text-muted);
  margin-bottom: 12px;
}
</style>
