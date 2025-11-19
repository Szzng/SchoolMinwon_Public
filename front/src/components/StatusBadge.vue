<template>
  <span :class="badgeClass">{{ status }}</span>
</template>

<script setup lang="ts">
const props = defineProps<{
  status:
    | '접수됨'
    | 'AI응답대기'
    | 'AI응답완료'
    | '1차완료'
    | '2차검토요청'
    | '교무실처리중'
    | '답변완료'
    | '종료됨'
}>()
const map: Record<string, string> = {
  접수됨: 'bg-blue-50 text-blue-700 ring-1 ring-blue-200',
  'AI응답대기': 'bg-purple-50 text-purple-700 ring-1 ring-purple-200',
  'AI응답완료': 'bg-cyan-50 text-cyan-700 ring-1 ring-cyan-200',
  '1차완료': 'bg-emerald-50 text-emerald-700 ring-1 ring-emerald-200',
  '2차검토요청': 'bg-yellow-50 text-yellow-700 ring-1 ring-yellow-200',
  '교무실처리중': 'bg-pink-50 text-pink-700 ring-1 ring-pink-200',
  '답변완료': 'bg-indigo-50 text-indigo-700 ring-1 ring-indigo-200',
  '종료됨': 'bg-gray-100 text-gray-700 ring-1 ring-gray-200',
}
const badgeClass = `inline-block rounded-full px-3 py-1 text-xs ${map[props.status] ?? 'bg-gray-100 text-gray-700 ring-1 ring-gray-200'}`
</script>
