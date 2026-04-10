<template>
  <div class="landing">
    <AppHeader />
    <section class="hero">
      <div class="hero-inner">
        <div class="hero-content fade-in-up">
          <span class="hero-badge">Agentic AI · MSA · RAG</span>
          <h1 class="hero-title">
            신입 맞춤 교육과<br />
            성장 인사이트를 한곳에서
          </h1>
          <p class="hero-desc">
            Goal Setter → Curriculum Designer → AI Tutor → Growth Report로 이어지는 스마트 HRD AIOps
            플로우를 지원합니다. (Gateway <code>/api/v1</code> 연동 전제)
          </p>
          <div class="hero-actions">
            <router-link to="/signup" class="btn btn-primary btn-lg">시작하기</router-link>
            <router-link to="/login" class="btn btn-outline btn-lg">로그인</router-link>
          </div>
          <!-- 개발 전용: 백엔드 없이 보호된 화면 UI 확인 -->
          <div v-if="isDev" class="dev-preview-panel">
            <p class="dev-preview-label">로컬 개발 — DB 없이 화면만 볼 때</p>
            <div class="dev-preview-btns">
              <button type="button" class="btn btn-ghost btn-sm" @click="previewEmployee">
                신입 화면 (학습·과제·진도)
              </button>
              <button type="button" class="btn btn-ghost btn-sm" @click="previewHr">HR 화면</button>
            </div>
            <DevScenarioLinks />
          </div>
        </div>
        <div class="hero-visual fade-in">
          <img src="@/assets/images/logo/main_logo.png" alt="" class="hero-logo" />
        </div>
      </div>
    </section>

    <section class="section-block">
      <div class="section-inner">
        <h2 class="section-title">역할별 화면</h2>
        <div class="card-grid">
          <div class="info-card">
            <h3>신입사원</h3>
            <p>프로필, 배정된 학습·과제, AI 튜터, 진도·성장 리포트</p>
          </div>
          <div class="info-card">
            <h3>HR</h3>
            <p>PDF 기반 커리큘럼 생성, 승인, 대시보드, 콘텐츠 관리, 팀 학습 진도, 튜터링 가이드, 리포트</p>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import AppHeader from '@/components/AppHeader.vue'
import DevScenarioLinks from '@/components/DevScenarioLinks.vue'
import { useAuthStore } from '@/store/auth.js'

const isDev = import.meta.env.DEV
const auth = useAuthStore()
const router = useRouter()

function previewEmployee() {
  auth.startDevPreview('EMPLOYEE')
  router.push('/learning')
}
function previewHr() {
  auth.startDevPreview('HR')
  router.push('/hr/dashboard')
}
</script>

<style scoped>
.landing {
  min-height: 100vh;
  background: var(--color-bg-secondary);
}
.hero {
  padding: 48px 24px 64px;
}
.hero-inner {
  max-width: 1100px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 48px;
  align-items: center;
}
@media (max-width: 900px) {
  .hero-inner {
    grid-template-columns: 1fr;
  }
}
.hero-badge {
  display: inline-block;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  background: var(--color-primary-light);
  color: var(--color-primary);
  margin-bottom: 16px;
}
.hero-title {
  font-size: clamp(1.75rem, 4vw, 2.25rem);
  font-weight: 700;
  line-height: 1.25;
  margin-bottom: 16px;
  letter-spacing: -0.5px;
}
.hero-desc {
  color: var(--color-text-secondary);
  font-size: 15px;
  margin-bottom: 28px;
  max-width: 480px;
}
.hero-desc code {
  font-size: 13px;
  background: var(--color-bg-tertiary);
  padding: 2px 6px;
  border-radius: 4px;
}
.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}
.btn-lg {
  padding: 12px 24px;
  font-size: 15px;
}
.dev-preview-panel {
  margin-top: 28px;
  padding: 16px 18px;
  border-radius: var(--radius-lg);
  border: 1px dashed var(--color-border-hover);
  background: var(--color-bg-primary);
  max-width: 520px;
}
.dev-preview-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--color-text-secondary);
  margin-bottom: 10px;
}
.dev-preview-btns {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.hero-visual {
  display: flex;
  justify-content: center;
}
.hero-logo {
  width: min(280px, 80vw);
  height: auto;
  opacity: 0.95;
}
.section-block {
  padding: 32px 24px 64px;
}
.section-inner {
  max-width: 1100px;
  margin: 0 auto;
}
.section-title {
  font-size: 1.25rem;
  font-weight: 700;
  margin-bottom: 20px;
}
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 16px;
}
.info-card {
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 20px;
  box-shadow: var(--shadow-sm);
}
.info-card h3 {
  font-size: 16px;
  margin-bottom: 8px;
}
.info-card p {
  font-size: 14px;
  color: var(--color-text-secondary);
  line-height: 1.55;
}
</style>
