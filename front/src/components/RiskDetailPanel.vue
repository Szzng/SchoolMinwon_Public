<template>
  <div v-if="riskData" class="border-b border-gray-100 p-4">
    <div class="mb-3 text-xs font-semibold uppercase tracking-wide text-gray-700">🛡️ AI 위험도 분석</div>

    <div
      :class="[
        'space-y-3 rounded-lg border p-4',
        riskData.needs_human_review
          ? 'border-red-300 bg-red-50'
          : riskData.toxicity_score > 0.5
            ? 'border-orange-200 bg-orange-50'
            : 'border-gray-200 bg-gray-50',
      ]"
    >
      <!-- Risk indicators row -->
      <div class="flex flex-wrap items-center gap-3">
        <!-- Sentiment badge -->
        <span :class="sentimentClass">
          {{ sentimentLabel }}
        </span>

        <!-- Toxicity score -->
        <div class="flex items-center gap-2">
          <span class="text-xs text-gray-700">위험도:</span>
          <div class="flex items-center gap-1.5">
            <div class="h-2.5 w-24 overflow-hidden rounded-full bg-gray-200">
              <div
                :style="{ width: `${riskData.toxicity_score * 100}%` }"
                :class="toxicityBarClass"
                class="h-full transition-all duration-300"
              ></div>
            </div>
            <span class="text-xs font-semibold tabular-nums">
              {{ (riskData.toxicity_score * 100).toFixed(0) }}%
            </span>
          </div>
        </div>

        <!-- Human review flag -->
        <span
          v-if="riskData.needs_human_review"
          class="inline-flex items-center gap-1 rounded-full bg-red-200 px-2.5 py-1 text-xs font-bold text-red-900 ring-2 ring-red-400"
        >
          ⚠️ 즉시 검토 필요
        </span>
      </div>

      <!-- Staff notes -->
      <div v-if="riskData.notes_for_staff" class="border-t border-current border-opacity-10 pt-2">
        <div class="mb-1.5 text-xs font-semibold text-gray-900">📝 담당자 메모</div>
        <div class="rounded-lg border border-gray-200 bg-white p-3 text-sm leading-relaxed text-gray-800">
          {{ riskData.notes_for_staff }}
        </div>
      </div>

      <!-- Reasons -->
      <div v-if="riskData.reasons?.length" class="border-t border-current border-opacity-10 pt-2">
        <div class="mb-1.5 text-xs font-semibold text-gray-900">🔍 분석 근거</div>
        <ul class="space-y-1.5 rounded-lg border border-gray-200 bg-white p-3 text-xs text-gray-700">
          <li v-for="(reason, idx) in riskData.reasons" :key="idx" class="flex items-start gap-2">
            <span class="flex-shrink-0 text-gray-400">•</span>
            <span class="leading-relaxed">{{ reason }}</span>
          </li>
        </ul>
      </div>

      <!-- Timestamp -->
      <div v-if="riskData.generatedAt" class="border-t border-current border-opacity-10 pt-2 text-right text-xs text-gray-500">
        분석 시각: {{ formatDate(riskData.generatedAt) }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface RiskData {
  sentiment: 'very_negative' | 'negative' | 'neutral' | 'positive'
  toxicity_score: number
  reasons: string[]
  category: string
  needs_human_review: boolean
  notes_for_staff: string
  generatedAt?: string
}

const props = defineProps<{
  riskData: RiskData | null | undefined
}>()

const sentimentLabel = computed(() => {
  return {
    very_negative: '매우 부정적',
    negative: '부정적',
    neutral: '중립',
    positive: '긍정적',
  }[props.riskData?.sentiment ?? 'neutral']
})

const sentimentClass = computed(() => {
  const base = 'inline-flex items-center rounded px-2.5 py-1 text-xs font-semibold'
  const map: Record<string, string> = {
    very_negative: `${base} bg-red-200 text-red-900 ring-1 ring-red-400`,
    negative: `${base} bg-orange-200 text-orange-900 ring-1 ring-orange-400`,
    neutral: `${base} bg-gray-200 text-gray-900 ring-1 ring-gray-400`,
    positive: `${base} bg-green-200 text-green-900 ring-1 ring-green-400`,
  }
  return map[props.riskData?.sentiment ?? 'neutral'] ?? map.neutral
})

const toxicityBarClass = computed(() => {
  const score = props.riskData?.toxicity_score ?? 0
  if (score > 0.7) return 'bg-red-600'
  if (score > 0.4) return 'bg-orange-500'
  return 'bg-yellow-500'
})

function formatDate(iso: string): string {
  try {
    return new Intl.DateTimeFormat('ko-KR', {
      dateStyle: 'short',
      timeStyle: 'short',
    }).format(new Date(iso))
  } catch {
    return iso
  }
}
</script>
