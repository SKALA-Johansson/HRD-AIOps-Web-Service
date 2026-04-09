<template>
  <div class="page">
    <AppHeader />
    <main class="main">
      <h1 class="page-title">담당 신입 학습 진도</h1>
      <p class="page-desc">
        HR이 담당 신입의 학습 진도를 보는 화면(프론트 스캐폴드). 실제 연동 시 GET 등 API로 교체합니다.
      </p>

      <div v-if="isDev" class="note">개발: 아래 표는 더미 데이터입니다.</div>

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
              <td>{{ row.completionRate }}%</td>
              <td>
                <span class="badge" :class="row.status === '지연' ? 'warn' : 'ok'">{{ row.status }}</span>
              </td>
              <td>{{ row.lastModule }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </main>
  </div>
</template>

<script setup>
import AppHeader from '@/components/AppHeader.vue'
import { MOCK_TEAM_PROGRESS } from '@/data/devMock.js'

const isDev = import.meta.env.DEV
const rows = MOCK_TEAM_PROGRESS
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
.page-title {
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: 8px;
}
.page-desc {
  font-size: 14px;
  color: var(--color-text-secondary);
  margin-bottom: 16px;
  line-height: 1.5;
}
.note {
  font-size: 13px;
  padding: 10px 14px;
  border-radius: var(--radius-md);
  background: var(--color-primary-light);
  color: var(--color-text-primary);
  margin-bottom: 20px;
}
.table-wrap {
  overflow-x: auto;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  background: var(--color-bg-primary);
}
.table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}
th,
td {
  padding: 12px 14px;
  text-align: left;
  border-bottom: 1px solid var(--color-border);
}
th {
  background: var(--color-bg-tertiary);
  font-weight: 600;
}
.badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
}
.badge.ok {
  background: var(--color-success-light);
  color: var(--color-success);
}
.badge.warn {
  background: var(--color-warning-light);
  color: var(--color-warning);
}
</style>
