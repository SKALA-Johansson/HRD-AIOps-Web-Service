<template>
  <div class="page">
    <AppHeader />
    <main class="main">
      <h1 class="page-title">내 프로필</h1>

      <div v-if="loading" class="muted">불러오는 중…</div>
      <form v-else class="card form-card" @submit.prevent="save">
        <div class="grid">
          <div>
            <label class="form-label">희망 계열사</label>
            <input v-model="form.desiredCompany" class="form-input" placeholder="예: SKT" />
          </div>
          <div>
            <label class="form-label">희망 직무</label>
            <input v-model="form.desiredJob" class="form-input" placeholder="예: AI/Data" />
          </div>
        </div>
        <label class="form-label">이력 요약</label>
        <textarea v-model="form.careerHistory" class="form-input area" rows="3" />

        <label class="form-label">자기소개</label>
        <textarea v-model="form.selfIntroduction" class="form-input area" rows="3" />

        <h2 class="sub-title">사전 역량 (0–100)</h2>
        <div class="grid three">
          <div>
            <label class="form-label">Python</label>
            <input v-model.number="form.preAssessment.python" type="number" min="0" max="100" class="form-input" />
          </div>
          <div>
            <label class="form-label">SQL</label>
            <input v-model.number="form.preAssessment.sql" type="number" min="0" max="100" class="form-input" />
          </div>
          <div>
            <label class="form-label">ML</label>
            <input v-model.number="form.preAssessment.ml" type="number" min="0" max="100" class="form-input" />
          </div>
        </div>

        <p v-if="message" class="success">{{ message }}</p>
        <p v-if="error" class="error">{{ error }}</p>

        <button type="submit" class="btn btn-primary" :disabled="saving">{{ saving ? '저장 중…' : '저장' }}</button>
      </form>
    </main>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import AppHeader from '@/components/AppHeader.vue'
import { profilesApi } from '@/api/profiles.js'

const loading = ref(true)
const saving = ref(false)
const error = ref('')
const message = ref('')

const form = reactive({
  desiredCompany: '',
  desiredJob: '',
  careerHistory: '',
  selfIntroduction: '',
  preAssessment: { python: 0, sql: 0, ml: 0 }
})

async function load() {
  loading.value = true
  error.value = ''
  try {
    const res = await profilesApi.getMe()
    const d = res.data?.data
    if (d) {
      form.desiredCompany = d.desiredCompany ?? ''
      form.desiredJob = d.desiredJob ?? ''
      form.careerHistory = d.careerHistory ?? ''
      form.selfIntroduction = d.selfIntroduction ?? ''
      form.preAssessment = {
        python: d.preAssessment?.python ?? 0,
        sql: d.preAssessment?.sql ?? 0,
        ml: d.preAssessment?.ml ?? 0
      }
    }
  } catch (e) {
    error.value = '프로필 정보를 불러오지 못했습니다.'
  } finally {
    loading.value = false
  }
}

async function save() {
  saving.value = true
  message.value = ''
  error.value = ''
  try {
    await profilesApi.updateMe({ ...form })
    message.value = '저장되었습니다.'
  } catch (e) {
    error.value = '프로필 저장에 실패했습니다. 잠시 후 다시 시도해 주세요.'
  } finally {
    saving.value = false
  }
}

onMounted(load)
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
.card {
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 24px;
  box-shadow: var(--shadow-sm);
}
.form-label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  margin-bottom: 6px;
}
.form-input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: 14px;
  margin-bottom: 16px;
}
.form-input.area {
  resize: vertical;
  min-height: 80px;
}
.grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}
.grid.three {
  grid-template-columns: repeat(3, 1fr);
}
@media (max-width: 640px) {
  .grid,
  .grid.three {
    grid-template-columns: 1fr;
  }
}
.sub-title {
  font-size: 15px;
  margin: 8px 0 12px;
}
.muted {
  color: var(--color-text-muted);
}
.success {
  color: var(--color-success);
  font-size: 14px;
  margin-bottom: 8px;
}
.error {
  color: var(--color-danger);
  font-size: 14px;
  margin-bottom: 8px;
}
</style>
