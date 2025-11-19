<script setup lang="ts">
import StatusBadge from '@/components/StatusBadge.vue'
import RiskBadge from '@/components/RiskBadge.vue'
import RiskDetailPanel from '@/components/RiskDetailPanel.vue'
import SelectDropdown from '@/components/SelectDropdown.vue'
import {
  useComplaintStore,
  type Attachment,
  type ComplaintStatus,
  type Student,
} from '@/stores/complaint'
import { useAIReviewStore } from '@/stores/aiReview'
import { computed, ref, onMounted, watch } from 'vue'

const store = useComplaintStore()
const aiReviewStore = useAIReviewStore()

// 컴포넌트 마운트 시 데이터 불러오기
onMounted(async () => {
  try {
    console.log('Fetching complaints...')
    await store.fetchComplaints()
    console.log('Complaints loaded:', store.items.length)

    // AI 리뷰 데이터를 localStorage에서 로드
    aiReviewStore.loadFromStorage()
  } catch (error) {
    console.error('Failed to load complaints:', error)
  }
})

// 파일 다운로드
function downloadFile(file: Attachment) {
  const link = document.createElement('a')
  link.href = `data:${file.mime_type};base64,${file.file}`
  link.download = file.original_name
  link.click()
}

// 필터 및 검색
const searchQuery = ref('')
const statusFilter = ref<
  '모든 상태' | 'AI응답대기' | 'AI응답완료' | '2차검토요청' | '교무실처리중' | '답변완료' | '종료됨'
>('모든 상태')
const riskFilter = ref<'모두' | '검토필요' | '높은위험' | '일반'>('모두')
const sortBy = ref<'최신순' | '상태순' | '위험도순'>('최신순')

// 상세 보기
const selectedId = ref<string | null>(null)
const replyText = ref('')
const staffStatusChange = ref<'교무실처리중' | '답변완료' | null>(null)
const aiReviewResult = ref<{ content: string; originalContent: string; timestamp: string } | null>(
  null,
)
const isReviewLoading = ref(false)

const selected = computed(() => (selectedId.value ? store.getById(selectedId.value) : null))

// 민원 선택 시 상세 정보 로드
watch(selectedId, async (newId) => {
  if (newId) {
    try {
      await store.fetchComplaintDetail(newId)

      // localStorage에서 해당 민원의 AI 리뷰 결과 로드
      const savedReview = aiReviewStore.getReviewByComplaintId(newId)
      if (savedReview) {
        aiReviewResult.value = {
          content: savedReview.content,
          originalContent: savedReview.originalContent,
          timestamp: savedReview.timestamp,
        }
        console.log('AI review loaded from storage:', savedReview)
      } else {
        aiReviewResult.value = null
      }
    } catch (error) {
      console.error('Failed to load complaint detail:', error)
    }
  }
})

// 필터링된 목록
const filteredComplaints = computed(() => {
  let items = [...store.items]

  // 검색
  if (searchQuery.value.trim()) {
    const q = searchQuery.value.toLowerCase()
    items = items.filter(
      (c) =>
        c.title.toLowerCase().includes(q) ||
        c.author_name.toLowerCase().includes(q) ||
        c.content.toLowerCase().includes(q),
    )
  }

  // 상태 필터
  if (statusFilter.value !== '모든 상태') {
    items = items.filter((c) => c.status === statusFilter.value)
  }

  // 위험도 필터
  if (riskFilter.value === '검토필요') {
    items = items.filter((c) => c.ai_risk_detect?.needs_human_review)
  } else if (riskFilter.value === '높은위험') {
    items = items.filter((c) => (c.ai_risk_detect?.toxicity_score ?? 0) > 0.7)
  } else if (riskFilter.value === '일반') {
    items = items.filter(
      (c) =>
        !c.ai_risk_detect?.needs_human_review && (c.ai_risk_detect?.toxicity_score ?? 0) <= 0.7,
    )
  }

  // 정렬
  if (sortBy.value === '최신순') {
    items.sort((a, b) => +new Date(b.created_at) - +new Date(a.created_at))
  } else if (sortBy.value === '상태순') {
    const order: ComplaintStatus[] = [
      'AI응답대기',
      'AI응답완료',
      '1차완료',
      '2차검토요청',
      '교무실처리중',
      '답변완료',
      '종료됨',
    ]
    items.sort((a, b) => order.indexOf(a.status) - order.indexOf(b.status))
  } else if (sortBy.value === '위험도순') {
    items.sort((a, b) => {
      const aScore = a.ai_risk_detect?.toxicity_score ?? 0
      const bScore = b.ai_risk_detect?.toxicity_score ?? 0
      const aNeedsReview = a.ai_risk_detect?.needs_human_review ? 1 : 0
      const bNeedsReview = b.ai_risk_detect?.needs_human_review ? 1 : 0
      return bNeedsReview - aNeedsReview || bScore - aScore
    })
  }

  return items
})

