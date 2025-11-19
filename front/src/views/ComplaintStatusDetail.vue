<script setup lang="ts">
import StatusBadge from '@/components/StatusBadge.vue'
import { useComplaintStore, type Attachment } from '@/stores/complaint'
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const store = useComplaintStore()
const route = useRoute()
const router = useRouter()

// 댓글 입력
const newComment = ref('')
const isSubmittingComment = ref(false)

// 페이지 로딩 상태
const isLoading = ref(true)
const error = ref<string | null>(null)

// AI 응답 폴링
const pollingInterval = ref<ReturnType<typeof setInterval> | null>(null)
const isPolling = ref(false)

// 파일 다운로드
function downloadFile(file: Attachment) {
  const link = document.createElement('a')
  link.href = file.file
  link.download = file.original_name
  link.click()
}

const current = computed(() => {
  const id = route.params.id as string | undefined
  return id ? store.getById(id) : undefined
})

// 폴링으로 AI 응답 자동 새로고침
function startPolling(id: string) {
  if (pollingInterval.value) return // 이미 폴링 중이면 반환

  isPolling.value = true
  const complaint = store.getById(id)

  // 상태가 AI응답대기가 아니면 폴링 시작 안함
  if (!complaint || complaint.status !== 'AI응답대기') {
    isPolling.value = false
    return
  }

  pollingInterval.value = setInterval(async () => {
    try {
      await store.fetchComplaintDetail(id)
      const updatedComplaint = store.getById(id)

      // AI 응답이 완료되면 폴링 중지
      if (updatedComplaint && updatedComplaint.status === 'AI응답완료') {
        stopPolling()
      }
    } catch (err) {
      console.error('Polling failed:', err)
    }
  }, 3000) // 3초마다 체크
}

function stopPolling() {
  if (pollingInterval.value) {
    clearInterval(pollingInterval.value)
    pollingInterval.value = null
    isPolling.value = false
  }
}

// 페이지 로드 시 데이터 가져오기
onMounted(async () => {
  const id = route.params.id as string | undefined
  if (!id) {
    error.value = '민원 ID를 찾을 수 없습니다.'
    isLoading.value = false
    return
  }

  try {
    isLoading.value = true
    error.value = null
    await store.fetchComplaintDetail(id)

    // AI 응답 대기 중이면 폴링 시작
    const complaint = store.getById(id)
    if (complaint && complaint.status === 'AI응답대기') {
      startPolling(id)
    }
  } catch (err: any) {
    error.value = err.message || '민원을 불러오는 데 실패했습니다.'
    console.error('Failed to load complaint:', err)
  } finally {
    isLoading.value = false
  }
})

// 컴포넌트 언마운트 시 폴링 중지
onUnmounted(() => {
  stopPolling()
})

function fmt(iso: string) {
  try {
    return new Intl.DateTimeFormat('ko-KR', { dateStyle: 'medium', timeStyle: 'short' }).format(
      new Date(iso),
    )
  } catch {
    return iso
  }
}

// 댓글 추가
function addComment() {
  if (!current.value || !newComment.value.trim()) return
  isSubmittingComment.value = true
  try {
    store.addComment(
      current.value.id,
      {
        type: 'user',
        name: current.value.author_name,
      },
      newComment.value.trim(),
    )
    newComment.value = ''
  } finally {
    isSubmittingComment.value = false
  }
}

// 1차 완료 (만족)
function markAsResolved() {
  if (!current.value) return
  if (confirm('이 민원을 1차 완료로 처리하시겠습니까?')) {
    store.markAsResolved(current.value.id)
  }
}

// 2차 검토 요청
function requestSecondReview() {
  if (!current.value) return
  if (confirm('추가 검토를 요청하시겠습니까? 교무실로 이관됩니다.')) {
    store.requestSecondReview(current.value.id)
  }
}

// 민원 종료
function closeComplaint() {
  if (!current.value) return
  if (current.value.status !== '답변완료') {
    alert('답변완료 상태에서만 민원을 종료할 수 있습니다.')
    return
  }
  if (confirm('이 민원을 종료하시겠습니까? 종료 후에는 더 이상 댓글을 작성할 수 없습니다.')) {
    store.closeComplaint(current.value.id, 'user')
  }
}

// AI 응답 대기 중인지 확인
function isWaitingForAI(status: string) {
  return status === 'AI응답대기'
}

