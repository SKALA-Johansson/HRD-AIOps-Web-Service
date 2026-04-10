<template>
  <div class="tutor-dock-root">
    <!-- 패널 (FAB 위로 펼침) -->
    <Transition name="panel">
      <div
        v-if="dock.isOpen"
        id="tutor-dock-panel"
        class="chat-panel"
        role="dialog"
        aria-labelledby="tutor-dock-title"
        aria-modal="true"
      >
        <header class="panel-head">
          <div>
            <h2 id="tutor-dock-title" class="panel-title">AI 튜터</h2>
            <p class="panel-sub">사내 RAG 기반 질의응답 · POST <code>/tutor/sessions</code></p>
          </div>
          <button type="button" class="icon-close" aria-label="닫기" @click="dock.close">×</button>
        </header>

        <div class="panel-settings">
          <label class="mini-label">curriculumId</label>
          <input v-model.number="form.curriculumId" type="number" class="mini-input" />
        </div>

        <div ref="threadEl" class="thread" aria-live="polite">
          <p v-if="!messages.length" class="thread-empty">
            학습·사내 규정에 대해 질문해 보세요. (예: 우리 팀 코딩 컨벤션은 뭐예요?)
          </p>
          <div
            v-for="(m, i) in messages"
            :key="i"
            class="bubble-wrap"
            :class="m.role"
          >
            <div class="bubble" :class="m.role">
              <p class="bubble-text">{{ m.text }}</p>
              <ul v-if="m.references?.length" class="bubble-refs">
                <li v-for="(r, j) in m.references" :key="j">{{ r.title }} — {{ r.source }}</li>
              </ul>
            </div>
          </div>
        </div>

        <div class="composer">
          <textarea
            v-model="draft"
            class="composer-input"
            rows="2"
            placeholder="메시지를 입력하세요…"
            @keydown.enter.exact.prevent="submit"
          />
          <button type="button" class="btn btn-primary btn-send" :disabled="loading || !draft.trim()" @click="submit">
            {{ loading ? '…' : '전송' }}
          </button>
        </div>
        <p v-if="error" class="composer-error">{{ error }}</p>
      </div>
    </Transition>

    <!-- 우하단 고정 FAB (뷰포트 기준 — 스크롤해도 같은 위치) -->
    <button
      type="button"
      class="fab"
      :class="{ 'is-open': dock.isOpen }"
      :aria-expanded="dock.isOpen"
      aria-controls="tutor-dock-panel"
      aria-label="AI 튜터 열기"
      @click="dock.toggle()"
    >
      <span class="fab-icon" aria-hidden="true">💬</span>
      <span class="fab-text">AI 튜터</span>
    </button>

    <!-- 열린 상태에서 바깥 클릭 시 닫기 -->
    <div v-if="dock.isOpen" class="backdrop" aria-hidden="true" @click="dock.close" />
  </div>
</template>

<script setup>
import { nextTick, reactive, ref, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { useTutorDockStore } from '@/store/tutorDock.js'
import { useAuthStore } from '@/store/auth.js'
import { tutorApi } from '@/api/tutor.js'

const dock = useTutorDockStore()
const { isOpen } = storeToRefs(dock)
const auth = useAuthStore()

const form = reactive({
  curriculumId: 301
})
const draft = ref('')
const loading = ref(false)
const error = ref('')
const messages = ref([])
const threadEl = ref(null)

watch(isOpen, async (open) => {
  if (open) {
    await nextTick()
    scrollThreadToEnd()
  }
})

function scrollThreadToEnd() {
  const el = threadEl.value
  if (el) el.scrollTop = el.scrollHeight
}

async function submit() {
  const q = draft.value.trim()
  if (!q || loading.value) return
  error.value = ''
  const uid = auth.user?.userId ?? 1
  messages.value.push({ role: 'user', text: q })
  draft.value = ''
  await nextTick()
  scrollThreadToEnd()
  loading.value = true
  try {
    const res = await tutorApi.ask({
      userId: uid,
      curriculumId: form.curriculumId,
      question: q
    })
    const d = res.data?.data
    messages.value.push({
      role: 'assistant',
      text: d?.answer ?? '(빈 응답)',
      references: d?.references ?? []
    })
  } catch (e) {
    error.value = e.response?.data?.message || e.message || '요청 실패'
    messages.value.push({
      role: 'assistant',
      text: `오류: ${error.value}`
    })
  } finally {
    loading.value = false
    await nextTick()
    scrollThreadToEnd()
  }
}
</script>

<style scoped>
.tutor-dock-root {
  position: relative;
  z-index: 240;
}

.backdrop {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.25);
  z-index: 241;
}

