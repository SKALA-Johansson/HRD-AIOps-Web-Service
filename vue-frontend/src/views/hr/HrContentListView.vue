<template>
  <div class="page">
    <AppHeader />
    <main class="main">
      <div class="head-row">
        <div>
          <h1 class="page-title">교육 콘텐츠 관리</h1>
          <p class="page-desc">GET <code>/contents</code> — Content Management Service</p>
        </div>
        <router-link to="/hr/contents/new" class="btn btn-primary btn-sm">새 콘텐츠</router-link>
      </div>

      <div class="filters">
        <input v-model="category" class="form-input" placeholder="category (예: BACKEND)" />
        <input v-model="type" class="form-input" placeholder="type (예: PDF)" />
        <button type="button" class="btn btn-outline btn-sm" @click="load">조회</button>
      </div>

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
import { onMounted, ref } from 'vue'
import AppHeader from '@/components/AppHeader.vue'
import { contentsApi } from '@/api/contents.js'

const category = ref('BACKEND')
const type = ref('PDF')
const loading = ref(false)
const error = ref('')
const rows = ref([])

async function load() {
  loading.value = true
  error.value = ''
  try {
    const res = await contentsApi.list({
      category: category.value || undefined,
      type: type.value || undefined
    })
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
