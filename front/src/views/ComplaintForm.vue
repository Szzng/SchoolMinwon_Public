<script setup lang="ts">
import SelectDropdown from '@/components/SelectDropdown.vue'
import { useComplaintStore, type ComplaintCategory } from '@/stores/complaint'
import { useAuthStore } from '@/stores/auth'
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { uploadAttachment } from '@/services/complaintApi'

const router = useRouter()
const store = useComplaintStore()
const authStore = useAuthStore()

type FormState = {
  studentIds: (number | string)[] // 복수 선택 (서버 ID)
  categories: ComplaintCategory[] // 카테고리 (배열 유지)
  title: string
  content: string
  website?: string
}
const form = reactive<FormState>({
  studentIds: [],
  categories: [],
  title: '',
  content: '',
  website: '',
})

// File attachment state
interface FileItem {
  file: File
  id: string
  progress: number
  status: 'pending' | 'uploading' | 'success' | 'error'
  errorMessage?: string
}

const attachedFiles = ref<FileItem[]>([])
const fileInputRef = ref<HTMLInputElement | null>(null)
const dragOverCount = ref(0)
const isUploadingFiles = ref(false)

// File constraints
const MAX_FILE_SIZE = 10 * 1024 * 1024 // 10MB
const MAX_FILES = 5
const ALLOWED_TYPES = [
  'image/jpeg',
  'image/png',
  'image/gif',
  'image/webp',
  'application/pdf',
  'application/msword',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'application/vnd.ms-excel',
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
  'text/plain',
]

function getFileTypeLabel(mimeType: string): string {
  if (mimeType.startsWith('image/')) return 'Image'
  if (mimeType === 'application/pdf') return 'PDF'
  if (mimeType.includes('word') || mimeType.includes('document')) return 'Document'
  if (mimeType.includes('sheet') || mimeType.includes('excel')) return 'Spreadsheet'
  if (mimeType === 'text/plain') return 'Text'
  return 'File'
}

function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i]
}

function validateFile(file: File): { valid: boolean; error?: string } {
  if (file.size > MAX_FILE_SIZE) {
    return { valid: false, error: `파일 크기가 10MB를 초과합니다. (${formatFileSize(file.size)})` }
  }
  if (!ALLOWED_TYPES.includes(file.type)) {
    return { valid: false, error: `지원하지 않는 파일 형식입니다. (${file.type || 'unknown'})` }
  }
  return { valid: true }
}

function addFiles(files: FileList | null) {
  if (!files) return

  const newFiles: FileItem[] = []
  for (let i = 0; i < files.length; i++) {
    const file = files.item(i)
    if (!file) continue

    // Check if file already exists
    if (attachedFiles.value.some((f) => f.file.name === file.name && f.file.size === file.size)) {
      continue
    }

    // Validate file
    const validation = validateFile(file)
    if (!validation.valid) {
      newFiles.push({
        file,
        id: Math.random().toString(36).substring(2),
        progress: 0,
        status: 'error',
        errorMessage: validation.error,
      })
      continue
    }

    newFiles.push({
      file,
      id: Math.random().toString(36).substring(2),
      progress: 0,
      status: 'pending',
    })
  }

  // Check total file count
  const totalFiles =
    attachedFiles.value.length + newFiles.filter((f) => f.status !== 'error').length
  if (totalFiles > MAX_FILES) {
    alert(`최대 ${MAX_FILES}개의 파일만 첨부할 수 있습니다.`)
    return
  }

  attachedFiles.value.push(...newFiles)
}

function removeFile(id: string) {
  attachedFiles.value = attachedFiles.value.filter((f) => f.id !== id)
}

function onFileInputChange(e: Event) {
  const input = e.target as HTMLInputElement
  addFiles(input.files)
  // Reset input
  input.value = ''
}

function onDragOver(e: DragEvent) {
  e.preventDefault()
  e.stopPropagation()
  dragOverCount.value++
}