.chat-panel {
  position: fixed;
  right: 24px;
  bottom: 96px;
  width: min(400px, calc(100vw - 32px));
  max-height: min(560px, calc(100vh - 120px));
  display: flex;
  flex-direction: column;
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-lg);
  z-index: 243;
  overflow: hidden;
}

.panel-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  padding: 14px 16px;
  border-bottom: 1px solid var(--color-border);
  background: var(--color-bg-secondary);
}
.panel-title {
  font-size: 16px;
  font-weight: 700;
  margin-bottom: 4px;
}
.panel-sub {
  font-size: 11px;
  color: var(--color-text-muted);
  line-height: 1.4;
}
.panel-sub code {
  font-size: 10px;
  background: var(--color-bg-tertiary);
  padding: 1px 4px;
  border-radius: 3px;
}
.icon-close {
  width: 36px;
  height: 36px;
  border: none;
  background: transparent;
  font-size: 24px;
  line-height: 1;
  color: var(--color-text-secondary);
  border-radius: var(--radius-sm);
  cursor: pointer;
  flex-shrink: 0;
}
.icon-close:hover {
  background: var(--color-bg-tertiary);
  color: var(--color-text-primary);
}

.panel-settings {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border-bottom: 1px solid var(--color-border);
  font-size: 12px;
}
.mini-label {
  color: var(--color-text-muted);
  white-space: nowrap;
}
.mini-input {
  width: 88px;
  padding: 6px 8px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-size: 13px;
}

.thread {
  flex: 1;
  min-height: 200px;
  max-height: 320px;
  overflow-y: auto;
  padding: 12px 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.thread-empty {
  font-size: 13px;
  color: var(--color-text-muted);
  line-height: 1.5;
  margin: auto 0;
  text-align: center;
  padding: 16px 8px;
}

.bubble-wrap {
  display: flex;
}
.bubble-wrap.user {
  justify-content: flex-end;
}
.bubble-wrap.assistant {
  justify-content: flex-start;
}
.bubble {
  max-width: 90%;
  padding: 10px 12px;
  border-radius: 14px;
  font-size: 14px;
  line-height: 1.5;
}
.bubble.user {
  background: var(--color-primary);
  color: #fff;
  border-bottom-right-radius: 4px;
}
.bubble.assistant {
  background: var(--color-bg-tertiary);
  color: var(--color-text-primary);
  border-bottom-left-radius: 4px;
  border: 1px solid var(--color-border);
}
.bubble-text {
  white-space: pre-wrap;
  word-break: break-word;
}
.bubble-refs {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid var(--color-border);
  font-size: 12px;
  color: var(--color-text-secondary);
  list-style: disc;
  margin-left: 1rem;
}

.composer {
  display: flex;
  gap: 8px;
  padding: 12px 16px;
  border-top: 1px solid var(--color-border);
  background: var(--color-bg-secondary);
  align-items: flex-end;
}
.composer-input {
  flex: 1;
  resize: none;
  padding: 10px 12px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: 14px;
  font-family: inherit;
}
.btn-send {
  flex-shrink: 0;
  padding: 10px 16px;
}
.composer-error {
  padding: 0 16px 10px;
  font-size: 12px;
  color: var(--color-danger);
}

.fab {
  position: fixed;
  right: 24px;
  bottom: 24px;
  z-index: 244;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 14px 18px;
  border-radius: 999px;
  border: none;
  background: var(--color-primary);
  color: #fff;
  font-size: 15px;
  font-weight: 600;
  font-family: inherit;
  cursor: pointer;
  box-shadow: var(--shadow-md);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.fab:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
  background: var(--color-primary-dark);
}
.fab.is-open {
  background: var(--color-text-secondary);
}
.fab-icon {
  font-size: 18px;
  line-height: 1;
}

.panel-enter-active,
.panel-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.panel-enter-from,
.panel-leave-to {
  opacity: 0;
  transform: translateY(12px);
}

@media (max-width: 480px) {
  .fab-text {
    display: none;
  }
  .fab {
    padding: 14px;
    border-radius: 50%;
  }
  .chat-panel {
    right: 16px;
    bottom: 88px;
    width: calc(100vw - 24px);
  }
}
</style>
