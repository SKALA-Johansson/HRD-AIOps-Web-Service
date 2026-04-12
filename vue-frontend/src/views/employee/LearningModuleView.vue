<template>
  <div class="page">
    <AppHeader />
    <main class="main">

      <div v-if="loading" class="state muted">콘텐츠 생성 중… (처음 열면 AI가 내용을 생성합니다)</div>
      <p v-else-if="error" class="error state">{{ error }}</p>

      <template v-else>
        <!-- 헤더 -->
        <div class="module-header">
          <span class="week-badge">{{ detail.week }}주차</span>
          <h1 class="module-title">{{ detail.title }}</h1>
          <p v-if="detail.description" class="module-desc">{{ detail.description }}</p>
          <span v-if="detail.estimatedHours" class="meta-chip">⏱ 예상 학습 시간 {{ detail.estimatedHours }}h</span>
        </div>

        <!-- 학습 목표 -->
        <section v-if="detail.learningObjectives?.length" class="section">
          <h2 class="section-title">학습 목표</h2>
          <ul class="objective-list">
            <li v-for="(obj, i) in detail.learningObjectives" :key="i" class="objective-item">
              <span class="obj-num">{{ i + 1 }}</span>
              <span>{{ obj }}</span>
            </li>
          </ul>
        </section>

        <!-- 학습 내용 (마크다운 렌더) -->
        <section v-if="detail.content" class="section">
          <h2 class="section-title">학습 내용</h2>
          <div class="content-body" v-html="renderedContent" />
        </section>

        <!-- 참고 자료 -->
        <section v-if="detail.resources?.length" class="section">
          <h2 class="section-title">참고 자료</h2>
          <ul class="resource-list">
            <li v-for="(res, i) in detail.resources" :key="i" class="resource-item">
              <template v-if="extractUrl(res)">
                <a :href="extractUrl(res)" target="_blank" rel="noopener" class="resource-link">
                  {{ extractTitle(res) }}
                </a>
              </template>
              <span v-else class="resource-text">{{ res }}</span>
            </li>
          </ul>
        </section>

        <!-- 과제 -->
        <section v-if="detail.assignments?.length" class="section">
          <h2 class="section-title">과제</h2>
          <ul class="assignment-list">
            <li v-for="(asgn, i) in detail.assignments" :key="i" class="assignment-item">
              <span class="asgn-num">{{ i + 1 }}</span>
              <span>{{ asgn }}</span>
            </li>
          </ul>
        </section>

        <!-- 퀴즈 -->
        <section class="section quiz-section">
          <div class="quiz-head">
            <h2 class="section-title" style="border:none;margin:0;padding:0">퀴즈</h2>
            <button
              v-if="quizState === 'idle'"
              type="button"
              class="btn btn-primary btn-sm"
              :disabled="quizLoading"
              @click="loadQuiz"
            >
              {{ quizLoading ? '생성 중…' : '퀴즈 시작' }}
            </button>
          </div>

          <!-- 로딩 -->
          <div v-if="quizLoading" class="quiz-loading muted">AI가 문제를 생성하고 있습니다…</div>
          <p v-if="quizError" class="error">{{ quizError }}</p>

          <!-- 문제 목록 -->
          <div v-if="quizState === 'answering'" class="quiz-questions">
            <div v-for="(q, qi) in questions" :key="q.id" class="q-card">
              <div class="q-header">
                <span class="q-num">Q{{ qi + 1 }}</span>
                <span class="q-points">{{ q.points }}점</span>
              </div>
              <p class="q-text">{{ q.question }}</p>
              <div class="q-options">
                <label
                  v-for="opt in q.options"
                  :key="opt"
                  class="q-option"
                  :class="{ selected: studentAnswers[qi] === opt.charAt(0) }"
                >
                  <input
                    type="radio"
                    :name="`q${qi}`"
                    :value="opt.charAt(0)"
                    v-model="studentAnswers[qi]"
                    class="q-radio"
                  />
                  <span class="q-opt-text">{{ opt }}</span>
                </label>
              </div>
            </div>

            <button
              type="button"
              class="btn btn-primary"
              :disabled="submitting || !allAnswered"
              @click="submitQuiz"
            >
              {{ submitting ? '채점 중…' : '제출하기' }}
            </button>
            <p v-if="!allAnswered" class="muted hint">모든 문제에 답하면 제출할 수 있습니다.</p>
          </div>

          <!-- 결과 -->
          <div v-if="quizState === 'done'" class="quiz-result">
            <div class="result-score" :class="quizResult.passed ? 'passed' : 'failed'">
              <span class="score-num">{{ quizResult.score }} / {{ quizResult.maxScore }}</span>
              <span class="score-label">{{ quizResult.passed ? '합격' : '재도전 필요' }}</span>
            </div>
            <p class="result-summary">{{ quizResult.summary }}</p>

            <!-- 주차 완료 알림 배너 -->
            <div v-if="weekCompleted" class="week-complete-banner">
              <div class="week-complete-icon">★</div>
              <div class="week-complete-body">
                <strong>{{ detail.week }}주차 학습 완료!</strong>
                <p>모든 모듈 학습을 마쳤습니다. AI가 성장 리포트를 생성하고 있습니다.</p>
              </div>
              <router-link :to="`/reports/me?curriculum_id=${detail.curriculumId}`" class="btn btn-outline btn-sm report-btn">
                리포트 보기
              </router-link>
            </div>

            <div v-for="r in quizResult.perQuestion" :key="r.id" class="q-result-row">
              <div class="q-result-header">
                <span class="q-result-icon">{{ r.is_correct ? '✓' : '✗' }}</span>
                <span class="q-result-text">{{ r.question }}</span>
              </div>
              <div v-if="!r.is_correct" class="q-result-detail">
                <span class="q-answer-label">내 답: </span><strong>{{ r.student_answer || '미응답' }}</strong>
                &nbsp;·&nbsp;
                <span class="q-answer-label">정답: </span><strong>{{ r.correct_answer }}</strong>
              </div>
              <p v-if="r.explanation" class="q-explanation">{{ r.explanation }}</p>
            </div>
          </div>
        </section>
      </template>

    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/store/auth.js'