function onDragLeave(e: DragEvent) {
  e.preventDefault()
  e.stopPropagation()
  dragOverCount.value = Math.max(0, dragOverCount.value - 1)
}

function onDrop(e: DragEvent) {
  e.preventDefault()
  e.stopPropagation()
  dragOverCount.value = 0
  addFiles(e.dataTransfer?.files || null)
}

async function uploadFiles(complaintId: string) {
  const filesToUpload = attachedFiles.value.filter(
    (f) => f.status === 'pending' || f.status === 'error',
  )

  if (filesToUpload.length === 0) return

  isUploadingFiles.value = true

  for (const fileItem of filesToUpload) {
    if (fileItem.status === 'error') continue

    fileItem.status = 'uploading'
    fileItem.progress = 0

    try {
      await uploadAttachment(complaintId, fileItem.file)
      fileItem.status = 'success'
      fileItem.progress = 100
    } catch (error: any) {
      fileItem.status = 'error'
      fileItem.errorMessage = error.message || '파일 업로드에 실패했습니다.'
    }
  }

  isUploadingFiles.value = false
}

// 민원 유형 목록
const categories: { value: ComplaintCategory; label: string; icon: string }[] = [
  { value: '교육과정', label: '교육과정', icon: '📚' },
  { value: '급식', label: '급식', icon: '🍽️' },
  { value: '시설', label: '시설', icon: '🏢' },
  { value: '학생지도', label: '학생지도', icon: '👨‍🏫' },
  { value: '행정', label: '행정', icon: '📋' },
  { value: '안전', label: '안전', icon: '🚨' },
  { value: '학교폭력', label: '학교폭력', icon: '⚠️' },
  { value: '체벌/인권', label: '체벌/인권', icon: '✋' },
  { value: '학용품비', label: '학용품비', icon: '💰' },
  { value: '방과후활동', label: '방과후활동', icon: '🎨' },
  { value: '특수교육', label: '특수교육', icon: '♿' },
  { value: '학부모소통', label: '학부모소통', icon: '💬' },
  { value: '기숙사', label: '기숙사', icon: '🏠' },
  { value: '교사태도', label: '교사태도', icon: '👥' },
  { value: '시험/평가', label: '시험/평가', icon: '📝' },
  { value: '진로/진학', label: '진로/진학', icon: '🎓' },
  { value: '기타', label: '기타', icon: '❓' },
]

// SelectDropdown options (매번 새로 생성하지 않도록 고정)
const categoryOptions = computed(() => [
  { value: null, label: '민원 유형을 선택해주세요' },
  ...categories.map((cat) => ({ value: cat.value, label: `${cat.icon} ${cat.label}` })),
])

const submitting = ref(false)
const touched = reactive<Record<keyof FormState, boolean>>({
  studentIds: false,
  categories: false,
  title: false,
  content: false,
  website: false,
})

// very light validations (프론트 임시 검사)
const errors = computed(() => {
  const e: Partial<Record<keyof FormState, string>> = {}
  // 사용자가 필드를 변경하거나 포커스 아웃한 경우에만 검증 표시
  if (touched.title && !form.title.trim()) e.title = '제목을 입력해 주세요.'
  if (touched.content && (!form.content.trim() || form.content.trim().length < 10)) {
    e.content = '내용을 10자 이상 입력해 주세요.'
  }
  return e
})
const isValid = computed(() => Object.keys(errors.value).length === 0)

// 자녀 목록 (인증 사용자 정보에서 로드)
const children = ref<Array<{ id: number; name: string; grade: number; classroom: number }>>([])
const loadingChildren = ref(false)

