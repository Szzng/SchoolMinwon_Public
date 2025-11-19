<script setup lang="ts">
import SelectDropdown from '@/components/SelectDropdown.vue'
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

// Form fields
const username = ref('')
const email = ref('')
const password = ref('')
const passwordConfirm = ref('')
const userType = ref<'PARENT' | 'TEACHER' | 'ADMIN'>('PARENT')
const realName = ref('')
const phone = ref('')
const schoolName = ref('')
const children = ref<Array<{ name: string; grade: number; classroom: number }>>([
  { name: '', grade: 1, classroom: 1 },
])

const showPassword = ref(false)
const showPasswordConfirm = ref(false)
const isSubmitting = ref(false)
const agreedToTerms = ref(false)

// Validation
const isPasswordValid = computed(() => password.value.length >= 8)
const isPasswordMatch = computed(() => password.value === passwordConfirm.value)
const isEmailValid = computed(() => email.value.includes('@') && email.value.includes('.'))

const isFormValid = computed(() => {
  const baseValid =
    username.value.trim() &&
    email.value.trim() &&
    isEmailValid.value &&
    isPasswordValid.value &&
    isPasswordMatch.value &&
    realName.value.trim() &&
    phone.value.trim() &&
    schoolName.value.trim() &&
    agreedToTerms.value

  // 학부모는 자녀 정보 필수
  if (userType.value === 'PARENT') {
    return baseValid && children.value.some((child) => child.name.trim())
  }

  return baseValid
})

async function handleSignUp() {
  if (!isFormValid.value) return

  isSubmitting.value = true
  try {
    await authStore.register(
      username.value,
      email.value,
      password.value,
      passwordConfirm.value,
      userType.value,
      realName.value,
      phone.value,
      schoolName.value,
      userType.value === 'PARENT' ? children.value : undefined,
    )
    // 회원가입 성공 후 대시보드로 이동
    router.push({ name: userType.value === 'PARENT' ? 'status' : 'staff' })
  } catch (err) {
    console.error('Sign up failed:', err)
  } finally {
    isSubmitting.value = false
  }
}

function addChild() {
  children.value.push({ name: '', grade: 1, classroom: 1 })
}

function removeChild(index: number) {
  if (children.value.length > 1) {
    children.value.splice(index, 1)
  }
}

function togglePasswordVisibility() {
  showPassword.value = !showPassword.value
}

function togglePasswordConfirmVisibility() {
  showPasswordConfirm.value = !showPasswordConfirm.value
}
</script>

