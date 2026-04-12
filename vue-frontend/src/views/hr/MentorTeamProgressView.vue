<template>
  <div class="page">
    <AppHeader />
    <main class="main">
      <h1 class="page-title">담당 신입 학습 진도</h1>

      <div v-if="loading" class="muted">불러오는 중…</div>
      <p v-if="error" class="error">{{ error }}</p>

      <div class="table-wrap">
        <table class="table">
          <thead>
            <tr>
              <th>이름</th>
              <th>userId</th>
              <th>진행률</th>
              <th>상태</th>
              <th>최근 모듈</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in rows" :key="row.userId">
              <td>{{ row.name }}</td>
              <td>{{ row.userId }}</td>
              <td>{{ row.completionRate != null ? row.completionRate + '%' : '—' }}</td>
              <td>
                <span class="badge" :class="row.status === '지연' || row.status === 'DELAYED' ? 'warn' : 'ok'">
                  {{ row.status }}
                </span>
              </td>
              <td>{{ row.lastModule || '—' }}</td>
            </tr>
            <tr v-if="!rows.length && !loading">
              <td colspan="5" class="muted">데이터가 없습니다.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </main>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import AppHeader from '@/components/AppHeader.vue'
import { reportsApi } from '@/api/reports.js'

const loading = ref(true)
const error = ref('')
const rows = ref([])

onMounted(async () => {
  loading.value = true
  error.value = ''
  try {
    const res = await reportsApi.users()
    const d = res.data?.data ?? res.data
    rows.value = Array.isArray(d) ? d : []
  } catch (e) {
    error.value = '학습 진도 목록을 불러오지 못했습니다.'
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.page { min-height: 100vh; background: var(--color-bg-secondary); }
.main { max-width: 960px; margin: 0 auto; padding: 28px 24px 64px; }
.page-title { font-size: 1.5rem; font-weight: 700; margin-bottom: 20px; }
.table-wrap { overflow-x: auto; border: 1px solid var(--color-border); border-radius: var(--radius-lg); background: var(--color-bg-primary); }
.table { width: 100%; border-collapse: collapse; font-size: 14px; }
th, td { padding: 12px 14px; text-align: left; border-bottom: 1px solid var(--color-border); }
th { background: var(--color-bg-tertiary); font-weight: 600; }
.badge { display: inline-block; padding: 2px 8px; border-radius: 6px; font-size: 12px; font-weight: 600; }
.badge.ok { background: var(--color-success-light); color: var(--color-success); }
.badge.warn { background: var(--color-warning-light); color: var(--color-warning); }
.muted { color: var(--color-text-muted); }
.error { color: var(--color-danger); margin-bottom: 12px; }
</style>