onMounted(async () => {
  if (authStore.isAuthenticated && authStore.user) {
    // 사용자 정보에서 자녀 목록 로드
    loadingChildren.value = true
    try {
      // 인증된 사용자의 자녀 정보 로드
      if (authStore.user.children && authStore.user.children.length > 0) {
        // 백엔드에서 제공하는 실제 child ID 사용
        children.value = authStore.user.children.map((child) => ({
          id: child.id,
          name: child.name,
          grade: child.grade,
          classroom: child.classroom,
        }))
      }
    } catch (err) {
      console.error('Failed to load children:', err)
    } finally {
      loadingChildren.value = false
    }
  }
})

// Draft autosave (localStorage)
const DRAFT_KEY = 'minwon_draft_v1'
onMounted(() => {
  try {
    const raw = localStorage.getItem(DRAFT_KEY)
    if (raw) {
      const saved = JSON.parse(raw)
      Object.assign(form, saved)
    }
  } catch {}
})
watch(
  form,
  (val) => {
    try {
      const { website, ...clean } = val // honeypot 제외하고 저장
      localStorage.setItem(DRAFT_KEY, JSON.stringify(clean))
    } catch {}
  },
  { deep: true },
)

async function onSubmit() {
  // honeypot: 봇이 채우면 막기
  if (form.website && form.website.trim().length > 0) return // 프론트 유효성 검사
  ;(Object.keys(touched) as (keyof FormState)[]).forEach((k) => (touched[k] = true))
  if (!isValid.value) return

  submitting.value = true
  try {
    const complaint = await store.create({
      title: form.title.trim(),
      content: form.content.trim(),
      categories: form.categories,
      children_ids: form.studentIds,
      website: form.website,
    })

    // 파일 업로드 (민원 생성 후)
    if (attachedFiles.value.length > 0) {
      await uploadFiles(complaint.id)
    }

    // 성공 시 임시저장 제거
    localStorage.removeItem(DRAFT_KEY)

    // 상세로 이동
    router.push({ name: 'status-detail', params: { id: complaint.id } })
  } catch (e) {
    console.error(e)
    alert('제출 중 문제가 발생했어요. 잠시 후 다시 시도해 주세요.')
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="grid gap-4">
    <!-- 헤더 카드 -->
    <div class="rounded-2xl border border-sky-200 bg-gradient-to-br from-sky-50 to-blue-50 p-6">
      <div class="flex items-start gap-3">
        <div class="flex-shrink-0 text-3xl">📝</div>
        <div>
          <h1 class="text-2xl font-bold text-gray-900">민원 접수</h1>
          <p class="mt-1 text-sm text-gray-700">
            학교 운영 관련 문제나 건의사항을 접수해주세요.<br class="hidden sm:inline" />
            작성 중인 내용은 자동으로 임시 저장됩니다.
          </p>
        </div>
      </div>
    </div>

    <!-- AI 응답 약속 카드 -->
    <div
      class="rounded-2xl border border-purple-200 bg-gradient-to-br from-purple-50 to-indigo-50 p-6"
    >
      <div class="flex items-start gap-3">
        <div class="flex-shrink-0 text-3xl">🤖</div>
        <div>
          <h2 class="text-base font-semibold text-purple-900">AI가 먼저 응답합니다</h2>
          <p class="mt-2 text-sm text-purple-700">
            접수 후 <strong>빠르게 AI가 초기 답변</strong>을 제공합니다. 만족하지 않으시면
            <strong>교무실 검토를 요청</strong>하실 수 있습니다.
          </p>
        </div>
      </div>
    </div>

    <!-- 메인 폼 카드 -->
    <div class="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
      <form @submit.prevent="onSubmit" class="grid gap-6" novalidate>
        <!-- 사용자 정보 (로그인된 사용자이므로 표시만) -->
        <div class="rounded-xl border border-blue-200 bg-blue-50 p-4">
          <div class="text-sm">
            <p class="font-medium text-blue-900">접수자: {{ authStore.user?.real_name }}</p>
            <p class="text-xs text-blue-700 mt-1">인증된 계정으로 민원이 접수됩니다.</p>
          </div>
        </div>

        <!-- 섹션: 민원 유형 & 자녀 정보 -->
        <fieldset class="grid gap-4 rounded-xl bg-gray-50/50 p-4 border border-gray-200/50">
          <legend class="text-sm font-semibold text-gray-700 px-1">민원 유형 & 자녀 정보</legend>

          <!-- 민원 유형 선택 (드롭다운) -->
          <div>
            <label class="mb-2 block text-sm font-medium text-gray-900">민원 유형</label>
            <SelectDropdown
              :model-value="form.categories[0] || null"
              @update:model-value="
                (val) => {
                  form.categories = val ? [val as ComplaintCategory] : []
                  touched.categories = true
                }
              "
              placeholder="민원 유형을 선택해주세요"
              :options="categoryOptions"
              button-class="w-full"
            />
          </div>

          <!-- 자녀 선택 (체크박스) -->
          <div>
            <label class="mb-3 block text-sm font-medium text-gray-900"
              >자녀 선택
              <span class="text-xs text-gray-500">(중복 선택 가능, 선택사항)</span></label
            >
            <div v-if="loadingChildren" class="text-sm text-gray-600">
              자녀 정보를 불러오는 중...
            </div>
            <div v-else-if="children.length > 0" class="grid grid-cols-1 sm:grid-cols-2 gap-2">
              <label
                v-for="child in children"
                :key="child.id"
                class="flex items-center gap-3 rounded-lg border-2 p-3 cursor-pointer transition"
                :class="
                  form.studentIds.includes(child.id)
                    ? 'border-indigo-500 bg-indigo-50'
                    : 'border-gray-200 bg-white hover:border-gray-300'
                "
              >
                <input
                  type="checkbox"
                  :value="child.id"
                  :checked="form.studentIds.includes(child.id)"
                  @change="
                    (e) => {
                      if ((e.target as HTMLInputElement).checked) {
                        form.studentIds.push(child.id)
                      } else {
                        form.studentIds = form.studentIds.filter((id) => id !== child.id)
                      }
                      touched.studentIds = true
                    }
                  "
                  class="h-4 w-4 text-indigo-600"
                />
                <div class="flex space-x-2 items-center">
                  <div class="text-sm font-medium text-gray-900">{{ child.name }}</div>
                  <div class="text-xs text-gray-600">
                    {{ child.grade }}학년 {{ child.classroom }}반
                  </div>
                </div>
              </label>
            </div>
            <div v-else class="rounded-lg bg-gray-50 p-3 text-sm text-gray-600">
              등록된 자녀가 없습니다.
              <RouterLink to="/settings" class="text-sky-600 hover:underline font-medium"
                >설정에서 자녀를 추가</RouterLink
              >할 수 있습니다.
            </div>
          </div>
        </fieldset>

        <!-- 섹션: 민원 내용 -->
        <fieldset class="grid gap-4 rounded-xl bg-gray-50/50 p-4 border border-gray-200/50">
          <legend class="text-sm font-semibold text-gray-700 px-1">민원 내용</legend>

          <!-- 제목 -->
          <div>
            <label for="title" class="mb-2 block text-sm font-medium text-gray-900"
              >제목 <span class="text-rose-500" aria-hidden="true">*</span></label
            >
            <input
              id="title"
              v-model.trim="form.title"
              @input="touched.title = true"
              :class="[
                'w-full rounded-xl border px-4 py-2.5 text-sm outline-none transition',
                'focus:ring-2 focus:ring-sky-500 focus:border-transparent',
                touched.title && errors.title
                  ? 'border-rose-300 bg-rose-50'
                  : 'border-gray-200 bg-white',
              ]"
              placeholder="예: 급식 관련 문의"
              required
              maxlength="80"
            />
            <div class="mt-2 flex items-center justify-between">
              <p
                v-if="touched.title && errors.title"
                class="text-xs font-medium text-rose-600 flex items-center gap-1"
              >
                <svg
                  class="w-3.5 h-3.5 flex-shrink-0"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                  aria-hidden="true"
                >
                  <path
                    fill-rule="evenodd"
                    d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
                    clip-rule="evenodd"
                  />
                </svg>
                {{ errors.title }}
              </p>
              <span v-else class="text-xs text-gray-500 font-medium"
                >{{ (form.title || '').length }}/80</span
              >
            </div>
          </div>

          <!-- 내용 -->
          <div>
            <label for="content" class="mb-2 block text-sm font-medium text-gray-900"
              >내용 <span class="text-rose-500" aria-hidden="true">*</span>
              <span class="ml-1 text-xs font-normal text-gray-500">(최소 10자)</span></label
            >
            <textarea
              id="content"
              v-model.trim="form.content"
              @input="touched.content = true"
              rows="8"
              :class="[
                'w-full rounded-xl border px-4 py-2.5 text-sm outline-none transition resize-none',
                'focus:ring-2 focus:ring-sky-500 focus:border-transparent font-mono text-sm leading-relaxed',
                touched.content && errors.content
                  ? 'border-rose-300 bg-rose-50'
                  : 'border-gray-200 bg-white',
              ]"
              placeholder="자세한 내용을 적어주세요.&#10;예: 발생 일시, 장소, 상황, 바라는 점 등"
              required
              maxlength="2000"
            />
            <div class="mt-2 flex items-center justify-between">
              <p
                v-if="touched.content && errors.content"
                class="text-xs font-medium text-rose-600 flex items-center gap-1"
              >
                <svg
                  class="w-3.5 h-3.5 flex-shrink-0"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                  aria-hidden="true"
                >
                  <path
                    fill-rule="evenodd"
                    d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
                    clip-rule="evenodd"
                  />
                </svg>
                {{ errors.content }}
              </p>
              <div v-else class="flex items-center gap-2">
                <!-- 진행도 바 -->
                <div class="h-1.5 w-32 bg-gray-200 rounded-full overflow-hidden">
                  <div
                    class="h-full transition-all"
                    :style="{ width: Math.min((form.content.length / 2000) * 100, 100) + '%' }"
                    :class="
                      form.content.length > 1900
                        ? 'bg-orange-400'
                        : form.content.length > 1500
                          ? 'bg-sky-400'
                          : 'bg-emerald-400'
                    "
                  />
                </div>
                <span class="text-xs text-gray-500 font-medium whitespace-nowrap"
                  >{{ (form.content || '').length }}/2000</span
                >
              </div>
            </div>
          </div>
        </fieldset>

        <!-- 섹션: 첨부파일 -->
        <fieldset class="grid gap-4 rounded-xl bg-gray-50/50 p-4 border border-gray-200/50">
          <legend class="text-sm font-semibold text-gray-700 px-1">첨부파일 (선택사항)</legend>

          <!-- 파일 업로드 영역 -->
          <div
            class="rounded-lg border-2 border-dashed transition cursor-pointer p-8"
            :class="
              dragOverCount > 0
                ? 'border-sky-500 bg-sky-50'
                : 'border-gray-300 bg-white hover:border-gray-400'
            "
            @dragover="onDragOver"
            @dragleave="onDragLeave"
            @drop="onDrop"
            @click="fileInputRef?.click()"
          >
            <input
              ref="fileInputRef"
              type="file"
              multiple
              class="hidden"
              @change="onFileInputChange"
              :accept="ALLOWED_TYPES.join(',')"
            />
            <div class="flex flex-col items-center gap-3 text-center">
              <svg
                class="w-8 h-8 text-gray-400"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                aria-hidden="true"
              >
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                <polyline points="17 8 12 3 7 8" />
                <line x1="12" y1="3" x2="12" y2="15" />
              </svg>
              <div>
                <p class="text-sm font-medium text-gray-900">
                  파일을 여기에 드래그하거나 클릭해 선택하세요
                </p>
                <p class="mt-1 text-xs text-gray-500">
                  최대 {{ MAX_FILES }}개, 파일당 최대 {{ formatFileSize(MAX_FILE_SIZE) }}
                </p>
              </div>
              <p class="text-xs text-gray-500">지원: 이미지, PDF, Word, Excel, 텍스트 파일</p>
            </div>
          </div>

          <!-- 첨부 파일 목록 -->
          <div v-if="attachedFiles.length > 0" class="grid gap-2">
            <p class="text-xs font-medium text-gray-700">
              첨부된 파일 ({{ attachedFiles.length }}/{{ MAX_FILES }})
            </p>
            <div class="space-y-2">
              <div
                v-for="fileItem in attachedFiles"
                :key="fileItem.id"
                class="flex items-start gap-3 rounded-lg border p-3 transition"
                :class="
                  fileItem.status === 'error'
                    ? 'border-rose-200 bg-rose-50'
                    : fileItem.status === 'success'
                      ? 'border-emerald-200 bg-emerald-50'
                      : 'border-gray-200 bg-white'
                "
              >
                <!-- 파일 정보 -->
                <div class="flex-1 min-w-0">
                  <div class="flex items-start gap-2">
                    <!-- 파일 아이콘 -->
                    <div
                      class="flex-shrink-0 w-8 h-8 rounded flex items-center justify-center text-xs font-semibold"
                      :class="{
                        'bg-blue-100 text-blue-700': fileItem.file.type.startsWith('image'),
                        'bg-red-100 text-red-700': fileItem.file.type === 'application/pdf',
                        'bg-purple-100 text-purple-700': fileItem.file.type.includes('word'),
                        'bg-green-100 text-green-700': fileItem.file.type.includes('sheet'),
                        'bg-gray-100 text-gray-700':
                          !fileItem.file.type.startsWith('image') &&
                          fileItem.file.type !== 'application/pdf' &&
                          !fileItem.file.type.includes('word') &&
                          !fileItem.file.type.includes('sheet'),
                      }"
                    >
                      {{ getFileTypeLabel(fileItem.file.type).substring(0, 1) }}
                    </div>
                    <!-- 파일명 및 크기 -->
                    <div class="flex-1 min-w-0">
                      <p class="text-sm font-medium text-gray-900 truncate">
                        {{ fileItem.file.name }}
                      </p>
                      <p class="text-xs text-gray-600">{{ formatFileSize(fileItem.file.size) }}</p>
                      <!-- 에러 메시지 -->
                      <p
                        v-if="fileItem.status === 'error' && fileItem.errorMessage"
                        class="text-xs text-rose-600 font-medium mt-1"
                      >
                        {{ fileItem.errorMessage }}
                      </p>
                    </div>
                  </div>

                  <!-- 업로드 진행률 -->
                  <div v-if="fileItem.status === 'uploading'" class="mt-2">
                    <div class="h-1.5 bg-gray-200 rounded-full overflow-hidden">
                      <div
                        class="h-full bg-sky-500 transition-all"
                        :style="{ width: fileItem.progress + '%' }"
                      />
                    </div>
                    <p class="text-xs text-gray-500 mt-1">{{ fileItem.progress }}%</p>
                  </div>

                  <!-- 상태 배지 -->
                  <div v-if="fileItem.status === 'success'" class="flex items-center gap-1 mt-2">
                    <svg
                      class="w-4 h-4 text-emerald-600"
                      viewBox="0 0 20 20"
                      fill="currentColor"
                      aria-hidden="true"
                    >
                      <path
                        fill-rule="evenodd"
                        d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                        clip-rule="evenodd"
                      />
                    </svg>
                    <span class="text-xs font-medium text-emerald-700">업로드 완료</span>
                  </div>
                </div>

                <!-- 삭제 버튼 -->
                <button
                  v-if="fileItem.status !== 'uploading' && fileItem.status !== 'success'"
                  type="button"
                  @click="removeFile(fileItem.id)"
                  class="flex-shrink-0 text-gray-400 hover:text-rose-600 transition"
                  aria-label="파일 제거"
                >
                  <svg class="w-5 h-5" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                    <path
                      fill-rule="evenodd"
                      d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                      clip-rule="evenodd"
                    />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </fieldset>

        <!-- honeypot (숨김) -->
        <div class="hidden">
          <label for="website">웹사이트</label>
          <input id="website" v-model="form.website" autocomplete="off" />
        </div>

        <!-- 유효성 피드백 -->
        <div
          v-if="Object.keys(touched).some((k) => touched[k as keyof FormState])"
          class="rounded-lg bg-blue-50 border border-blue-200 p-3"
        >
          <div class="flex items-start gap-2">
            <svg
              class="w-4 h-4 text-blue-600 flex-shrink-0 mt-0.5"
              viewBox="0 0 20 20"
              fill="currentColor"
              aria-hidden="true"
            >
              <path
                fill-rule="evenodd"
                d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
                clip-rule="evenodd"
              />
            </svg>
            <div class="text-xs text-blue-800">
              <p class="font-medium">필수 항목을 확인해주세요</p>
              <ul v-if="Object.keys(errors).length > 0" class="mt-1.5 space-y-1 text-blue-700">
                <li v-if="errors.title">• 제목</li>
                <li v-if="errors.content">• 내용 (최소 10자)</li>
              </ul>
            </div>
          </div>
        </div>

        <!-- 동작 버튼 -->
        <div class="flex flex-col sm:flex-row gap-2 sm:justify-end">
          <RouterLink
            :to="{ name: 'status' }"
            class="inline-flex items-center justify-center rounded-xl border border-gray-200 bg-white px-5 py-2.5 text-sm font-medium text-gray-700 transition hover:border-sky-300 hover:bg-sky-50"
          >
            목록으로 돌아가기
          </RouterLink>
          <button
            type="submit"
            class="inline-flex items-center justify-center rounded-xl bg-gradient-to-r from-sky-600 to-sky-700 px-6 py-2.5 text-sm font-semibold text-white shadow-md transition hover:from-sky-700 hover:to-sky-800 disabled:cursor-not-allowed disabled:opacity-60 disabled:shadow-none"
            :disabled="submitting || !isValid || isUploadingFiles"
            :aria-busy="submitting || isUploadingFiles ? 'true' : 'false'"
          >
            <svg
              v-if="submitting || isUploadingFiles"
              class="mr-2 h-4 w-4 animate-spin"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              aria-hidden="true"
            >
              <circle cx="12" cy="12" r="10" />
              <path d="M12 6v6l4 2" stroke-linecap="round" />
            </svg>
            <svg
              v-else
              class="mr-2 h-4 w-4"
              viewBox="0 0 20 20"
              fill="currentColor"
              aria-hidden="true"
            >
              <path
                fill-rule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                clip-rule="evenodd"
              />
            </svg>
            {{ submitting || isUploadingFiles ? '접수 중...' : '민원 접수' }}
          </button>
        </div>

        <!-- 안내 문구 -->
        <div
          class="rounded-lg bg-emerald-50 border border-emerald-200 p-3 text-xs text-emerald-800"
        >
          <p class="font-medium">✓ 작성 중인 내용은 자동으로 임시 저장됩니다.</p>
          <p class="mt-1">
            민원 접수 후,
            <RouterLink
              :to="{ name: 'status' }"
              class="font-semibold text-emerald-700 hover:underline"
              >민원 현황 페이지</RouterLink
            >에서 처리 진행 상황을 확인할 수 있습니다.
          </p>
        </div>
      </form>
    </div>
  </div>
</template>
