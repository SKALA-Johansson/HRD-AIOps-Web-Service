<template>
  <router-link v-if="to" :to="to" class="course-card is-link">
    <div class="thumb" :class="thumbClass">
      <span v-if="badge" class="thumb-badge">{{ badge }}</span>
      <img v-if="imageUrl" :src="imageUrl" :alt="title" class="thumb-img" loading="lazy" />
    </div>
    <div class="body">
      <p class="title">{{ title }}</p>
      <p class="sub">{{ subtitle }}</p>
    </div>
  </router-link>
  <div v-else class="course-card">
    <div class="thumb" :class="thumbClass">
      <span v-if="badge" class="thumb-badge">{{ badge }}</span>
      <img v-if="imageUrl" :src="imageUrl" :alt="title" class="thumb-img" loading="lazy" />
    </div>
    <div class="body">
      <p class="title">{{ title }}</p>
      <p class="sub">{{ subtitle }}</p>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  title: { type: String, required: true },
  subtitle: { type: String, default: '' },
  to: { type: [String, Object], default: null },
  imageUrl: { type: String, default: '' },
  paletteIndex: { type: Number, default: 0 },
  badge: { type: String, default: '' }
})

/** 이미지 없을 때만 global.css의 SK 계열 .course-grad-* 적용 */
const thumbClass = computed(() => {
  if (props.imageUrl) return ''
  const i = Math.abs(props.paletteIndex) % 5
  return `course-grad-${i}`
})
</script>

<style scoped>
.course-card {
  display: block;
  width: 240px;
  flex-shrink: 0;
  border-radius: var(--radius-lg);
  overflow: hidden;
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-sm);
  transition: var(--transition);
  text-align: left;
  color: inherit;
}
.course-card.is-link:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-md);
  border-color: var(--color-primary);
}
.thumb {
  position: relative;
  aspect-ratio: 16 / 9;
  overflow: hidden;
  background: var(--color-bg-tertiary);
}
.thumb-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.thumb-badge {
  position: absolute;
  top: 8px;
  left: 8px;
  z-index: 1;
  font-size: 11px;
  font-weight: 600;
  padding: 4px 8px;
  border-radius: 6px;
  background: rgba(0, 0, 0, 0.55);
  color: #fff;
}
.body {
  padding: 12px 14px 16px;
}
.title {
  font-size: 14px;
  font-weight: 700;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  margin-bottom: 6px;
  letter-spacing: -0.2px;
}
.sub {
  font-size: 12px;
  color: var(--color-text-muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
