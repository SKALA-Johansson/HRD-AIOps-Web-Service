<template>
  <div class="page">
    <AppHeader />
    <main class="main">
      <h1 class="page-title">{{ isEdit ? '콘텐츠 수정' : '콘텐츠 등록' }}</h1>
      <p class="page-desc">
        {{ isEdit ? 'PUT' : 'POST' }} <code>/contents</code>
        <template v-if="isEdit"> / <code>/contents/{contentId}</code></template>
      </p>

      <form class="card" @submit.prevent="submit">
        <label class="form-label">제목</label>
        <input v-model="form.title" class="form-input" required />
        <label class="form-label">유형 (PDF, VIDEO …)</label>
        <input v-model="form.type" class="form-input" required />
        <label class="form-label">카테고리 (BACKEND 등)</label>
        <input v-model="form.category" class="form-input" required />
        <label class="form-label">파일 URL</label>
        <input v-model="form.fileUrl" class="form-input" required />
        <label class="form-label">태그 (쉼표 구분)</label>
        <input v-model="tagsRaw" class="form-input" placeholder="spring, backend, java" />

        <p v-if="msg" class="success">{{ msg }}</p>
        <p v-if="err" class="error">{{ err }}</p>
        <div class="row">
          <button type="submit" class="btn btn-primary" :disabled="loading">
            {{ loading ? '저장 중…' : '저장' }}
          </button>
          <router-link to="/hr/contents" class="btn btn-ghost">목록</router-link>
        </div>
      </form>
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import AppHeader from '@/components/AppHeader.vue'
import { contentsApi } from '@/api/contents.js'

const route = useRoute()
const contentId = computed(() => route.params.contentId)
const isEdit = computed(() => !!contentId.value)

const form = ref({
  title: 'Spring Boot 기초',
  type: 'PDF',
  category: 'BACKEND',
  fileUrl: 'https://example.com/files/spring-basic.pdf',
  tags: ['spring', 'backend', 'java']
})
const tagsRaw = ref('spring, backend, java')
const loading = ref(false)
const msg = ref('')
const err = ref('')

onMounted(async () => {
  if (!isEdit.value) return
  loading.value = true
  try {
    const res = await contentsApi.list({})
    const list = Array.isArray(res.data?.data) ? res.data.data : []
    const found = list.find((c) => String(c.contentId) === String(contentId.value))
    if (found) {
      form.value = {
        title: found.title,
        type: found.type,
        category: found.category,
        fileUrl: found.fileUrl,
        tags: found.tags || []
      }
      tagsRaw.value = (found.tags || []).join(', ')
    }
  } catch {
    /* 목록으로 상세 조회 API가 없을 때는 기본값 유지 */
  } finally {
    loading.value = false
  }
})

async function submit() {
  msg.value = ''
  err.value = ''
  loading.value = true
  const tags = tagsRaw.value
    .split(',')
    .map((s) => s.trim())
    .filter(Boolean)
  const body = {
    title: form.value.title,
    type: form.value.type,
    category: form.value.category,
    fileUrl: form.value.fileUrl,
    tags
  }
  try {
    if (isEdit.value) {
      await contentsApi.update(contentId.value, body)
    } else {
      await contentsApi.create(body)
    }
    msg.value = '저장되었습니다.'
  } catch (e) {
    err.value = e.response?.data?.message || e.message || '실패'
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
.row {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}
.success {
  color: var(--color-success);
  margin-bottom: 8px;
}
.error {
  color: var(--color-danger);
  margin-bottom: 8px;
}
</style>