// 통계
const stats = computed(() => {
  return {
    total: store.items.length,
    waiting: store.items.filter((c) => c.status === 'AI응답대기').length,
    aiResponded: store.items.filter((c) => c.status === 'AI응답완료').length,
    secondReview: store.items.filter((c) => c.status === '2차검토요청').length,
    processing: store.items.filter((c) => c.status === '교무실처리중').length,
    completed: store.items.filter((c) => c.status === '답변완료').length,
    closed: store.items.filter((c) => c.status === '종료됨' || c.status === '1차완료').length,
    needsReview: store.items.filter((c) => c.ai_risk_detect?.needs_human_review).length,
  }
})

// 댓글 추가 (기존 답변 함수 대체)
async function addComment() {
  if (!selected.value || !replyText.value.trim()) {
    console.warn('Comment submission blocked: missing selected or empty text')
    return
  }

  try {
    console.log('Adding comment to complaint:', selected.value.id)
    await store.addComment(
      selected.value.id,
      {
        type: 'staff',
        name: '교무실',
      },
      replyText.value.trim(),
    )
    console.log('Comment added successfully')
    replyText.value = ''
  } catch (error) {
    console.error('Failed to add comment:', error)
    alert('댓글 추가에 실패했습니다: ' + (error instanceof Error ? error.message : String(error)))
  }
}

// AI 리뷰 (작성 중인 댓글 리뷰)
async function reviewReply() {
  if (!selected.value) {
    console.warn('AI review blocked: no complaint selected')
    return
  }

  if (!replyText.value.trim()) {
    alert('검토할 댓글 내용을 입력하세요.')
    return
  }

  isReviewLoading.value = true
  try {
    console.log('Requesting AI review for complaint:', selected.value.id)
    const result = await store.reviewComplaintReply(selected.value.id, replyText.value.trim())
    console.log('AI review completed successfully:', result)

    // AI 리뷰 결과를 UI에 표시하고 localStorage에 저장
    if (result && result.aiReview) {
      const reviewContent = result.aiReview.content
      const originalContent = result.aiReview.original_content
      const reviewTimestamp = result.aiReview.created_at

      // UI에 표시
      aiReviewResult.value = {
        content: reviewContent,
        originalContent: originalContent,
        timestamp: reviewTimestamp,
      }

      // localStorage에 저장 (1회성이 아닌 지속적 저장)
      aiReviewStore.setReview(selected.value.id, reviewContent, originalContent, reviewTimestamp)
    } else {
      console.warn('No AI review data in response:', result)
    }
  } catch (error) {
    console.error('Failed to review reply:', error)
    alert('AI 리뷰에 실패했습니다: ' + (error instanceof Error ? error.message : String(error)))
  } finally {
    isReviewLoading.value = false
  }
}

