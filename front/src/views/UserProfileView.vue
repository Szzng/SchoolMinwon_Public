<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const isEditMode = ref(false)
const isSubmitting = ref(false)
const activeTab = ref<'profile' | 'settings'>('profile')

// Form fields
const realName = ref('')
const email = ref('')
const phone = ref('')
const schoolName = ref('')
const currentPassword = ref('')
const newPassword = ref('')
const newPasswordConfirm = ref('')

const showCurrentPassword = ref(false)
const showNewPassword = ref(false)
const showNewPasswordConfirm = ref(false)

// Computed
const isNewPasswordValid = computed(
  () => newPassword.value.length === 0 || newPassword.value.length >= 8,
)
const isNewPasswordMatch = computed(() =>
  newPassword.value.length === 0 ? true : newPassword.value === newPasswordConfirm.value,
)

const isProfileUpdateValid = computed(
  () => realName.value.trim() && email.value.includes('@') && email.value.includes('.'),
)

onMounted(() => {
  if (authStore.user) {
    realName.value = authStore.user.real_name || ''
    email.value = authStore.user.email || ''
    phone.value = authStore.user.phone || ''
    schoolName.value = authStore.user.school_name || ''
  } else {
    router.push({ name: 'login' })
  }
})

async function handleProfileUpdate() {
  if (!isProfileUpdateValid.value) return

  isSubmitting.value = true
  try {
    await authStore.updateProfile({
      real_name: realName.value,
      email: email.value,
      phone: phone.value,
      school_name: schoolName.value,
    })
    isEditMode.value = false
  } catch (err) {
    console.error('Profile update failed:', err)
  } finally {
    isSubmitting.value = false
  }
}

async function handlePasswordChange() {
  if (!isNewPasswordValid.value || !isNewPasswordMatch.value) return

  isSubmitting.value = true
  try {
    // TODO: Implement password change API call
    // await authStore.changePassword(currentPassword.value, newPassword.value)
    alert('비밀번호 변경 기능은 아직 구현 중입니다.')
    currentPassword.value = ''
    newPassword.value = ''
    newPasswordConfirm.value = ''
  } catch (err) {
    console.error('Password change failed:', err)
  } finally {
    isSubmitting.value = false
  }
}

function handleLogout() {
  if (confirm('로그아웃하시겠습니까?')) {
    authStore.logout()
    router.push({ name: 'home' })
  }
}

