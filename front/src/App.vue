<script setup lang="ts">
import { onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const authStore = useAuthStore()
const open = ref(false)
const scrolled = ref(false)

// 데스크톱/모바일 공용 네비 아이템
const navItems = [
  { label: '홈', name: 'home' },
  { label: '민원 신청', name: 'form' },
  { label: '민원 현황', name: 'status', match: 'status' },
  { label: '교직원', name: 'staff' },
  // { label: '정책', name: 'policy' },
]

// 라우트 변경 시 모바일 메뉴 닫기
watch(
  () => route.fullPath,
  () => (open.value = false),
)

// 스크롤 시 헤더 축소
const handleScroll = () => {
  scrolled.value = window.scrollY > 10
}
onMounted(() => {
  window.addEventListener('scroll', handleScroll)
  authStore.initialize()
})
onUnmounted(() => window.removeEventListener('scroll', handleScroll))
</script>

<template>
  <div
    class="min-h-screen flex flex-col bg-gradient-to-b from-sky-50 via-white to-emerald-50 text-gray-800"
  >
    <!-- HEADER -->
    <header
      :class="[
        'sticky top-0 z-40 transition-all duration-300 border-b border-slate-200/50',
        'backdrop-blur-md',
        scrolled ? 'bg-white/80 shadow-sm py-2' : 'bg-white/50 py-3',
      ]"
    >
      <div class="mx-auto flex max-w-6xl items-center justify-between px-4">
        <!-- BRAND -->
        <RouterLink :to="{ name: 'home' }" class="flex items-center gap-2">
          <div
            class="inline-flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-sky-500 to-indigo-600 text-white shadow-md"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-4 w-4"
              viewBox="0 0 24 24"
              fill="currentColor"
            >
              <path d="M5 3v18l7-4 7 4V3z" />
            </svg>
          </div>
          <span
            class="text-lg font-bold tracking-tight bg-gradient-to-r from-sky-600 to-emerald-600 bg-clip-text text-transparent"
          >
            스쿨 민원
          </span>
        </RouterLink>

        <!-- DESKTOP NAV (md 이상에서 표시) -->
        <nav class="hidden md:flex items-center gap-6 text-sm font-medium">
          <RouterLink
            v-for="(item, i) in navItems"
            :key="i"
            :to="{ name: item.name }"
            class="group relative px-2 py-2 text-gray-700 transition-colors hover:text-sky-700"
            :class="{
              'text-sky-700 font-semibold':
                route.name === item.name || String(route.name).startsWith(item.match || item.name),
            }"
          >
            {{ item.label }}
            <!-- 하이라이트 바: z-10로 안전화 -->
            <span
              v-if="
                route.name === item.name || String(route.name).startsWith(item.match || item.name)
              "
              class="pointer-events-none absolute left-1/2 bottom-0 -translate-x-1/2 h-[2px] w-5/6 rounded bg-gradient-to-r from-sky-500 to-emerald-500 z-10"
            />
            <!-- 호버 배경 글로우: 음수 z-index 제거 -->
            <span
              class="pointer-events-none absolute inset-0 opacity-0 group-hover:opacity-100 transition rounded-xl bg-sky-50/70 blur-[2px] z-0"
            ></span>
          </RouterLink>
        </nav>

        <!-- AUTH BUTTONS (desktop) -->
        <div class="hidden md:flex items-center gap-3">
          <div
            v-if="authStore.isAuthenticated"
            class="flex items-center gap-3 pl-3 border-l border-slate-200"
          >
            <span class="text-sm text-gray-700 font-medium">
              {{ authStore.user?.real_name || authStore.user?.username }}
            </span>
            <RouterLink
              :to="{ name: 'profile' }"
              class="inline-flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-100 text-indigo-600 hover:bg-indigo-200 transition"
              title="프로필"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="h-4 w-4"
                viewBox="0 0 24 24"
                fill="currentColor"
              >
                <path
                  d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"
                />
              </svg>
            </RouterLink>
          </div>
          <div v-else class="flex items-center gap-2">
            <RouterLink
              :to="{ name: 'login' }"
              class="rounded-lg px-4 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-100 transition"
            >
              로그인
            </RouterLink>
            <RouterLink
              :to="{ name: 'signup' }"
              class="rounded-lg bg-gradient-to-r from-sky-500 to-indigo-600 px-4 py-1.5 text-sm font-medium text-white hover:shadow-md transition"
            >
              회원가입
            </RouterLink>
          </div>
        </div>

        <!-- MOBILE MENU BUTTON -->
        <button
          class="md:hidden inline-flex h-9 w-9 items-center justify-center rounded-xl border border-slate-200 bg-white/80 shadow-sm transition hover:bg-white focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-sky-600"
          @click="open = !open"
          aria-label="메뉴 열기/닫기"
          :aria-expanded="open ? 'true' : 'false'"
        >
          <svg
            v-if="!open"
            xmlns="http://www.w3.org/2000/svg"
            class="h-5 w-5 text-slate-700"
            viewBox="0 0 24 24"
            fill="currentColor"
          >
            <path d="M3 6h18v2H3zM3 11h18v2H3zM3 16h18v2H3z" />
          </svg>
          <svg
            v-else
            xmlns="http://www.w3.org/2000/svg"
            class="h-5 w-5 text-slate-700"
            viewBox="0 0 24 24"
            fill="currentColor"
          >
            <path d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- MOBILE NAV -->
      <transition
        enter-active-class="transition-all duration-300 ease-out"
        enter-from-class="max-h-0 opacity-0"
        enter-to-class="max-h-96 opacity-100"
        leave-active-class="transition-all duration-200 ease-in"
        leave-from-class="max-h-96 opacity-100"
        leave-to-class="max-h-0 opacity-0"
      >
        <div v-if="open" class="md:hidden border-t border-slate-200 bg-white/90 backdrop-blur">
          <nav class="flex flex-col px-4 py-3 space-y-1">
            <RouterLink
              v-for="(item, i) in navItems"
              :key="i"
              :to="{ name: item.name }"
              class="rounded-lg px-3 py-2 text-sm transition hover:bg-sky-50"
              :class="{
                'text-sky-700 font-semibold':
                  route.name === item.name ||
                  String(route.name).startsWith(item.match || item.name),
              }"
            >
              {{ item.label }}
            </RouterLink>

            <!-- Mobile Auth Section -->
            <div class="border-t border-slate-200 pt-3 mt-3 space-y-1">
              <div v-if="authStore.isAuthenticated">
                <div class="px-3 py-2 text-sm font-medium text-gray-700">
                  {{ authStore.user?.real_name || authStore.user?.username }}
                </div>
                <RouterLink
                  :to="{ name: 'profile' }"
                  class="block rounded-lg px-3 py-2 text-sm transition hover:bg-indigo-50 text-gray-700 hover:text-indigo-700"
                >
                  프로필 설정
                </RouterLink>
              </div>
              <div v-else class="space-y-1">
                <RouterLink
                  :to="{ name: 'login' }"
                  class="block rounded-lg px-3 py-2 text-sm transition hover:bg-sky-50 text-gray-700 hover:text-sky-700"
                >
                  로그인
                </RouterLink>
                <RouterLink
                  :to="{ name: 'signup' }"
                  class="block rounded-lg px-3 py-2 text-sm font-medium bg-gradient-to-r from-sky-500 to-indigo-600 text-white transition hover:shadow-md text-center"
                >
                  회원가입
                </RouterLink>
              </div>
            </div>
          </nav>
        </div>
      </transition>
    </header>

    <!-- MAIN -->
    <main id="main" class="flex-1 mx-auto w-full max-w-6xl px-4 py-6">
      <RouterView v-slot="{ Component }">
        <transition
          mode="out-in"
          enter-active-class="transition duration-300 ease-out"
          enter-from-class="opacity-0 translate-y-2"
          enter-to-class="opacity-100 translate-y-0"
          leave-active-class="transition duration-200 ease-in"
          leave-from-class="opacity-100 translate-y-0"
          leave-to-class="opacity-0 translate-y-1"
        >
          <component :is="Component" />
        </transition>
      </RouterView>
    </main>

    <!-- FOOTER -->
    <footer class="border-t border-slate-200/70 bg-white/60 backdrop-blur">
      <div
        class="mx-auto flex max-w-6xl flex-col items-center justify-between gap-2 px-4 py-4 text-xs text-slate-500 sm:flex-row"
      >
        <span>© 2025 SchoolMinwon Demo</span>
        <div class="flex items-center gap-3">
          <RouterLink :to="{ name: 'policy' }" class="hover:text-sky-700">이용약관/정책</RouterLink>
        </div>
      </div>
    </footer>
  </div>
</template>

<style scoped>
/* 은은한 hover glow (가독성 해치지 않도록 낮은 강도) */
nav a:hover {
  text-shadow: 0 0 4px rgba(56, 189, 248, 0.35);
}
</style>