// 상태 변경 (스토어 액션 사용)
async function changeStatus(status: ComplaintStatus) {
  if (!selected.value) return
  try {
    // 상태 변경 액션 맵핑
    const actionMap: Record<ComplaintStatus, string> = {
      AI응답대기: 'ai_response_wait',
      AI응답완료: 'ai_response_complete',
      '1차완료': 'first_complete',
      '2차검토요청': 'request_second_review',
      교무실처리중: 'start_office_processing',
      답변완료: 'response_complete',
      종료됨: 'close_by_staff',
    }

    const action = actionMap[status]
    await store.changeStatus(selected.value.id, action)
  } catch (error) {
    console.error('Failed to change status:', error)
  }
}

// 드롭다운에서 상태 변경
async function applyStatusChange() {
  if (!staffStatusChange.value || !selected.value) return
  await changeStatus(staffStatusChange.value)
  staffStatusChange.value = null
}

// 민원 종료 (교무실)
function closeComplaint() {
  if (!selected.value) return
  if (confirm('이 민원을 종료하시겠습니까?')) {
    store.closeComplaint(selected.value.id, 'staff')
  }
}

// 민원 삭제
function deleteComplaint(id: string) {
  if (confirm('정말 이 민원을 삭제하시겠습니까?')) {
    store.remove(id)
    // 해당 민원의 AI 리뷰도 함께 삭제
    aiReviewStore.deleteReview(id)
    selectedId.value = null
  }
}

// AI 리뷰 결과 삭제
function clearAIReview(id: string) {
  aiReviewStore.deleteReview(id)
  aiReviewResult.value = null
}

// 날짜 포매팅
function fmt(iso: string) {
  try {
    return new Intl.DateTimeFormat('ko-KR', {
      dateStyle: 'short',
      timeStyle: 'short',
    }).format(new Date(iso))
  } catch {
    return iso
  }
}

// 경과 시간 계산
function timeAgo(iso: string) {
  const now = new Date()
  const then = new Date(iso)
  const diffMs = now.getTime() - then.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)

  if (diffMins < 1) return '방금'
  if (diffMins < 60) return `${diffMins}분 전`
  if (diffHours < 24) return `${diffHours}시간 전`
  return `${diffDays}일 전`
}

// 상태별 색상
const statusColors: Record<ComplaintStatus, string> = {
  AI응답대기: 'bg-purple-100 text-purple-900 ring-1 ring-purple-300',
  AI응답완료: 'bg-cyan-100 text-cyan-900 ring-1 ring-cyan-300',
  '1차완료': 'bg-emerald-100 text-emerald-900 ring-1 ring-emerald-300',
  '2차검토요청': 'bg-yellow-100 text-yellow-900 ring-1 ring-yellow-300',
  교무실처리중: 'bg-pink-100 text-pink-900 ring-1 ring-pink-300',
  답변완료: 'bg-indigo-100 text-indigo-900 ring-1 ring-indigo-300',
  종료됨: 'bg-gray-100 text-gray-900 ring-1 ring-gray-300',
}

// 학생 정보 조회
function getStudentNames(students: Student[]) {
  return students.map((s) => `${s.name} (${s.grade}학년 ${s.classroom}반)`).join(', ')
}

// 카테고리 표시
const categoryColors: Record<string, string> = {
  교육과정: 'bg-blue-100 text-blue-700',
  급식: 'bg-orange-100 text-orange-700',
  시설: 'bg-gray-100 text-gray-700',
  학생지도: 'bg-green-100 text-green-700',
  행정: 'bg-purple-100 text-purple-700',
  안전: 'bg-red-100 text-red-700',
  학교폭력: 'bg-rose-100 text-rose-700',
  '체벌/인권': 'bg-pink-100 text-pink-700',
  학용품비: 'bg-indigo-100 text-indigo-700',
  방과후활동: 'bg-cyan-100 text-cyan-700',
  특수교육: 'bg-teal-100 text-teal-700',
  학부모소통: 'bg-emerald-100 text-emerald-700',
  기숙사: 'bg-yellow-100 text-yellow-700',
  교사태도: 'bg-violet-100 text-violet-700',
  '시험/평가': 'bg-lime-100 text-lime-700',
  '진로/진학': 'bg-fuchsia-100 text-fuchsia-700',
  기타: 'bg-slate-100 text-slate-700',
}
</script>

