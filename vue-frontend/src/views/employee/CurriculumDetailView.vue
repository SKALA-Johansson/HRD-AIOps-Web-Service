<template>
  <div class="page">
    <AppHeader />
    <main class="main">
      <h1 class="page-title">커리큘럼 상세</h1>

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

const route = useRoute()
const curriculumId = computed(() => route.params.curriculumId)

const loading = ref(true)
const error = ref('')
const detail = reactive({ title: '', status: '', modules: [] })

async function load() {
  loading.value = true
  error.value = ''
  try {
    const res = await curriculumsApi.get(curriculumId.value)
    const d = res.data?.data
    if (d) {
      detail.title = d.title ?? ''
      detail.status = d.status ?? ''
      detail.modules = d.modules ?? []
    }
  } catch (e) {
    error.value = '커리큘럼 정보를 불러오지 못했습니다.'
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.page { min-height: 100vh; background: var(--color-bg-secondary); }
.main { max-width: 800px; margin: 0 auto; padding: 28px 24px 64px; }
.page-title { font-size: 1.5rem; font-weight: 700; margin-bottom: 20px; }
.card { background: var(--color-bg-primary); border: 1px solid var(--color-border); border-radius: var(--radius-lg); padding: 24px; }
.title { font-size: 1.25rem; margin-bottom: 8px; }
.status { margin-bottom: 16px; }
.sub { font-size: 15px; margin-bottom: 10px; }
.modules { list-style: none; }
.mod { display: flex; align-items: center; gap: 12px; padding: 10px 0; border-bottom: 1px solid var(--color-border); }
.week { font-size: 13px; color: var(--color-text-muted); min-width: 56px; }
.mod-link { color: var(--color-primary); font-weight: 500; }
.muted { color: var(--color-text-muted); font-size: 14px; }
.error { color: var(--color-danger); }
</style>
