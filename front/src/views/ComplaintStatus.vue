<script setup lang="ts">
import StatusBadge from '@/components/StatusBadge.vue'
import SelectDropdown from '@/components/SelectDropdown.vue'
import { useComplaintStore } from '@/stores/complaint'
import { useAuthStore } from '@/stores/auth'
import { computed, ref, onMounted } from 'vue'

const store = useComplaintStore()
const authStore = useAuthStore()

// 검색/필터/정렬
const q = ref('')
const statusFilter = ref<'모든 상태' | 'AI응답완료' | '2차검토요청' | '답변완료' | '종료됨'>(
  '모든 상태',
)
const sortKey = ref<'최신순' | '상태순'>('최신순')
const isLoading = ref(false)
const error = ref<string | null>(null)

// 데이터 로드
onMounted(async () => {
  // 인증 확인
  if (!authStore.isAuthenticated) {
    error.value = '로그인이 필요합니다.'
    return
  }

  isLoading.value = true
  error.value = null
  try {
    await store.fetchComplaints()
  } catch (err: any) {
    error.value = err.message || '민원을 불러오는 데 실패했습니다.'
    console.error('Failed to fetch complaints:', err)
  } finally {
    isLoading.value = false
  }
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

function initFilters() {
  q.value = ''
  statusFilter.value = '모든 상태'
  sortKey.value = '최신순'
}

// 목록 필터링/정렬
const filteredItems = computed(() => {
  const term = q.value.trim().toLowerCase()
  let items = store.items.filter((c) => {
    const okStatus = statusFilter.value === '모든 상태' ? true : c.status === statusFilter.value
    const okSearch =
      !term ||
      c.title.toLowerCase().includes(term) ||
      c.author_name.toLowerCase().includes(term) ||
      c.content.toLowerCase().includes(term)
    return okStatus && okSearch
  })

  if (sortKey.value === '최신순') {
    items = items.slice().sort((a, b) => +new Date(b.created_at) - +new Date(a.created_at))
  } else if (sortKey.value === '상태순') {
    const order = [
      'AI응답대기',
      'AI응답완료',
      '1차완료',
      '2차검토요청',
      '교무실처리중',
      '답변완료',
      '종료됨',
    ]
    items = items.slice().sort((a, b) => order.indexOf(a.status) - order.indexOf(b.status))
  }
  return items
})
</script>

<template>
  <div class="grid gap-4">
    <!-- 헤더 -->
    <div class="rounded-2xl border border-sky-200 bg-gradient-to-br from-sky-50 to-blue-50 p-6">
      <div class="flex items-start gap-3">
        <div class="flex-shrink-0 text-3xl">📋</div>
        <div>
          <h1 class="text-2xl font-bold text-gray-900">민원 현황</h1>
          <p class="mt-1 text-sm text-gray-700">
            접수하신 민원의 처리 상황을 확인하실 수 있습니다.
          </p>
        </div>
      </div>
    </div>

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
        </div>
      </div>
    </div>

    <!-- 통계 요약 -->
    <template v-else>
      <div class="grid grid-cols-2 gap-3 sm:grid-cols-3">
        <div class="rounded-lg border border-purple-200 bg-purple-50 p-3">
          <div class="text-2xl font-bold text-purple-700">
            {{ store.items.filter((i) => i.status === 'AI응답완료').length }}
          </div>
          <div class="mt-1 text-xs text-purple-600 font-medium">AI응답완료</div>
        </div>
        <div class="rounded-lg border border-yellow-200 bg-yellow-50 p-3">
          <div class="text-2xl font-bold text-yellow-700">
            {{ store.items.filter((i) => i.status === '2차검토요청').length }}
          </div>
          <div class="mt-1 text-xs text-yellow-600 font-medium">2차검토요청</div>
        </div>
        <div class="rounded-lg border border-emerald-200 bg-emerald-50 p-3">
          <div class="text-2xl font-bold text-emerald-700">
            {{
              store.items.filter((i) => i.status === '1차완료' || i.closed_by !== undefined).length
            }}
          </div>
          <div class="mt-1 text-xs text-emerald-600 font-medium">종료됨</div>
        </div>
      </div>

      <!-- 필터 & 검색 -->
      <div class="rounded-2xl border border-gray-200 bg-white p-5">
        <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <h2 class="text-lg font-semibold text-gray-900">민원 목록</h2>

          <!-- 툴바 -->
          <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:gap-2">
            <!-- 검색 -->
            <input
              v-model.trim="q"
              type="search"
              placeholder="검색..."
              class="w-full rounded-xl border border-gray-200 px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-sky-500 sm:w-48"
              aria-label="검색"
            />
            <div class="flex items-center gap-2">
              <SelectDropdown
                v-model="statusFilter"
                placeholder="상태"
                :options="[
                  { value: '모든 상태', label: '전체' },
                  { value: 'AI응답완료', label: 'AI응답완료' },
                  { value: '2차검토요청', label: '2차검토요청' },
                  { value: '답변완료', label: '답변완료' },
                  { value: '종료됨', label: '종료됨' },
                ]"
                class="w-28"
              />
              <SelectDropdown
                v-model="sortKey"
                placeholder="정렬"
                :options="[
                  { value: '최신순', label: '최신순' },
                  { value: '상태순', label: '상태순' },
                ]"
                class="w-28"
              />
            </div>

            <!-- 액션 버튼 -->
            <div class="flex items-center gap-2">
              <button
                class="flex-1 sm:flex-auto inline-flex items-center justify-center rounded-xl border border-gray-200 bg-white px-3 py-2 text-xs sm:text-sm text-gray-700 hover:border-sky-500 hover:text-sky-700 transition"
                @click="initFilters"
                type="button"
                title="필터 및 검색 초기화"
              >
                초기화
              </button>
              <RouterLink
                :to="{ name: 'form' }"
                class="flex-1 sm:flex-auto inline-flex items-center justify-center rounded-xl bg-indigo-600 px-3 py-2 text-xs sm:text-sm font-semibold text-white shadow-sm hover:brightness-110 transition"
              >
                + 신청
              </RouterLink>
            </div>
          </div>
        </div>
      </div>

      <!-- 목록 -->
      <div class="grid gap-3">
        <div
          v-for="complaint in filteredItems"
          :key="complaint.id"
          :to="{ name: 'status-detail', params: { id: complaint.id } }"
          class="cursor-pointer rounded-2xl border border-gray-200 p-4 transition hover:-translate-y-[1px] hover:bg-gray-50 hover:shadow-sm"
          @click="$router.push({ name: 'status-detail', params: { id: complaint.id } })"
          role="button"
          tabindex="0"
          @keyup.enter="$router.push({ name: 'status-detail', params: { id: complaint.id } })"
          :aria-label="`민원 상세 보기: ${complaint.title}`"
        >
          <div class="flex items-start justify-between gap-3">
            <div class="min-w-0 flex-1">
              <div class="truncate font-semibold text-gray-900">{{ complaint.title }}</div>
              <div class="mt-1 line-clamp-2 text-sm text-gray-600">{{ complaint.content }}</div>
              <div class="mt-2 truncate text-xs text-gray-500">
                {{ complaint.author_name }} · {{ fmt(complaint.created_at) }}
              </div>
            </div>
            <div class="flex-shrink-0">
              <StatusBadge :status="complaint.status" />
            </div>
          </div>
        </div>

        <div
          v-if="filteredItems.length === 0"
          class="flex flex-col items-center justify-center rounded-2xl border border-dashed border-gray-200 py-16 px-4"
        >
          <div class="mb-3 text-4xl">📋</div>
          <p class="text-base font-semibold text-gray-900">조건에 맞는 민원이 없습니다.</p>
          <p class="mt-2 text-sm text-gray-600">
            {{
              q
                ? '검색 조건을 변경해보세요.'
                : store.items.length === 0
                  ? '첫 번째 민원을 신청해주세요.'
                  : '필터를 초기화해보세요.'
            }}
          </p>
        </div>
      </div>
    </template>
  </div>
</template>