import AppHeader from '@/components/AppHeader.vue'
import { curriculumsApi } from '@/api/curriculums.js'
import { tutorApi } from '@/api/tutor.js'

const route = useRoute()
const auth = useAuthStore()
const moduleId = computed(() => route.params.moduleId)

// ── 모듈 상세 ─────────────────────────────────────────────────────
const loading = ref(true)
const error = ref('')
const detail = reactive({
  moduleId: '',
  curriculumId: '',
  week: '',
  title: '',
  description: '',
  content: '',
  learningObjectives: [],
  resources: [],
  assignments: [],
  estimatedHours: null,
})

// ── 퀴즈 ──────────────────────────────────────────────────────────
// quizState: 'idle' | 'answering' | 'done'
const quizState = ref('idle')
const quizLoading = ref(false)
const quizError = ref('')
const questions = ref([])          // [{id, question, options, correct_answer, explanation, points}]
const studentAnswers = ref([])     // ['A', 'B', ...]
const submitting = ref(false)
const weekCompleted = ref(false)   // 이번 퀴즈로 주차 완료 여부 (서버에서 판단됨)
const quizResult = reactive({
  score: 0,
  maxScore: 100,
  passed: false,
  summary: '',
  perQuestion: [],
})

const allAnswered = computed(() =>
  questions.value.length > 0 && studentAnswers.value.every((a) => !!a)
)

// 마크다운 → HTML 변환
const renderedContent = computed(() => {
  const text = detail.content || ''
  return text
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/^#{3} (.+)$/gm, '<h3>$1</h3>')
    .replace(/^#{2} (.+)$/gm, '<h2>$1</h2>')
    .replace(/^# (.+)$/gm, '<h1>$1</h1>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/^- (.+)$/gm, '<li>$1</li>')
    .replace(/(<li>.*<\/li>\n?)+/g, (m) => `<ul>${m}</ul>`)
    .replace(/\n\n+/g, '</p><p>')
    .replace(/\n/g, '<br>')
})

function extractUrl(resource) {
  const m = resource.match(/https?:\/\/[^\s)]+/)
  return m ? m[0] : null
}

function extractTitle(resource) {
  return resource.replace(/\s*\(https?:\/\/[^\s)]+\)/, '').trim() || resource
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const res = await curriculumsApi.getModule(moduleId.value)
    const d = res.data?.data
    if (d) Object.assign(detail, d)
  } catch {
    error.value = '모듈 정보를 불러오지 못했습니다.'
  } finally {
    loading.value = false
  }
}