<template>
  <div class="relative min-h-[calc(100vh-80px)] overflow-hidden">
    <!-- BACKGROUND -->
    <div class="absolute inset-0 -z-30 bg-gradient-to-b from-white via-slate-50/50 to-white"></div>

    <!-- Animated Gradient Orbs -->
    <div
      class="pointer-events-none absolute -top-40 -left-40 -z-20 h-[50rem] w-[50rem] rounded-full bg-gradient-to-br from-indigo-300/20 via-indigo-200/10 to-transparent blur-3xl"
    ></div>
    <div
      class="pointer-events-none absolute -bottom-40 -right-40 -z-20 h-[50rem] w-[50rem] rounded-full bg-gradient-to-tl from-cyan-300/15 via-blue-200/10 to-transparent blur-3xl"
    ></div>

    <!-- MAIN CONTENT -->
    <div class="mx-auto max-w-4xl px-6 py-12">
      <!-- Header -->
      <div class="mb-12 text-center">
        <h1
          class="bg-gradient-to-r from-indigo-600 via-purple-600 to-indigo-600 bg-clip-text text-4xl font-black text-transparent"
        >
          SchoolMinwon에 가입하세요
        </h1>
        <p class="mt-4 text-lg text-gray-600">간편한 민원 관리 시스템에 참여하세요</p>
      </div>

      <!-- Form Card -->
      <div
        class="mx-auto max-w-2xl rounded-2xl border border-gray-200/60 bg-white/80 p-8 shadow-lg backdrop-blur-sm"
      >
        <form @submit.prevent="handleSignUp" class="space-y-6">
          <!-- User Type Selection -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-3"> 사용자 유형 선택 * </label>
            <div class="grid grid-cols-3 gap-3">
              <label
                v-for="type in ['PARENT', 'TEACHER', 'ADMIN']"
                :key="type"
                class="relative flex cursor-pointer items-center"
              >
                <input
                  type="radio"
                  :value="type"
                  v-model="userType"
                  class="h-4 w-4 border-gray-300 text-indigo-600"
                />
                <span class="ml-3 text-sm font-medium text-gray-700">
                  {{ type === 'PARENT' ? '학부모' : type === 'TEACHER' ? '교사' : '관리자' }}
                </span>
              </label>
            </div>
          </div>

          <!-- Basic Info -->
          <div class="grid grid-cols-1 gap-5 md:grid-cols-2">
            <div>
              <label for="username" class="block text-sm font-medium text-gray-700 mb-2">
                아이디 *
              </label>
              <input
                id="username"
                v-model="username"
                type="text"
                placeholder="아이디를 입력하세요"
                class="w-full rounded-lg border border-gray-300 bg-white/50 px-4 py-2.5 text-sm text-gray-900 placeholder-gray-500 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200"
              />
            </div>

            <div>
              <label for="email" class="block text-sm font-medium text-gray-700 mb-2">
                이메일 *
              </label>
              <input
                id="email"
                v-model="email"
                type="email"
                placeholder="example@school.com"
                class="w-full rounded-lg border border-gray-300 bg-white/50 px-4 py-2.5 text-sm text-gray-900 placeholder-gray-500 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200"
              />
              <p v-if="email && !isEmailValid" class="mt-1 text-xs text-red-600">
                올바른 이메일 형식을 입력하세요
              </p>
            </div>
          </div>

          <!-- Real Name (all users) -->
          <div class="grid grid-cols-1 gap-5 md:grid-cols-2">
            <div class="md:col-span-2">
              <label for="realName" class="block text-sm font-medium text-gray-700 mb-2">
                실명 *
              </label>
              <input
                id="realName"
                v-model="realName"
                type="text"
                placeholder="홍길동"
                class="w-full rounded-lg border border-gray-300 bg-white/50 px-4 py-2.5 text-sm text-gray-900 placeholder-gray-500 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200"
              />
            </div>

            <div>
              <label for="phone" class="block text-sm font-medium text-gray-700 mb-2">
                연락처 *
              </label>
              <input
                id="phone"
                v-model="phone"
                type="tel"
                placeholder="010-1234-5678"
                class="w-full rounded-lg border border-gray-300 bg-white/50 px-4 py-2.5 text-sm text-gray-900 placeholder-gray-500 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200"
              />
            </div>

            <div>
              <label for="schoolName" class="block text-sm font-medium text-gray-700 mb-2">
                학교명 *
              </label>
              <input
                id="schoolName"
                v-model="schoolName"
                type="text"
                placeholder="예시초등학교"
                class="w-full rounded-lg border border-gray-300 bg-white/50 px-4 py-2.5 text-sm text-gray-900 placeholder-gray-500 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200"
              />
            </div>
          </div>

          <!-- Children Info (only for PARENT) -->
          <div v-if="userType === 'PARENT'" class="border-t pt-6">
            <div class="mb-4 flex items-center justify-between">
              <label class="block text-sm font-medium text-gray-700"> 자녀 정보 * </label>
              <button
                type="button"
                @click="addChild"
                class="inline-flex items-center gap-1 rounded-lg bg-indigo-100 px-3 py-1.5 text-xs font-medium text-indigo-700 hover:bg-indigo-200"
              >
                <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M12 4v16m8-8H4"
                  />
                </svg>
                추가
              </button>
            </div>

            <div class="space-y-4">
              <div
                v-for="(child, index) in children"
                :key="index"
                class="rounded-lg border border-gray-200 bg-gray-50 p-4"
              >
                <div class="grid grid-cols-1 gap-3 md:grid-cols-3">
                  <div>
                    <label
                      :for="`childName-${index}`"
                      class="block text-xs font-medium text-gray-700 mb-1"
                    >
                      이름 *
                    </label>
                    <input
                      :id="`childName-${index}`"
                      v-model="child.name"
                      type="text"
                      placeholder="자녀 이름"
                      class="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 placeholder-gray-500 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200"
                    />
                  </div>

                  <div>
                    <label
                      :for="`childGrade-${index}`"
                      class="block text-xs font-medium text-gray-700 mb-1"
                    >
                      학년 *
                    </label>
                    <SelectDropdown
                      :model-value="child.grade ? String(child.grade) : null"
                      @update:model-value="(val) => { child.grade = val ? parseInt(val) : 0 }"
                      placeholder="학년 선택"
                      :options="[
                        { value: null, label: '학년 선택' },
                        ...Array.from({ length: 6 }, (_, i) => ({ value: String(i + 1), label: `${i + 1}학년` }))
                      ]"
                    />
                  </div>

                  <div class="flex gap-2">
                    <div class="flex-1">
                      <label
                        class="block text-xs font-medium text-gray-700 mb-1"
                      >
                        반 *
                      </label>
                      <SelectDropdown
                        :model-value="child.classroom ? String(child.classroom) : null"
                        @update:model-value="(val) => { child.classroom = val ? parseInt(val) : 0 }"
                        placeholder="반 선택"
                        :options="[
                          { value: null, label: '반 선택' },
                          ...Array.from({ length: 10 }, (_, i) => ({ value: String(i + 1), label: `${i + 1}반` }))
                        ]"
                      />
                    </div>

                    <div class="flex items-end">
                      <button
                        v-if="children.length > 1"
                        type="button"
                        @click="removeChild(index)"
                        class="rounded-lg bg-red-100 px-3 py-2 text-red-700 hover:bg-red-200"
                      >
                        <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                          <path
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="2"
                            d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                          />
                        </svg>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Password Fields -->
          <div class="grid grid-cols-1 gap-5 md:grid-cols-2">
            <div>
              <label for="password" class="block text-sm font-medium text-gray-700 mb-2">
                비밀번호 (최소 8자) *
              </label>
              <div class="relative">
                <input
                  id="password"
                  v-model="password"
                  :type="showPassword ? 'text' : 'password'"
                  placeholder="최소 8자 이상"
                  class="w-full rounded-lg border border-gray-300 bg-white/50 px-4 py-2.5 text-sm text-gray-900 placeholder-gray-500 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200"
                />
                <button
                  type="button"
                  @click="togglePasswordVisibility"
                  class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700"
                >
                  <svg v-if="!showPassword" class="h-5 w-5" viewBox="0 0 24 24" fill="currentColor">
                    <path
                      d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm3.5-9c.83 0 1.5-.67 1.5-1.5S16.33 8 15.5 8 14 8.67 14 9.5s.67 1.5 1.5 1.5z"
                    />
                  </svg>
                  <svg v-else class="h-5 w-5" viewBox="0 0 24 24" fill="currentColor">
                    <path
                      d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z"
                    />
                  </svg>
                </button>
              </div>
              <p v-if="password && !isPasswordValid" class="mt-1 text-xs text-red-600">
                최소 8자 이상이어야 합니다
              </p>
            </div>

            <div>
              <label for="passwordConfirm" class="block text-sm font-medium text-gray-700 mb-2">
                비밀번호 확인 *
              </label>
              <div class="relative">
                <input
                  id="passwordConfirm"
                  v-model="passwordConfirm"
                  :type="showPasswordConfirm ? 'text' : 'password'"
                  placeholder="비밀번호를 다시 입력하세요"
                  class="w-full rounded-lg border border-gray-300 bg-white/50 px-4 py-2.5 text-sm text-gray-900 placeholder-gray-500 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200"
                />
                <button
                  type="button"
                  @click="togglePasswordConfirmVisibility"
                  class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700"
                >
                  <svg
                    v-if="!showPasswordConfirm"
                    class="h-5 w-5"
                    viewBox="0 0 24 24"
                    fill="currentColor"
                  >
                    <path
                      d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm3.5-9c.83 0 1.5-.67 1.5-1.5S16.33 8 15.5 8 14 8.67 14 9.5s.67 1.5 1.5 1.5z"
                    />
                  </svg>
                  <svg v-else class="h-5 w-5" viewBox="0 0 24 24" fill="currentColor">
                    <path
                      d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z"
                    />
                  </svg>
                </button>
              </div>
              <p v-if="passwordConfirm && !isPasswordMatch" class="mt-1 text-xs text-red-600">
                비밀번호가 일치하지 않습니다
              </p>
            </div>
          </div>

          <!-- Error Message -->
          <div
            v-if="authStore.error"
            class="rounded-lg border border-red-300 bg-red-50 p-3 text-sm text-red-700"
          >
            {{ authStore.error }}
          </div>

          <!-- Terms Agreement -->
          <div class="flex items-start gap-3">
            <input
              id="terms"
              v-model="agreedToTerms"
              type="checkbox"
              class="mt-1 h-4 w-4 rounded border-gray-300 text-indigo-600"
            />
            <label for="terms" class="text-sm text-gray-600">
              <span class="font-medium">서비스 약관</span>에 동의합니다 *
            </label>
          </div>

          <!-- Submit Button -->
          <button
            type="submit"
            :disabled="!isFormValid || isSubmitting"
            class="w-full rounded-lg bg-gradient-to-r from-indigo-600 to-purple-600 py-3 text-base font-semibold text-white shadow-md transition-all hover:shadow-lg hover:-translate-y-0.5 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span v-if="!isSubmitting">회원가입</span>
            <span v-else class="flex items-center justify-center gap-2">
              <svg
                class="h-4 w-4 animate-spin"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
              >
                <circle
                  cx="12"
                  cy="12"
                  r="10"
                  stroke-width="2"
                  stroke-dasharray="15.7"
                  stroke-dashoffset="0"
                />
              </svg>
              회원가입 중...
            </span>
          </button>
        </form>

        <!-- Divider -->
        <div class="my-6 flex items-center gap-3">
          <div class="h-px flex-1 bg-gray-200"></div>
          <span class="text-sm text-gray-500">또는</span>
          <div class="h-px flex-1 bg-gray-200"></div>
        </div>

        <!-- Login Link -->
        <div class="text-center text-sm text-gray-600">
          이미 계정이 있으신가요?
          <RouterLink to="/auth/login" class="font-semibold text-indigo-600 hover:text-indigo-700">
            로그인하기
          </RouterLink>
        </div>
      </div>
    </div>
  </div>
</template>