// AI 응답 완료 후 선택지가 나타나는지 확인
function shouldShowResolutionOptions(status: string) {
  return status === 'AI응답완료'
}

async function copyId(id: string) {
  try {
    await navigator.clipboard.writeText(id)
    alert('ID가 복사되었습니다.')
  } catch {
    // noop
  }
}

function remove() {
  if (!current.value) return
  if (confirm('이 민원을 삭제하시겠습니까?')) {
    store.remove(current.value.id)
    router.push({ name: 'status' })
  }
}
</script>

<template>
  <div class="grid gap-4">
    <!-- 로딩 중 -->
    <div
      v-if="isLoading"
      class="rounded-2xl border border-gray-200 bg-white p-8 shadow-sm text-center"
    >
      <div class="flex items-center justify-center gap-2 mb-3">
        <svg
          class="h-6 w-6 text-blue-600 animate-spin"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
        >
          <circle cx="12" cy="12" r="10" />
          <path d="M12 6v6l4 2" stroke-linecap="round" />
        </svg>
        <span class="text-gray-600">민원을 불러오는 중...</span>
      </div>
    </div>

    <!-- 에러 표시 -->
    <div v-else-if="error" class="rounded-2xl border border-red-200 bg-red-50 p-6 shadow-sm">
      <div class="flex items-start gap-3">
        <div class="text-2xl">⚠️</div>
        <div>
          <p class="font-semibold text-red-900">오류 발생</p>
          <p class="text-sm text-red-700 mt-1">{{ error }}</p>
          <RouterLink
            :to="{ name: 'status' }"
            class="mt-4 inline-flex items-center justify-center rounded-xl border border-red-300 bg-white px-4 py-2 text-red-700 hover:border-red-500"
          >
            목록으로 돌아가기
          </RouterLink>
        </div>
      </div>
    </div>

    <!-- 상세 패널 -->
    <div v-else-if="current" class="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
      <div class="flex items-start justify-between gap-3">
        <div>
          <h2 class="text-lg font-semibold text-gray-900">{{ current.title }}</h2>
          <div class="mt-1 text-sm text-gray-500">
            <span class="mr-2">ID: {{ current.id }}</span>
            <button
              class="rounded-lg border border-gray-200 bg-white px-2 py-0.5 text-[11px] text-gray-700 hover:border-sky-500 hover:text-sky-700"
              @click="copyId(current.id)"
            >
              ID 복사
            </button>
            <span class="mx-2">·</span>
            접수일시: {{ fmt(current.createdAt) }}
          </div>
        </div>
        <StatusBadge :status="current.status" />
      </div>

      <div class="mt-6 grid gap-6">
        <!-- 민원인 정보 -->
        <div class="grid gap-3 rounded-xl bg-gradient-to-br from-sky-50 to-blue-50 p-4">
          <div class="text-xs font-semibold uppercase tracking-wide text-gray-700">민원인</div>
          <div class="flex items-center gap-2">
            <div
              class="inline-flex h-8 w-8 items-center justify-center rounded-full bg-sky-200 text-sm font-bold text-sky-900"
            >
              {{ current.author_name.charAt(0) }}
            </div>
            <div>
              <div class="font-semibold text-gray-900">{{ current.author_name }}</div>
              <div class="text-sm text-gray-600">연락처 정보는 별도 페이지에서 확인</div>
            </div>
          </div>
        </div>

        <!-- 내용 -->
        <div class="grid gap-3">
          <div class="text-xs font-semibold uppercase tracking-wide text-gray-700">민원 내용</div>
          <div
            class="rounded-xl border border-gray-200 bg-gray-50 p-5 leading-relaxed text-gray-900 whitespace-pre-wrap"
          >
            {{ current.content }}
          </div>
        </div>

        <!-- AI 응답 대기 중 -->
        <div
          v-if="isWaitingForAI(current.status)"
          class="grid gap-3 rounded-xl border border-purple-200 bg-purple-50 p-4"
        >
          <div class="flex items-center gap-2">
            <svg
              class="h-5 w-5 text-purple-600 animate-spin"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              aria-hidden="true"
            >
              <circle cx="12" cy="12" r="10" />
              <path d="M12 6v6l4 2" stroke-linecap="round" />
            </svg>
            <span class="font-semibold text-purple-900">AI가 초기 응답을 생성 중입니다...</span>
          </div>
          <p class="text-sm text-purple-800">
            잠시만 기다려주세요. 대부분 2-3초 이내에 완료됩니다.
          </p>
        </div>

        <!-- AI 응답 -->
        <div
          v-if="current.ai_response"
          class="grid gap-3 rounded-xl border border-cyan-200 bg-gradient-to-br from-cyan-50 to-blue-50 p-4"
        >
          <div class="flex items-start gap-3">
            <div class="flex-shrink-0 text-2xl">🤖</div>
            <div class="flex-1">
              <div class="text-xs font-semibold uppercase tracking-wide text-cyan-700 mb-2">
                AI 초기 응답
              </div>
              <div class="rounded-lg bg-white border border-cyan-100 p-3">
                <div class="whitespace-pre-wrap text-sm text-gray-800 leading-relaxed">
                  {{ current.ai_response.content }}
                </div>
              </div>
              <div class="mt-2 text-xs text-cyan-600">
                {{ fmt(current.ai_response.generatedAt) }}
              </div>
            </div>
          </div>
        </div>

        <!-- 1차/2차 선택지 (AI 응답 완료 후) -->
        <div
          v-if="shouldShowResolutionOptions(current.status)"
          class="grid gap-3 rounded-xl border border-yellow-200 bg-yellow-50 p-4"
        >
          <div class="text-sm font-semibold text-yellow-900">AI 응답으로 문제가 해결되셨나요?</div>
          <div class="flex gap-2">
            <button
              @click="markAsResolved"
              class="flex-1 rounded-lg bg-emerald-600 px-3 py-2 text-sm font-medium text-white hover:bg-emerald-700 transition"
            >
              ✓ 네, 해결됐습니다
            </button>
            <button
              @click="requestSecondReview"
              class="flex-1 rounded-lg bg-orange-600 px-3 py-2 text-sm font-medium text-white hover:bg-orange-700 transition"
            >
              🔄 추가 도움이 필요합니다
            </button>
          </div>
        </div>

        <!-- 첨부파일 -->
        <div v-if="current.attachments && current.attachments.length > 0" class="grid gap-3">
          <div class="text-xs font-semibold uppercase tracking-wide text-gray-700">첨부파일</div>
          <div class="space-y-2">
            <div
              v-for="file in current.attachments"
              :key="file.id"
              class="flex items-center gap-3 rounded-lg border border-gray-200 bg-white p-3"
            >
              <svg
                class="h-5 w-5 text-indigo-600 flex-shrink-0"
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
                <div class="truncate text-sm font-medium text-gray-900">
                  {{ file.original_name }}
                </div>
                <div class="text-xs text-gray-500">{{ (file.size / 1024).toFixed(1) }} KB</div>
              </div>
              <button
                @click="downloadFile(file)"
                class="ml-2 text-indigo-600 hover:text-indigo-700 transition flex-shrink-0"
                title="다운로드"
              >
                <svg class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
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

        <!-- 댓글 섹션 -->
        <div v-if="!current.closedBy" class="grid gap-3 rounded-xl bg-gray-50 p-4">
          <div class="text-xs font-semibold uppercase tracking-wide text-gray-700">댓글</div>

          <!-- 댓글 목록 -->
          <div
            v-if="current.comments && current.comments.length > 0"
            class="space-y-2 max-h-64 overflow-y-auto"
          >
            <div
              v-for="comment in current.comments"
              :key="comment.id"
              class="rounded-lg bg-white border border-gray-200 p-3"
            >
              <div class="flex items-start justify-between gap-2">
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
                  <div class="flex-1">
                    <div class="flex items-center gap-2">
                      <span class="font-medium text-sm text-gray-900">{{
                        comment.author_name
                      }}</span>
                      <span class="text-xs px-2 py-0.5 rounded bg-gray-100 text-gray-600">
                        {{
                          comment.author_type === 'ai'
                            ? 'AI'
                            : comment.author_type === 'staff'
                              ? '교무실'
                              : '민원인'
                        }}
                      </span>
                    </div>
                    <div class="mt-1 text-sm text-gray-700 whitespace-pre-wrap">
                      {{ comment.content }}
                    </div>
                    <div class="mt-1 text-xs text-gray-500">{{ fmt(comment.created_at) }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 댓글 입력 -->
          <div class="space-y-2 border-t border-gray-200 pt-3">
            <textarea
              v-model="newComment"
              :disabled="current.closed_by !== undefined && current.closed_by !== null"
              placeholder="댓글을 작성해주세요..."
              rows="3"
              class="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-indigo-500 resize-none disabled:bg-gray-100 disabled:cursor-not-allowed"
            />
            <button
              @click="addComment"
              :disabled="
                !newComment.trim() ||
                isSubmittingComment ||
                (current.closed_by !== undefined && current.closed_by !== null)
              "
              class="w-full rounded-lg bg-indigo-600 px-3 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
            >
              {{ isSubmittingComment ? '작성 중...' : '댓글 작성' }}
            </button>
          </div>
        </div>

        <!-- 종료됨 알림 -->
        <div
          v-if="current.closed_by"
          class="rounded-xl border border-gray-300 bg-gray-100 p-4 text-center"
        >
          <svg
            class="mx-auto h-6 w-6 text-gray-600 mb-2"
            viewBox="0 0 20 20"
            fill="currentColor"
            aria-hidden="true"
          >
            <path
              fill-rule="evenodd"
              d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
              clip-rule="evenodd"
            />
          </svg>
          <p class="font-semibold text-gray-700">이 민원은 종료되었습니다.</p>
          <p class="mt-1 text-sm text-gray-600">
            {{ current.closed_by === 'user' ? '민원인' : '교무실' }}이
            {{ fmt(current.closed_at || '') }}에 종료했습니다.
          </p>
        </div>

        <!-- 처리 진행도 -->
        <div class="grid gap-3">
          <div class="text-xs font-semibold uppercase tracking-wide text-gray-700">처리 진행도</div>
          <div class="space-y-3">
            <div v-for="(h, idx) in current.history" :key="h.at" class="flex gap-4">
              <!-- 타임라인 좌측 -->
              <div class="flex flex-col items-center">
                <div
                  :class="[
                    'h-8 w-8 rounded-full border-2 flex items-center justify-center text-xs font-bold',
                    idx === current.history.length - 1
                      ? 'border-emerald-500 bg-emerald-100 text-emerald-700'
                      : 'border-gray-300 bg-gray-100 text-gray-700',
                  ]"
                >
                  {{ idx + 1 }}
                </div>
                <div
                  v-if="idx < current.history.length - 1"
                  class="mt-1 h-8 w-0.5 bg-gradient-to-b from-gray-300 to-gray-200"
                ></div>
              </div>

              <!-- 타임라인 우측 -->
              <div class="pb-4 pt-1">
                <div class="font-semibold text-gray-900">{{ h.status }}</div>
                <div class="mt-1 text-sm text-gray-600">{{ h.note }}</div>
                <div class="mt-2 text-xs text-gray-500">{{ fmt(h.at) }}</div>
              </div>
            </div>
          </div>
        </div>

        <div class="mt-3 flex flex-wrap gap-2">
          <!-- 종료 버튼 (답변완료 상태에서만) -->
          <button
            v-if="current.status === '답변완료'"
            @click="closeComplaint"
            :disabled="current.closed_by !== undefined && current.closed_by !== null"
            class="inline-flex items-center justify-center rounded-xl bg-gray-700 px-4 py-2 text-white shadow-sm transition hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            ✓ 민원 종료하기
          </button>

          <!-- 기본 액션 버튼들 -->
          <button
            class="inline-flex items-center justify-center rounded-xl border border-gray-200 bg-white px-4 py-2 text-gray-700 hover:border-sky-500 hover:text-sky-700"
            @click="remove"
          >
            삭제
          </button>
          <RouterLink
            :to="{ name: 'status' }"
            class="inline-flex items-center justify-center rounded-xl border border-gray-200 bg-white px-4 py-2 text-gray-700 hover:border-sky-500 hover:text-sky-700"
          >
            목록으로
          </RouterLink>
        </div>
      </div>
    </div>

    <!-- 페이지 없음 -->
    <div v-else class="rounded-2xl border border-dashed border-gray-200 bg-gray-50 p-8 text-center">
      <div class="text-4xl mb-3">❌</div>
      <p class="text-sm text-gray-600">민원을 찾을 수 없습니다.</p>
      <RouterLink
        :to="{ name: 'status' }"
        class="mt-4 inline-flex items-center justify-center rounded-xl border border-gray-200 bg-white px-4 py-2 text-gray-700 hover:border-sky-500 hover:text-sky-700"
      >
        목록으로 돌아가기
      </RouterLink>
    </div>
  </div>
</template>
