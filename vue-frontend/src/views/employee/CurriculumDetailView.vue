<template>
  <div class="page">
    <AppHeader />
    <main class="main">
      <h1 class="page-title">커리큘럼 상세</h1>
      <p class="page-desc">GET <code>/curriculums/{curriculumId}</code></p>

      <p v-if="usedMock" class="mock-hint">개발 미리보기: 커리큘럼·모듈은 더미입니다.</p>
      <div v-if="loading" class="muted">불러오는 중…</div>
      <p v-else-if="error" class="error">{{ error }}</p>
      <div v-else class="card">
        <h2 class="title">{{ detail.title }}</h2>
        <p class="status">
          <span class="badge badge-blue">{{ detail.status }}</span>
        </p>
        <h3 class="sub">모듈</h3>
        <ul class="modules">
          <li v-for="m in detail.modules" :key="m.moduleId" class="mod">
            <span class="week">{{ m.week }}주차</span>
            <router-link :to="`/learning/modules/${m.moduleId}`" class="mod-link">{{ m.title }}</router-link>
          </li>
          <li v-if="!detail.modules?.length" class="muted">모듈 정보 없음</li>
        </ul>
      </div>
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute } from 'vue-router'
import AppHeader from '@/components/AppHeader.vue'
import { curriculumsApi } from '@/api/curriculums.js'
import { useAuthStore } from '@/store/auth.js'
import { mockCurriculum } from '@/data/devMock.js'

const route = useRoute()
const auth = useAuthStore()
const curriculumId = computed(() => route.params.curriculumId)

const loading = ref(true)
const error = ref('')
const usedMock = ref(false)
const detail = reactive({
  title: '',
  status: '',
  modules: []
})

function applyMock() {
  const m = mockCurriculum(curriculumId.value)
  detail.title = m.title
  detail.status = m.status
  detail.modules = m.modules ?? []
  usedMock.value = true
  error.value = ''
}

async function load() {
  loading.value = true
  error.value = ''
  usedMock.value = false
  try {
    const res = await curriculumsApi.get(curriculumId.value)
    const d = res.data?.data
    if (d) {
      detail.title = d.title ?? ''
      detail.status = d.status ?? ''
      detail.modules = d.modules ?? []
    } else if (auth.isDevPreview) {
      applyMock()
    }
  } catch (e) {
    error.value = e.response?.data?.message || e.message || '조회 실패'
    if (auth.isDevPreview) applyMock()
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
.card {
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 24px;
}
.title {
  font-size: 1.25rem;
  margin-bottom: 8px;
}
.status {
  margin-bottom: 16px;
}
.sub {
  font-size: 15px;
  margin-bottom: 10px;
}
.modules {
  list-style: none;
}
.mod {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 0;
  border-bottom: 1px solid var(--color-border);
}
.week {
  font-size: 13px;
  color: var(--color-text-muted);
  min-width: 56px;
}
.mod-link {
  color: var(--color-primary);
  font-weight: 500;
}
.muted {
  color: var(--color-text-muted);
  font-size: 14px;
}
.error {
  color: var(--color-danger);
}
.mock-hint {
  font-size: 13px;
  color: var(--color-text-muted);
  margin-bottom: 12px;
}
</style>