function cancelEdit() {
  if (authStore.user) {
    realName.value = authStore.user.real_name || ''
    email.value = authStore.user.email || ''
    phone.value = authStore.user.phone || ''
    schoolName.value = authStore.user.school_name || ''
  }
  isEditMode.value = false
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
      <div class="mb-8 flex items-center justify-between">
        <div>
          <h1 class="text-3xl font-bold text-gray-950">계정 설정</h1>
          <p class="mt-2 text-gray-600">프로필 정보와 보안 설정을 관리하세요</p>
        </div>
      </div>

      <div class="grid grid-cols-1 gap-8 lg:grid-cols-4">
        <!-- Sidebar Navigation -->
        <div class="lg:col-span-1">
          <div class="space-y-2">
            <button
              @click="activeTab = 'profile'"
              :class="[
                'w-full text-left rounded-lg px-4 py-3 text-sm font-medium transition-all',
                activeTab === 'profile'
                  ? 'bg-indigo-100 text-indigo-700'
                  : 'text-gray-700 hover:bg-gray-100',
              ]"
            >
              프로필 정보
            </button>
            <button
              @click="activeTab = 'settings'"
              :class="[
                'w-full text-left rounded-lg px-4 py-3 text-sm font-medium transition-all',
                activeTab === 'settings'
                  ? 'bg-indigo-100 text-indigo-700'
                  : 'text-gray-700 hover:bg-gray-100',
              ]"
            >
              보안 설정
            </button>
          </div>
        </div>

        <!-- Main Content -->
        <div class="lg:col-span-3">
          <!-- Profile Tab -->
          <div v-if="activeTab === 'profile'" class="space-y-6">
            <!-- User Info Card -->
            <div
              class="rounded-2xl border border-gray-200/60 bg-white/80 p-6 shadow-sm backdrop-blur-sm"
            >
              <div class="mb-6 flex items-center justify-between">
                <h2 class="text-xl font-bold text-gray-950">프로필 정보</h2>
                <button
                  v-if="!isEditMode"
                  @click="isEditMode = true"
                  class="rounded-lg bg-indigo-100 px-4 py-2 text-sm font-medium text-indigo-700 hover:bg-indigo-200 transition-colors"
                >
                  수정하기
                </button>
              </div>

              <!-- Display Mode -->
              <div v-if="!isEditMode" class="space-y-4">
                <div class="grid grid-cols-1 gap-6 md:grid-cols-2">
                  <div>
                    <p class="text-sm text-gray-600">사용자명</p>
                    <p class="mt-1 text-base font-medium text-gray-950">
                      {{ authStore.user?.username }}
                    </p>
                  </div>
                  <div>
                    <p class="text-sm text-gray-600">실명</p>
                    <p class="mt-1 text-base font-medium text-gray-950">
                      {{ authStore.user?.real_name || '-' }}
                    </p>
                  </div>
                  <div>
                    <p class="text-sm text-gray-600">이메일</p>
                    <p class="mt-1 text-base font-medium text-gray-950">
                      {{ authStore.user?.email }}
                    </p>
                  </div>
                  <div>
                    <p class="text-sm text-gray-600">연락처</p>
                    <p class="mt-1 text-base font-medium text-gray-950">
                      {{ authStore.user?.phone || '-' }}
                    </p>
                  </div>
                  <div>
                    <p class="text-sm text-gray-600">학교명</p>
                    <p class="mt-1 text-base font-medium text-gray-950">
                      {{ authStore.user?.school_name || '-' }}
                    </p>
                  </div>
                </div>

                <!-- User Type Badge -->
                <div class="mt-6 pt-6 border-t border-gray-200">
                  <p class="mb-2 text-sm text-gray-600">사용자 유형</p>
                  <div
                    :class="[
                      'inline-flex items-center gap-2 rounded-full px-4 py-2 text-sm font-semibold',
                      authStore.isParent
                        ? 'bg-blue-100 text-blue-700'
                        : authStore.isTeacher
                          ? 'bg-green-100 text-green-700'
                          : 'bg-purple-100 text-purple-700',
                    ]"
                  >
                    {{ authStore.isParent ? '학부모' : authStore.isTeacher ? '교사' : '관리자' }}
                  </div>
                </div>

                <!-- Children Info (only for PARENT) -->
                <div v-if="authStore.isParent && authStore.user?.children?.length">
                  <div class="mt-6 pt-6 border-t border-gray-200">
                    <p class="mb-4 text-sm font-medium text-gray-700">자녀 정보</p>
                    <div class="space-y-3">
                      <div
                        v-for="(child, index) in authStore.user.children"
                        :key="index"
                        class="rounded-lg border border-gray-200 bg-gray-50 p-4"
                      >
                        <div class="grid grid-cols-3 gap-4">
                          <div>
                            <p class="text-xs text-gray-600">이름</p>
                            <p class="mt-1 text-sm font-medium text-gray-950">{{ child.name }}</p>
                          </div>
                          <div>
                            <p class="text-xs text-gray-600">학년</p>
                            <p class="mt-1 text-sm font-medium text-gray-950">{{ child.grade }}학년</p>
                          </div>
                          <div>
                            <p class="text-xs text-gray-600">반</p>
                            <p class="mt-1 text-sm font-medium text-gray-950">{{ child.classroom }}반</p>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Edit Mode -->
              <form v-else @submit.prevent="handleProfileUpdate" class="space-y-5">
                <div class="grid grid-cols-1 gap-5 md:grid-cols-2">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">사용자명</label>
                    <input
                      :value="authStore.user?.username"
                      type="text"
                      disabled
                      class="w-full rounded-lg border border-gray-300 bg-gray-100 px-4 py-2.5 text-sm text-gray-500 cursor-not-allowed"
                    />
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">실명 *</label>
                    <input
                      v-model="realName"
                      type="text"
                      placeholder="홍길동"
                      class="w-full rounded-lg border border-gray-300 bg-white/50 px-4 py-2.5 text-sm text-gray-900 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200"
                    />
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">이메일 *</label>
                    <input
                      v-model="email"
                      type="email"
                      class="w-full rounded-lg border border-gray-300 bg-white/50 px-4 py-2.5 text-sm text-gray-900 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200"
                    />
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">연락처</label>
                    <input
                      v-model="phone"
                      type="tel"
                      placeholder="010-1234-5678"
                      class="w-full rounded-lg border border-gray-300 bg-white/50 px-4 py-2.5 text-sm text-gray-900 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200"
                    />
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">학교명</label>
                    <input
                      v-model="schoolName"
                      type="text"
                      placeholder="예시초등학교"
                      class="w-full rounded-lg border border-gray-300 bg-white/50 px-4 py-2.5 text-sm text-gray-900 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200"
                    />
                  </div>
                </div>

                <!-- Error Message -->
                <div
                  v-if="authStore.error"
                  class="rounded-lg border border-red-300 bg-red-50 p-3 text-sm text-red-700"
                >
                  {{ authStore.error }}
                </div>

                <!-- Buttons -->
                <div class="flex gap-3 pt-6">
                  <button
                    type="submit"
                    :disabled="!isProfileUpdateValid || isSubmitting"
                    class="flex-1 rounded-lg bg-gradient-to-r from-indigo-600 to-purple-600 py-2.5 text-sm font-semibold text-white transition-all hover:shadow-lg disabled:opacity-50"
                  >
                    <span v-if="!isSubmitting">변경사항 저장</span>
                    <span v-else class="flex items-center justify-center gap-2">
                      <svg
                        class="h-4 w-4 animate-spin"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                      >
                        <circle cx="12" cy="12" r="10" stroke-width="2" stroke-dasharray="15.7" />
                      </svg>
                      저장 중...
                    </span>
                  </button>
                  <button
                    type="button"
                    @click="cancelEdit"
                    class="rounded-lg border border-gray-300 bg-white px-6 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50"
                  >
                    취소
                  </button>
                </div>
              </form>
            </div>
          </div>

          <!-- Settings Tab -->
          <div v-if="activeTab === 'settings'" class="space-y-6">
            <!-- Password Change Card -->
            <div
              class="rounded-2xl border border-gray-200/60 bg-white/80 p-6 shadow-sm backdrop-blur-sm"
            >
              <h2 class="mb-6 text-xl font-bold text-gray-950">비밀번호 변경</h2>

              <form @submit.prevent="handlePasswordChange" class="space-y-5">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">
                    현재 비밀번호 *
                  </label>
                  <div class="relative">
                    <input
                      v-model="currentPassword"
                      :type="showCurrentPassword ? 'text' : 'password'"
                      placeholder="현재 비밀번호를 입력하세요"
                      class="w-full rounded-lg border border-gray-300 bg-white/50 px-4 py-2.5 text-sm text-gray-900 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200"
                    />
                    <button
                      type="button"
                      @click="showCurrentPassword = !showCurrentPassword"
                      class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700"
                    >
                      <svg
                        v-if="!showCurrentPassword"
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
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">
                    새 비밀번호 (최소 8자) *
                  </label>
                  <div class="relative">
                    <input
                      v-model="newPassword"
                      :type="showNewPassword ? 'text' : 'password'"
                      placeholder="새 비밀번호를 입력하세요"
                      class="w-full rounded-lg border border-gray-300 bg-white/50 px-4 py-2.5 text-sm text-gray-900 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200"
                    />
                    <button
                      type="button"
                      @click="showNewPassword = !showNewPassword"
                      class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700"
                    >
                      <svg
                        v-if="!showNewPassword"
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
                  <p v-if="newPassword && !isNewPasswordValid" class="mt-1 text-xs text-red-600">
                    최소 8자 이상이어야 합니다
                  </p>
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">
                    새 비밀번호 확인 *
                  </label>
                  <div class="relative">
                    <input
                      v-model="newPasswordConfirm"
                      :type="showNewPasswordConfirm ? 'text' : 'password'"
                      placeholder="새 비밀번호를 다시 입력하세요"
                      class="w-full rounded-lg border border-gray-300 bg-white/50 px-4 py-2.5 text-sm text-gray-900 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200"
                    />
                    <button
                      type="button"
                      @click="showNewPasswordConfirm = !showNewPasswordConfirm"
                      class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700"
                    >
                      <svg
                        v-if="!showNewPasswordConfirm"
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
                  <p
                    v-if="newPasswordConfirm && !isNewPasswordMatch"
                    class="mt-1 text-xs text-red-600"
                  >
                    비밀번호가 일치하지 않습니다
                  </p>
                </div>

                <!-- Button -->
                <div class="flex gap-3 pt-6">
                  <button
                    type="submit"
                    :disabled="
                      !currentPassword || !newPassword || !newPasswordConfirm || isSubmitting
                    "
                    class="rounded-lg bg-gradient-to-r from-indigo-600 to-purple-600 px-6 py-2.5 text-sm font-semibold text-white transition-all hover:shadow-lg disabled:opacity-50"
                  >
                    <span v-if="!isSubmitting">비밀번호 변경</span>
                    <span v-else class="flex items-center justify-center gap-2">
                      <svg
                        class="h-4 w-4 animate-spin"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                      >
                        <circle cx="12" cy="12" r="10" stroke-width="2" stroke-dasharray="15.7" />
                      </svg>
                      변경 중...
                    </span>
                  </button>
                </div>
              </form>
            </div>

            <!-- Logout Card -->
            <div
              class="rounded-2xl border border-gray-200/60 bg-white/80 p-6 shadow-sm backdrop-blur-sm"
            >
              <h2 class="mb-3 text-xl font-bold text-gray-950">로그아웃</h2>
              <p class="mb-6 text-sm text-gray-600">현재 계정에서 로그아웃합니다.</p>
              <button
                @click="handleLogout"
                class="rounded-lg border border-red-300 bg-red-50 px-6 py-2.5 text-sm font-semibold text-red-700 hover:bg-red-100 transition-colors"
              >
                로그아웃하기
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
