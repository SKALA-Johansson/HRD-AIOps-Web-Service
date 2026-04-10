<template>
  <div class="dev-scenarios">
    <p class="lead">
      <strong>Step 1 요구사항</strong> 기준 바로가기 — 역할을 맞춘 뒤 해당 화면으로 이동합니다. (DB 없이
      미리보기 세션 필요)
    </p>

    <div class="block">
      <h3 class="block-title">공통</h3>
      <div class="btns">
        <router-link to="/signup" class="btn btn-outline btn-sm">회원가입</router-link>
        <router-link to="/login" class="btn btn-outline btn-sm">로그인</router-link>
      </div>
    </div>

    <div class="block">
      <h3 class="block-title">신입사원</h3>
      <div class="btns">
        <button type="button" class="btn btn-ghost btn-sm" @click="goEmp('/profile')">프로필</button>
        <button type="button" class="btn btn-ghost btn-sm" @click="goEmp('/learning')">맞춤 커리큘럼(학습 홈)</button>
        <button type="button" class="btn btn-ghost btn-sm" @click="goEmp('/learning/progress')">학습 진도</button>
        <button type="button" class="btn btn-ghost btn-sm" @click="goEmp('/curriculums/301')">커리큘럼 상세(더미 301)</button>
        <button type="button" class="btn btn-ghost btn-sm" @click="goEmp('/learning/modules/1')">콘텐츠·과제 제출(모듈 1)</button>
        <button type="button" class="btn btn-ghost btn-sm" @click="openTutorChat">AI 튜터(챗 패널)</button>
        <button type="button" class="btn btn-ghost btn-sm" @click="goEmp('/reports/me')">성장 리포트</button>
      </div>
    </div>

    <div class="block">
      <h3 class="block-title">HR 담당자</h3>
      <div class="btns">
        <button type="button" class="btn btn-ghost btn-sm" @click="goHr('/hr/dashboard')">교육 현황 대시보드</button>
        <button type="button" class="btn btn-ghost btn-sm" @click="goHr('/hr/curriculums')">커리큘럼 생성·승인</button>
        <button type="button" class="btn btn-ghost btn-sm" @click="goHr('/hr/contents')">콘텐츠 목록</button>
        <button type="button" class="btn btn-ghost btn-sm" @click="goHr('/hr/contents/new')">콘텐츠 등록</button>
        <button type="button" class="btn btn-ghost btn-sm" @click="goHr('/hr/reports')">성장 리포트 조회</button>
        <button type="button" class="btn btn-ghost btn-sm" @click="goHr('/hr/team-progress')">담당 신입 학습 진도</button>
        <button type="button" class="btn btn-ghost btn-sm" @click="goHr('/profile')">프로필</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth.js'
import { useTutorDockStore } from '@/store/tutorDock.js'

const router = useRouter()
const auth = useAuthStore()
const tutorDock = useTutorDockStore()

function openTutorChat() {
  auth.startDevPreview('EMPLOYEE')
  tutorDock.open()
  router.push('/learning')
}

function goEmp(path) {
  auth.startDevPreview('EMPLOYEE')
  router.push(path)
}
function goHr(path) {
  auth.startDevPreview('HR')
  router.push(path)
}
</script>

<style scoped>
.dev-scenarios {
  margin-top: 20px;
  padding: 18px 20px;
  border-radius: var(--radius-lg);
  border: 1px dashed var(--color-border-hover);
  background: var(--color-bg-secondary);
  max-width: 720px;
}
.lead {
  font-size: 13px;
  color: var(--color-text-secondary);
  line-height: 1.55;
  margin-bottom: 18px;
}
.block {
  margin-bottom: 16px;
}
.block:last-child {
  margin-bottom: 0;
}
.block-title {
  font-size: 13px;
  font-weight: 700;
  color: var(--color-text-primary);
  margin-bottom: 8px;
}
.btns {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.btn-sm {
  padding: 7px 12px;
  font-size: 12px;
}
</style>