<template>
  <div class="grid gap-4 lg:grid-cols-2">
    <!-- 왼쪽: 민원 목록 -->
    <div class="lg:col-span-1">
      <!-- 헤더 -->
      <div
        class="rounded-2xl border border-indigo-200 bg-gradient-to-br from-indigo-50 to-blue-50 p-6 mb-4"
      >
        <div class="flex items-start gap-3">
          <div class="flex-shrink-0 text-3xl">⚙️</div>
          <div>
            <h1 class="text-2xl font-bold text-gray-900">관리 대시보드</h1>
            <p class="mt-1 text-sm text-gray-700">모든 민원을 한눈에 보고 효율적으로 처리합니다.</p>
          </div>
        </div>
      </div>

      <!-- 통계 카드 -->
      <div class="grid grid-cols-2 gap-3 sm:grid-cols-5 mb-4">
        <div class="rounded-lg border border-gray-200 bg-white p-3">
          <div class="text-2xl font-bold text-gray-900">{{ stats.total }}</div>
          <div class="mt-1 text-xs text-gray-600 font-medium">총 민원</div>
        </div>
        <div class="rounded-lg border border-purple-200 bg-purple-50 p-3">
          <div class="text-2xl font-bold text-purple-700">{{ stats.waiting }}</div>
          <div class="mt-1 text-xs text-purple-600 font-medium">AI 대기중</div>
        </div>
        <div class="rounded-lg border border-yellow-200 bg-yellow-50 p-3">
          <div class="text-2xl font-bold text-yellow-700">{{ stats.secondReview }}</div>
          <div class="mt-1 text-xs text-yellow-600 font-medium">2차검토 요청</div>
        </div>
        <div class="rounded-lg border border-emerald-200 bg-emerald-50 p-3">
          <div class="text-2xl font-bold text-emerald-700">{{ stats.closed }}</div>
          <div class="mt-1 text-xs text-emerald-600 font-medium">종료됨</div>
        </div>
        <div class="rounded-lg border border-red-200 bg-red-50 p-3">
          <div class="text-2xl font-bold text-red-700">{{ stats.needsReview }}</div>
          <div class="mt-1 text-xs text-red-600 font-medium">⚠️ 검토필요</div>
        </div>
      </div>

      <!-- 필터 & 검색 -->
      <div class="rounded-2xl border border-gray-200 bg-white p-4 mb-4">
        <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:gap-2">
          <input
            v-model.trim="searchQuery"
            type="search"
            placeholder="제목, 이름, 내용 검색..."
            class="flex-1 rounded-lg border border-gray-200 px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-indigo-500"
          />
          <SelectDropdown
            v-model="statusFilter"
            placeholder="상태 선택..."
            :options="[
              { value: '모든 상태', label: '모든 상태' },
              { value: 'AI응답대기', label: 'AI 응답 대기' },
              { value: 'AI응답완료', label: 'AI 응답 완료' },
              { value: '2차검토요청', label: '2차 검토 요청' },
              { value: '교무실처리중', label: '교무실 처리 중' },
              { value: '답변완료', label: '답변 완료' },
              { value: '종료됨', label: '종료됨' },
            ]"
            buttonClass="w-28"
          />
          <SelectDropdown
            v-model="sortBy"
            placeholder="정렬..."
            :options="[
              { value: '최신순', label: '최신순' },
              { value: '상태순', label: '상태순' },
              { value: '위험도순', label: '⚠️ 위험도순' },
            ]"
            buttonClass="w-28"
          />
        </div>
      </div>

      <!-- 민원 목록 -->
      <div class="space-y-2 max-h-[calc(100vh-400px)] overflow-y-auto">
        <div
          v-for="complaint in filteredComplaints"
          :key="complaint.id"
          class="rounded-lg border transition cursor-pointer"
          :class="
            selectedId === complaint.id
              ? 'border-indigo-500 bg-indigo-50'
              : 'border-gray-200 bg-white hover:border-gray-300 hover:shadow-sm'
          "
          @click="selectedId = complaint.id"
        >
          <div class="p-4">
            <div class="flex items-start justify-between gap-3">
              <div class="min-w-0 flex-1">
                <div class="font-medium text-gray-900 truncate">{{ complaint.title }}</div>
                <div class="mt-1 text-xs text-gray-600">
                  {{ complaint.author_name }} · {{ timeAgo(complaint.created_at) }}
                </div>
                <div class="mt-2 line-clamp-2 text-sm text-gray-700">{{ complaint.content }}</div>
              </div>
              <div class="flex-shrink-0 flex flex-col items-end gap-2">
                <StatusBadge :status="complaint.status" />
                <RiskBadge :risk-data="complaint.ai_risk_detect" />
              </div>
            </div>
          </div>
        </div>

        <div v-if="filteredComplaints.length === 0" class="text-center py-8 text-gray-500">
          <p class="text-sm">조건에 맞는 민원이 없습니다.</p>
        </div>
      </div>
    </div>

    <!-- 오른쪽: 상세 패널 -->
    <div class="lg:col-span-1">
      <div
        v-if="selected"
        class="sticky top-24 rounded-2xl border border-gray-200 bg-white shadow-sm max-h-[calc(100vh-120px)] flex flex-col"
      >
        <!-- 헤더 -->
        <div class="border-b border-gray-100 p-4">
          <div class="flex items-start justify-between gap-2">
            <div class="min-w-0 flex-1">
              <div class="flex space-x-2">
                <h3 class="font-semibold text-gray-900 truncate">{{ selected.title }}</h3>
                <div class="flex flex-wrap gap-1.5">
                  <span
                    v-for="cat in selected.categories || []"
                    :key="cat"
                    :class="[
                      'px-2.5 py-1 rounded text-xs font-medium',
                      categoryColors[cat] || 'bg-gray-100 text-gray-700',
                    ]"
                  >
                    {{ cat }}
                  </span>
                </div>
              </div>

              <div class="mt-1 text-xs text-gray-600">ID: {{ selected.id }}</div>
              <div class="mt-1 text-xs text-gray-600">접수: {{ fmt(selected.created_at) }}</div>
            </div>
            <StatusBadge :status="selected.status" />
          </div>
        </div>

        <!-- 스크롤 가능한 콘텐츠 -->
        <div class="flex-1 overflow-y-auto">
          <!-- 민원인 정보 -->
          <div class="border-b border-gray-100 p-4">
            <div class="text-xs font-semibold uppercase tracking-wide text-gray-700 mb-3">
              민원인 정보
            </div>
            <div class="space-y-1.5">
              <div class="flex items-center gap-4">
                <span class="text-xs text-gray-600">이름</span>
                <div class="font-medium text-sm text-gray-900">{{ selected.author_name }}</div>
              </div>

              <div v-if="(selected.children?.length ?? 0) > 0">
                <div class="flex items-center gap-4">
                  <span class="text-xs text-gray-600">대상 학생</span>
                  <div class="text-sm text-gray-900 font-medium">
                    {{ getStudentNames(selected.children || []) }}
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 민원 내용 -->
          <div class="border-b border-gray-100 p-4">
            <div class="text-xs font-semibold uppercase tracking-wide text-gray-700 mb-3">내용</div>
            <div class="whitespace-pre-wrap text-sm text-gray-700 bg-gray-50 rounded-lg p-3">
              {{ selected.content }}
            </div>
          </div>

          <!-- AI 위험도 분석 -->
          <RiskDetailPanel :risk-data="selected.ai_risk_detect" />

          <!-- AI 응답 -->
          <div v-if="selected.ai_response" class="border-b border-gray-100 p-4">
            <div class="text-xs font-semibold uppercase tracking-wide text-gray-700 mb-3">
              🤖 AI 초기 응답
            </div>
            <div class="rounded-lg border border-cyan-200 bg-cyan-50 p-3">
              <div class="whitespace-pre-wrap text-xs text-gray-800 leading-relaxed">
                {{ selected.ai_response.content }}
              </div>
              <div class="mt-2 text-xs text-cyan-600">
                {{ fmt(selected.ai_response.generatedAt) }}
              </div>
            </div>
          </div>

          <!-- 첨부파일 -->
          <div v-if="(selected.attachments?.length ?? 0) > 0" class="border-b border-gray-100 p-4">
            <div class="text-xs font-semibold uppercase tracking-wide text-gray-700 mb-3">
              첨부파일
            </div>
            <div class="space-y-2">
              <div
                v-for="file in selected.attachments || []"
                :key="file.id"
                class="flex items-center justify-between rounded-lg bg-gray-50 p-2.5 text-xs border border-gray-200"
              >
                <div class="flex items-center gap-2 min-w-0 flex-1">
                  <svg
                    class="h-4 w-4 text-indigo-600 flex-shrink-0"
                    viewBox="0 0 20 20"
                    fill="currentColor"
                    aria-hidden="true"
                  >
                    <path
                      fill-rule="evenodd"
                      d="M8 16.5a1 1 0 01-1-1V4a1 1 0 011-1h3.5a1 1 0 011 1v11.5a1 1 0 01-1 1h-3.5zm5-11.5a.5.5 0 01.5-.5H15a1 1 0 011 1v11.5a1 1 0 01-1 1h-1.5a.5.5 0 01-.5-.5V4.5z"
                      clip-rule="evenodd"
                    />
                  </svg>
                  <div class="min-w-0 flex-1">
                    <div class="truncate font-medium text-gray-900">{{ file.original_name }}</div>
                    <div class="text-gray-600">{{ (file.size / 1024).toFixed(1) }} KB</div>
                  </div>
                </div>
                <button
                  @click="downloadFile(file)"
                  class="ml-2 text-indigo-600 hover:text-indigo-700 transition flex-shrink-0"
                  title="다운로드"
                >
                  <svg class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                    <path
                      fill-rule="evenodd"
                      d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z"
                      clip-rule="evenodd"
                    />
                  </svg>
                </button>
              </div>
            </div>
          </div>

          <!-- 히스토리 -->
          <div class="border-b border-gray-100 p-4">
            <div class="text-xs font-semibold uppercase tracking-wide text-gray-700 mb-3">
              처리 이력
            </div>
            <div class="space-y-2 max-h-40 overflow-y-auto">
              <div
                v-for="h in selected.history || []"
                :key="h.at"
                class="rounded-lg bg-gray-50 p-2.5 text-xs"
              >
                <div class="flex items-center justify-between gap-2">
                  <span :class="['px-2 py-1 rounded text-xs font-medium', statusColors[h.status]]">
                    {{ h.status }}
                  </span>
                  <span class="text-gray-600">{{ fmt(h.at) }}</span>
                </div>
                <div v-if="h.note" class="mt-1 text-gray-700">{{ h.note }}</div>
              </div>
            </div>
          </div>

          <!-- 댓글 목록 -->
          <div v-if="(selected.comments?.length ?? 0) > 0" class="border-b border-gray-100 p-4">
            <div class="text-xs font-semibold uppercase tracking-wide text-gray-700 mb-3">
              💬 댓글 ({{ selected.comments?.length ?? 0 }})
            </div>
            <div class="space-y-2 max-h-48 overflow-y-auto">
              <div
                v-for="comment in selected.comments || []"
                :key="comment.id"
                class="rounded-lg bg-gray-50 border border-gray-200 p-3"
              >
                <div class="flex items-start gap-2">
                  <div
                    :class="[
                      'inline-flex h-6 w-6 items-center justify-center rounded-full text-xs font-bold flex-shrink-0',
                      comment.author_type === 'ai'
                        ? 'bg-purple-200 text-purple-700'
                        : comment.author_type === 'staff'
                          ? 'bg-orange-200 text-orange-700'
                          : 'bg-blue-200 text-blue-700',
                    ]"
                  >
                    {{
                      comment.author_type === 'ai'
                        ? '🤖'
                        : comment.author_type === 'staff'
                          ? '👨‍💼'
                          : '👤'
                    }}
                  </div>
                  <div class="flex-1 min-w-0">
                    <div class="flex items-center gap-2 mb-1">
                      <span class="text-xs font-semibold text-gray-900">{{
                        comment.author_name
                      }}</span>
                      <span class="text-xs px-1.5 py-0.5 rounded bg-gray-100 text-gray-600">
                        {{
                          comment.author_type === 'ai'
                            ? 'AI'
                            : comment.author_type === 'staff'
                              ? '교무실'
                              : '민원인'
                        }}
                      </span>
                    </div>
                    <div
                      class="text-xs text-gray-700 whitespace-pre-wrap leading-relaxed break-words"
                    >
                      {{ comment.content }}
                    </div>
                    <div class="mt-1.5 text-xs text-gray-500">{{ fmt(comment.created_at) }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 상태 변경 -->
          <div class="border-b border-gray-100 p-4">
            <div class="text-xs font-semibold uppercase tracking-wide text-gray-700 mb-3">
              상태 관리
            </div>
            <div class="space-y-2">
              <div class="flex items-center w-full">
                <div class="flex items-center gap-2 text-xs text-gray-600 mb-2 w-1/3">
                  현재:
                  <span
                    :class="[
                      'inline-block px-2.5 py-1 rounded text-xs font-medium',
                      statusColors[selected.status],
                    ]"
                    >{{ selected.status }}</span
                  >
                </div>

                <div class="flex w-2/3 items-center gap-2">
                  <SelectDropdown
                    v-model="staffStatusChange"
                    placeholder="상태 선택..."
                    :options="[
                      { value: null, label: '상태 선택...' },
                      ...(selected.status !== '2차검토요청'
                        ? [{ value: '2차검토요청', label: '2차검토요청' }]
                        : []),
                      ...(selected.status !== '교무실처리중'
                        ? [{ value: '교무실처리중', label: '교무실 처리 중' }]
                        : []),
                      ...(selected.status !== '답변완료'
                        ? [{ value: '답변완료', label: '답변 완료' }]
                        : []),
                    ]"
                    buttonClass="w-60"
                  />

                  <button
                    @click="applyStatusChange"
                    :disabled="!staffStatusChange"
                    class="w-20 rounded-lg bg-indigo-600 px-3 py-2 text-xs font-medium text-white hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
                  >
                    변경
                  </button>
                </div>
              </div>

              <div class="text-xs text-gray-500 bg-blue-50 rounded p-2 border border-blue-100">
                💡 댓글 작성 시 '2차검토요청'에서 '교무실처리중'으로 자동 전환됩니다.
              </div>
            </div>
          </div>

          <!-- 댓글 입력 -->
          <div class="border-b border-gray-100 p-4">
            <div class="text-xs font-semibold uppercase tracking-wide text-gray-700 mb-3">
              댓글 추가
            </div>
            <div class="space-y-2">
              <textarea
                v-model="replyText"
                :disabled="selected.closed_by !== undefined && selected.closed_by !== null"
                placeholder="민원자와의 대화를 계속하세요..."
                rows="4"
                class="w-full rounded-lg border border-gray-200 px-3 py-2 text-xs outline-none focus:ring-2 focus:ring-indigo-500 resize-none disabled:bg-gray-100 disabled:cursor-not-allowed"
              />
              <div class="flex gap-2">
                <button
                  @click="addComment"
                  :disabled="
                    !replyText.trim() ||
                    (selected.closed_by !== undefined && selected.closed_by !== null)
                  "
                  class="flex-1 rounded-lg bg-indigo-600 px-3 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
                >
                  댓글 작성
                </button>
                <button
                  @click="reviewReply"
                  :disabled="
                    isReviewLoading ||
                    (selected.closed_by !== undefined && selected.closed_by !== null)
                  "
                  class="flex-1 rounded-lg bg-purple-600 px-3 py-2 text-sm font-medium text-white hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition inline-flex items-center justify-center gap-2"
                  title="교무실 댓글에 대한 AI 리뷰를 요청합니다"
                >
                  <span
                    v-if="isReviewLoading"
                    class="inline-block h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent"
                  ></span>
                  <span>{{ isReviewLoading ? '검토중...' : '🤖 AI 리뷰' }}</span>
                </button>
              </div>
            </div>
          </div>

          <!-- AI 리뷰 결과 -->
          <div v-if="aiReviewResult" class="border-b border-gray-100 p-4">
            <div class="text-xs font-semibold uppercase tracking-wide text-gray-700 mb-3">
              🤖 AI 리뷰 결과
            </div>
            <div class="rounded-lg border border-purple-200 bg-purple-50 p-3 space-y-3">
              <!-- 리뷰 대상이었던 원문 -->
              <div v-if="aiReviewResult.originalContent" class="border-b border-purple-200 pb-3">
                <div class="text-xs font-semibold text-purple-700 mb-2">📝 검토 대상 댓글</div>
                <div
                  class="text-xs text-gray-700 whitespace-pre-wrap leading-relaxed break-words bg-white rounded p-2"
                >
                  {{ aiReviewResult.originalContent }}
                </div>
              </div>
              <!-- AI 리뷰 내용 -->
              <div>
                <div class="text-xs font-semibold text-purple-700 mb-2">💬 AI 리뷰</div>
                <div class="text-xs text-gray-700 whitespace-pre-wrap leading-relaxed break-words">
                  {{ aiReviewResult.content }}
                </div>
              </div>
              <div class="text-xs text-purple-600 flex items-center justify-between">
                <span>{{ fmt(aiReviewResult.timestamp) }}</span>
                <button
                  @click="clearAIReview(selected!.id)"
                  class="text-purple-600 hover:text-purple-700 transition"
                  title="리뷰 삭제"
                >
                  ✕
                </button>
              </div>
            </div>
          </div>

          <!-- 종료 버튼 -->
          <div v-if="selected.status === '답변완료'" class="border-b border-gray-100 p-4">
            <button
              @click="closeComplaint"
              :disabled="selected.closed_by !== undefined"
              class="w-full rounded-lg bg-gray-700 px-3 py-2 text-sm font-medium text-white hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed transition"
            >
              ✓ 민원 종료하기
            </button>
          </div>
        </div>

        <!-- 푸터 -->
        <div class="border-t border-gray-100 p-4">
          <button
            @click="deleteComplaint(selected.id)"
            class="w-full rounded-lg border border-rose-200 bg-rose-50 px-3 py-2 text-sm font-medium text-rose-700 hover:bg-rose-100 transition"
          >
            삭제
          </button>
        </div>
      </div>

      <!-- 선택 안 됨 -->
      <div
        v-else
        class="rounded-2xl border border-dashed border-gray-200 bg-gray-50 p-8 text-center lg:sticky lg:top-24"
      >
        <div class="text-4xl mb-3">👈</div>
        <p class="text-sm text-gray-600">왼쪽 목록에서 민원을 선택하여</p>
        <p class="text-sm text-gray-600">상세 정보를 확인하고 처리하세요.</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

:deep(.animate-spin) {
  animation: spin 1s linear infinite;
}
</style>
