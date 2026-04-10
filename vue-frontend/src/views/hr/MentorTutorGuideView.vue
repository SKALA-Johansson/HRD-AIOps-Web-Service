<template>
  <div class="page">
    <AppHeader />
    <main class="main">
      <h1 class="page-title">AI 튜터링 가이드</h1>
      <p class="page-desc">
        Growth Reporter 등에서 생성되는 면담 가이드(요구사항 Step 1). 백엔드 연동 전 더미입니다.
      </p>

      <div v-if="isDev" class="note">개발: API 대신 정적 더미입니다.</div>

      <section class="card">
        <h2 class="sub">이번 주 포커스</h2>
        <p class="body">{{ guide.weekFocus }}</p>
      </section>

      <section class="card">
        <h2 class="sub">면담 시 짚을 포인트</h2>
        <ul>
          <li v-for="(t, i) in guide.talkingPoints" :key="i">{{ t }}</li>
        </ul>
      </section>

      <section class="card">
        <h2 class="sub">추천 질문</h2>
        <ul>
          <li v-for="(q, i) in guide.suggestedQuestions" :key="i">{{ q }}</li>
        </ul>
      </section>
    </main>
  </div>
</template>

<script setup>
import AppHeader from '@/components/AppHeader.vue'
import { MOCK_TUTOR_GUIDE } from '@/data/devMock.js'

const isDev = import.meta.env.DEV
const guide = MOCK_TUTOR_GUIDE
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
  margin-bottom: 16px;
  line-height: 1.5;
}
.note {
  font-size: 13px;
  padding: 10px 14px;
  border-radius: var(--radius-md);
  background: var(--color-primary-light);
  margin-bottom: 20px;
}
.card {
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 20px;
  margin-bottom: 16px;
}
.sub {
  font-size: 16px;
  margin-bottom: 12px;
}
.body {
  font-size: 14px;
  line-height: 1.6;
  color: var(--color-text-secondary);
}
ul {
  margin-left: 1.2rem;
  font-size: 14px;
  line-height: 1.65;
  color: var(--color-text-secondary);
}
</style>