async function loadQuiz() {
  quizLoading.value = true
  quizError.value = ''
  try {
    const res = await tutorApi.generateQuiz({
      module_id: detail.moduleId,
      module_title: detail.title,
      learning_objectives: detail.learningObjectives,
      content: detail.content,
      num_questions: 4,
    })
    const qs = res.data?.data?.questions ?? []
    if (!qs.length) throw new Error('문제를 생성하지 못했습니다.')
    questions.value = qs
    studentAnswers.value = Array(qs.length).fill('')
    quizState.value = 'answering'
  } catch (e) {
    quizError.value = e.message || '퀴즈 생성에 실패했습니다.'
  } finally {
    quizLoading.value = false
  }
}

async function submitQuiz() {
  submitting.value = true
  quizError.value = ''
  weekCompleted.value = false
  try {
    const quizId = detail.moduleId
    const userId = auth.user?.username || auth.user?.userId || '0'
    const res = await tutorApi.submitQuiz(quizId, {
      user_id: String(userId),
      module_id: detail.moduleId,
      curriculum_id: detail.curriculumId,
      week_number: detail.week ? Number(detail.week) : undefined,
      questions: questions.value,
      student_answers: studentAnswers.value,
    })
    const d = res.data?.data
    quizResult.score = d?.score ?? 0
    quizResult.maxScore = d?.maxScore ?? 100
    quizResult.passed = d?.passed ?? false
    quizResult.summary = d?.summary ?? ''
    quizResult.perQuestion = d?.perQuestion ?? []
    quizState.value = 'done'

    // 주차 완료 여부는 서버(curriculum-designer-agent)가 kafka로 판단.
    // 합격 시 배너 표시 (리포트는 비동기 생성됨)
    if (quizResult.passed) {
      weekCompleted.value = true
    }
  } catch {
    quizError.value = '채점 중 오류가 발생했습니다.'
  } finally {
    submitting.value = false
  }
}

function resetQuiz() {
  quizState.value = 'idle'
  questions.value = []
  studentAnswers.value = []
  weekCompleted.value = false
  quizResult.score = 0
  quizResult.passed = false
  quizResult.summary = ''
  quizResult.perQuestion = []
}

onMounted(load)
</script>

<style scoped>
.page { min-height: 100vh; background: var(--color-bg-secondary); }
.main { max-width: 860px; margin: 0 auto; padding: 28px 24px 80px; }

/* 헤더 */
.module-header {
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
  padding: 28px 32px;
  margin-bottom: 24px;
  border-left: 5px solid var(--color-primary);
}
.week-badge {
  display: inline-block;
  font-size: 12px;
  font-weight: 700;
  color: var(--color-primary);
  background: var(--color-primary-light);
  padding: 3px 10px;
  border-radius: 999px;
  margin-bottom: 10px;
}
.module-title { font-size: 1.5rem; font-weight: 800; margin-bottom: 8px; line-height: 1.3; }
.module-desc { font-size: 15px; color: var(--color-text-secondary); line-height: 1.6; margin-bottom: 12px; }
.meta-chip {
  display: inline-block;
  font-size: 12px;
  color: var(--color-text-muted);
  background: var(--color-bg-tertiary);
  padding: 3px 10px;
  border-radius: 999px;
  border: 1px solid var(--color-border);
}

/* 섹션 공통 */
.section {
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 24px;
  margin-bottom: 16px;
}
.section-title {
  font-size: 15px;
  font-weight: 700;
  color: var(--color-text-primary);
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--color-border);
}

/* 학습 목표 */
.objective-list { list-style: none; display: flex; flex-direction: column; gap: 10px; }
.objective-item { display: flex; align-items: flex-start; gap: 12px; font-size: 14px; line-height: 1.55; }
.obj-num {
  flex-shrink: 0;
  width: 24px; height: 24px;
  border-radius: 50%;
  background: var(--color-primary);
  color: #fff;
  font-size: 12px; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
}

/* 학습 내용 */
.content-body {
  font-size: 14px;
  line-height: 1.75;
  color: var(--color-text-primary);
}
.content-body :deep(h1) { font-size: 1.2rem; font-weight: 700; margin: 16px 0 8px; }
.content-body :deep(h2) { font-size: 1.05rem; font-weight: 700; margin: 14px 0 6px; }
.content-body :deep(h3) { font-size: 1rem; font-weight: 600; margin: 12px 0 4px; }
.content-body :deep(code) {
  background: var(--color-bg-tertiary);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: monospace;
  font-size: 13px;
}
.content-body :deep(ul) { padding-left: 20px; margin: 8px 0; }
.content-body :deep(li) { margin: 4px 0; }
.content-body :deep(strong) { font-weight: 700; }

