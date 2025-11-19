<template>
  <span :class="badgeClasses">
    <span class="flex-shrink-0">{{ icon }}</span>
    <span>{{ label }}</span>
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface RiskData {
  needs_human_review: boolean
  toxicity_score: number
  sentiment: 'very_negative' | 'negative' | 'neutral' | 'positive'
}

const props = withDefaults(
  defineProps<{
    riskData: RiskData | null | undefined
    variant?: 'compact' | 'detailed'
  }>(),
  {
    variant: 'compact',
  },
)

const icon = computed(() => {
  // 데이터가 없으면 분석중
  if (!props.riskData) return '⏳'
  if (props.riskData.needs_human_review) return '⚠️'
  if ((props.riskData.toxicity_score ?? 0) > 0.5) return '⚡'
  return '✅'
})

const label = computed(() => {
  // 데이터가 없으면 분석중
  if (!props.riskData) return '분석중'
  if (props.riskData.needs_human_review) return '검토필요'
  if ((props.riskData.toxicity_score ?? 0) > 0.7) return '높음'
  if ((props.riskData.toxicity_score ?? 0) > 0.4) return '주의'
  return '안전'
})

const badgeClasses = computed(() => {
  const base = 'inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-semibold'

  // 데이터가 없으면 분석중 상태 표시
  if (!props.riskData) {
    return `${base} bg-gray-100 text-gray-700 ring-1 ring-gray-300 animate-pulse`
  }

  if (props.riskData.needs_human_review) {
    return `${base} bg-red-100 text-red-800 ring-1 ring-red-300`
  }
  if ((props.riskData.toxicity_score ?? 0) > 0.5) {
    return `${base} bg-orange-100 text-orange-800 ring-1 ring-orange-300`
  }
  return `${base} bg-green-100 text-green-800 ring-1 ring-green-300`
})
</script>
