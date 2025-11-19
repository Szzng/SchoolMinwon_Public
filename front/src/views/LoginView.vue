<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const username = ref('')
const password = ref('')
const showPassword = ref(false)
const isSubmitting = ref(false)

const isFormValid = computed(() => username.value.trim() && password.value.length >= 6)

async function handleLogin() {
  if (!isFormValid.value) return

  isSubmitting.value = true
  try {
    await authStore.login(username.value, password.value)
    // 로그인 성공 후 대시보드 또는 홈으로 이동
    if (authStore.isTeacher || authStore.isAdmin) {
      router.push({ name: 'staff' })
    } else {
      router.push({ name: 'status' })
    }
  } catch (err) {
    // 오류는 authStore.error에 저장됨
    console.error('Login failed:', err)
  } finally {
    isSubmitting.value = false
  }
}

function togglePasswordVisibility() {
  showPassword.value = !showPassword.value
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
    <div class="mx-auto flex min-h-[calc(100vh-80px)] max-w-7xl items-center px-6 py-12">
      <!-- LEFT SIDE - Info -->
      <div class="hidden flex-1 pr-12 lg:block">
        <div class="space-y-8">
          <div>
            <h1
              class="bg-gradient-to-r from-indigo-600 via-purple-600 to-indigo-600 bg-clip-text text-4xl font-black text-transparent leading-tight"
            >
              다시 돌아오셨네요!
            </h1>
            <p class="mt-4 text-lg text-gray-600">
              SchoolMinwon에 로그인하여 민원 관리를 계속하세요
            </p>
          </div>

          <!-- Feature List -->
          <div class="space-y-4">
            <div class="flex items-start gap-3">
              <div class="mt-1 flex h-6 w-6 items-center justify-center rounded-full bg-indigo-100">
                <svg class="h-4 w-4 text-indigo-600" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z" />
                </svg>
              </div>
              <div>
                <h3 class="font-semibold text-gray-950">실시간 민원 추적</h3>
                <p class="mt-1 text-sm text-gray-600">접수부터 완료까지 모든 단계를 확인하세요</p>
              </div>
            </div>

            <div class="flex items-start gap-3">
              <div class="mt-1 flex h-6 w-6 items-center justify-center rounded-full bg-indigo-100">
                <svg class="h-4 w-4 text-indigo-600" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z" />
                </svg>
              </div>
              <div>
                <h3 class="font-semibold text-gray-950">AI 자동 분류</h3>
                <p class="mt-1 text-sm text-gray-600">민원이 자동으로 분류되어 신속하게 처리됩니다</p>
              </div>
            </div>

            <div class="flex items-start gap-3">
              <div class="mt-1 flex h-6 w-6 items-center justify-center rounded-full bg-indigo-100">
                <svg class="h-4 w-4 text-indigo-600" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z" />
                </svg>
              </div>
              <div>
                <h3 class="font-semibold text-gray-950">안전한 소통</h3>
                <p class="mt-1 text-sm text-gray-600">모든 기록은 암호화되어 안전하게 보관됩니다</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- RIGHT SIDE - Login Form -->
      <div class="w-full lg:flex-1">
        <div
          class="mx-auto max-w-md rounded-2xl border border-gray-200/60 bg-white/80 p-8 shadow-lg backdrop-blur-sm"
        >
          <!-- Header -->
          <div class="mb-8 text-center">
            <h2 class="text-2xl font-bold text-gray-950">로그인</h2>
            <p class="mt-2 text-sm text-gray-600">계정으로 로그인하세요</p>
          </div>

          <!-- Form -->
          <form @submit.prevent="handleLogin" class="space-y-5">
            <!-- Username Field -->
            <div>
              <label for="username" class="block text-sm font-medium text-gray-700 mb-2">
                사용자명
              </label>
              <input
                id="username"
                v-model="username"
                type="text"
                placeholder="사용자명을 입력하세요"
                class="w-full rounded-lg border border-gray-300 bg-white/50 px-4 py-2.5 text-sm text-gray-900 placeholder-gray-500 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200"
              />
            </div>

            <!-- Password Field -->
            <div>
              <label for="password" class="block text-sm font-medium text-gray-700 mb-2">
                비밀번호
              </label>
              <div class="relative">
                <input
                  id="password"
                  v-model="password"
                  :type="showPassword ? 'text' : 'password'"
                  placeholder="비밀번호를 입력하세요"
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
            </div>

            <!-- Error Message -->
            <div v-if="authStore.error" class="rounded-lg border border-red-300 bg-red-50 p-3 text-sm text-red-700">
              {{ authStore.error }}
            </div>

            <!-- Submit Button -->
            <button
              type="submit"
              :disabled="!isFormValid || isSubmitting"
              class="w-full rounded-lg bg-gradient-to-r from-indigo-600 to-purple-600 py-2.5 text-sm font-semibold text-white shadow-md transition-all hover:shadow-lg hover:-translate-y-0.5 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span v-if="!isSubmitting">로그인</span>
              <span v-else class="flex items-center justify-center gap-2">
                <svg class="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <circle cx="12" cy="12" r="10" stroke-width="2" stroke-dasharray="15.7" stroke-dashoffset="0" />
                </svg>
                로그인 중...
              </span>
            </button>
          </form>

          <!-- Divider -->
          <div class="my-6 flex items-center gap-3">
            <div class="h-px flex-1 bg-gray-200"></div>
            <span class="text-sm text-gray-500">또는</span>
            <div class="h-px flex-1 bg-gray-200"></div>
          </div>

          <!-- Sign Up Link -->
          <div class="text-center text-sm text-gray-600">
            계정이 없으신가요?
            <RouterLink to="/auth/signup" class="font-semibold text-indigo-600 hover:text-indigo-700">
              회원가입하기
            </RouterLink>
          </div>

          <!-- Home Link -->
          <div class="mt-4 text-center">
            <RouterLink to="/" class="text-sm text-gray-500 hover:text-gray-700">
              홈으로 돌아가기
            </RouterLink>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