/* 참고 자료 */
.resource-list { list-style: none; display: flex; flex-direction: column; gap: 8px; }
.resource-item { font-size: 14px; }
.resource-link { color: var(--color-primary); text-decoration: underline; }
.resource-link:hover { opacity: 0.8; }
.resource-text { color: var(--color-text-secondary); }

/* 과제 */
.assignment-list { list-style: none; display: flex; flex-direction: column; gap: 10px; }
.assignment-item { display: flex; align-items: flex-start; gap: 12px; font-size: 14px; line-height: 1.55; }
.asgn-num {
  flex-shrink: 0;
  width: 24px; height: 24px;
  border-radius: 6px;
  background: var(--color-bg-tertiary);
  border: 1px solid var(--color-border);
  font-size: 12px; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
}

/* 퀴즈 */
.quiz-section { }
.quiz-head {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--color-border);
}
.quiz-loading { padding: 20px 0; font-size: 14px; }
.quiz-questions { display: flex; flex-direction: column; gap: 20px; }
.q-card {
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 18px 20px;
  background: var(--color-bg-secondary);
}
.q-header { display: flex; justify-content: space-between; margin-bottom: 10px; }
.q-num {
  font-size: 12px; font-weight: 700; color: var(--color-primary);
  background: var(--color-primary-light); padding: 2px 8px; border-radius: 999px;
}
.q-points { font-size: 12px; color: var(--color-text-muted); }
.q-text { font-size: 15px; font-weight: 500; line-height: 1.55; margin-bottom: 14px; }
.q-options { display: flex; flex-direction: column; gap: 8px; }
.q-option {
  display: flex; align-items: flex-start; gap: 10px;
  padding: 10px 14px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: var(--transition);
  background: var(--color-bg-primary);
}
.q-option:hover { border-color: var(--color-primary); }
.q-option.selected { border-color: var(--color-primary); background: var(--color-primary-light); }
.q-radio { margin-top: 2px; flex-shrink: 0; accent-color: var(--color-primary); }
.q-opt-text { font-size: 14px; line-height: 1.45; }
.hint { font-size: 12px; margin-top: 8px; }

/* 결과 */
.quiz-result { display: flex; flex-direction: column; gap: 16px; }
.result-score {
  display: flex; flex-direction: column; align-items: center;
  padding: 24px; border-radius: var(--radius-lg);
  text-align: center;
}
.result-score.passed { background: var(--color-success-light); border: 1px solid var(--color-success); }
.result-score.failed { background: #fff3f3; border: 1px solid var(--color-danger); }
.score-num { font-size: 2.2rem; font-weight: 800; }
.score-label { font-size: 1rem; font-weight: 600; margin-top: 6px; }
.result-summary { font-size: 14px; color: var(--color-text-secondary); text-align: center; }
.q-result-row {
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 14px 16px;
}
.q-result-header { display: flex; gap: 10px; align-items: flex-start; margin-bottom: 6px; }
.q-result-icon { font-size: 16px; font-weight: 700; flex-shrink: 0; }
.q-result-text { font-size: 14px; line-height: 1.5; }
.q-result-detail { font-size: 13px; color: var(--color-text-secondary); margin-bottom: 6px; padding-left: 26px; }
.q-answer-label { color: var(--color-text-muted); }
.q-explanation { font-size: 13px; color: var(--color-text-secondary); padding-left: 26px; line-height: 1.5; border-left: 3px solid var(--color-border); margin: 0; }

/* 주차 완료 배너 */
.week-complete-banner {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px 20px;
  background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
  border: 1px solid #f59e0b;
  border-radius: var(--radius-lg);
  margin-bottom: 8px;
}
.week-complete-icon {
  font-size: 28px;
  color: #f59e0b;
  flex-shrink: 0;
}
.week-complete-body { flex: 1; }
.week-complete-body strong { font-size: 15px; font-weight: 700; color: #92400e; }
.week-complete-body p { font-size: 13px; color: #78350f; margin: 4px 0 0; }
.report-btn { flex-shrink: 0; border-color: #f59e0b; color: #92400e; }
.report-btn:hover { background: #f59e0b; color: #fff; }

.state { padding: 40px 0; text-align: center; }
.muted { color: var(--color-text-muted); }
.error { color: var(--color-danger); }
</style>
