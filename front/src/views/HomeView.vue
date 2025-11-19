<script setup lang="ts">
const steps = [
  {
    title: '민원 신청',
    desc: '1. 학교 정보 자동 포함',
    desc2: '2. 간편한 양식 작성',
    emoji: '📝',
  },
  {
    title: '[1단계] AI봇 대응',
    desc: '1. 특이(악성) 민원 분류',
    desc2: '2. 학교 지식 DB 기반 답변',
    emoji: '🤖',
    highlight: false,
  },
  {
    title: '[2단계] 교직원 검토',
    desc: '1. AI 답변 리뷰 및 추천',
    desc2: '2. 내부 민원대응팀 협업',
    emoji: '👥',
  },
  {
    title: '처리 완료',
    desc: '1. AI 리뷰 후 답변',
    desc2: '2. 민원인 알림 발송',
    emoji: '✅',
  },
  {
    title: '통계 분석',
    desc: '1. 교육청 단위 데이터 축적',
    desc2: '2. 데이터 기반 정책 수립',
    emoji: '📈',
  },
]
</script>

<template>
  <div class="relative min-h-[calc(100vh-80px)] overflow-hidden">
    <!-- BACKGROUND - Premium Gradient -->
    <div class="absolute inset-0 -z-30 bg-gradient-to-b from-white via-slate-50/50 to-white"></div>

    <!-- Animated Gradient Orbs -->
    <div
      class="pointer-events-none absolute -top-40 -left-40 -z-20 h-[50rem] w-[50rem] rounded-full bg-gradient-to-br from-indigo-300/20 via-indigo-200/10 to-transparent blur-3xl"
    ></div>
    <div
      class="pointer-events-none absolute -bottom-40 -right-40 -z-20 h-[50rem] w-[50rem] rounded-full bg-gradient-to-tl from-cyan-300/15 via-blue-200/10 to-transparent blur-3xl"
    ></div>

    <!-- HERO -->
    <section class="mx-auto flex max-w-6xl flex-col items-center px-6 pt-11 text-center">
      <!-- Badge with Enhanced Glass Effect -->
      <span
        class="animate-in fade-in slide-in-from-top-2 duration-500 inline-flex items-center gap-2 rounded-full border border-indigo-200/70 bg-white/50 px-4 py-2 text-sm font-medium text-indigo-700 shadow-sm backdrop-blur-md"
      >
        <span class="h-2 w-2 rounded-full bg-indigo-500"></span>
        학교 민원 창구 일원화, 스쿨 민원
      </span>

      <!-- Enhanced Heading -->
      <h1
        class="mt-8 max-w-5xl text-4xl font-black leading-tight text-gray-950 sm:text-5xl md:text-6xl lg:leading-[1.2]"
      >
        <span
          class="bg-gradient-to-r from-indigo-600 via-purple-600 to-indigo-600 bg-clip-text text-transparent"
        >
          AI </span
        >기반
        <span
          class="bg-gradient-to-r from-cyan-500 via-purple-700 to-cyan-500 bg-clip-text text-transparent"
          >학교 민원 통합 관리 시스템</span
        >
      </h1>

      <!-- CTA Buttons - Enhanced -->
      <div class="mt-12 flex flex-col items-center justify-center gap-4 sm:flex-row sm:gap-4">
        <RouterLink
          :to="{ name: 'form' }"
          class="group relative inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 px-7 py-3.5 text-sm font-semibold text-white shadow-lg transition-all hover:shadow-xl hover:-translate-y-0.5 active:translate-y-0 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
          aria-label="민원 신청으로 이동"
        >
          <svg
            class="h-5 w-5 transition-transform group-hover:scale-110"
            viewBox="0 0 24 24"
            fill="currentColor"
            aria-hidden="true"
          >
            <path d="M5 4h14v2H5zM5 8h14v12H5zM7 10h10v8H7z" />
          </svg>
          <span>민원 신청하기</span>
          <span
            class="absolute inset-0 rounded-xl bg-white/0 transition group-hover:bg-white/10"
          ></span>
        </RouterLink>

        <RouterLink
          :to="{ name: 'status' }"
          class="group inline-flex items-center gap-2 rounded-xl border border-gray-300/60 bg-white/60 px-7 py-3.5 text-sm font-semibold text-gray-700 shadow-sm backdrop-blur-sm transition-all hover:border-indigo-400 hover:bg-white hover:shadow-md hover:text-indigo-600 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
          aria-label="민원 현황으로 이동"
        >
          <svg
            class="h-5 w-5 transition-transform group-hover:scale-110"
            viewBox="0 0 24 24"
            fill="currentColor"
            aria-hidden="true"
          >
            <path d="M3 3h18v2H3zM3 19h18v2H3zM3 7h10v10H3zM15 7h6v10h-6z" />
          </svg>
          <span>민원 목록</span>
        </RouterLink>

        <RouterLink
          :to="{ name: 'staff' }"
          class="group inline-flex items-center gap-2 rounded-xl border border-gray-300/60 bg-white/60 px-7 py-3.5 text-sm font-semibold text-gray-700 shadow-sm backdrop-blur-sm transition-all hover:border-emerald-400 hover:bg-white hover:shadow-md hover:text-emerald-600 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-emerald-600"
          aria-label="교직원 전용 화면으로 이동"
        >
          <svg
            class="h-5 w-5 transition-transform group-hover:scale-110 text-emerald-500"
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill="currentColor"
            aria-hidden="true"
          >
            <path d="M4 5h16v2H4zM4 11h16v2H4zM4 17h10v2H4z" />
          </svg>
          <span>교직원 전용</span>
        </RouterLink>
      </div>
    </section>

    <!-- PROCESS - Modern Timeline Design -->
    <section class="mx-auto mt-20 max-w-6xl px-6">
      <!-- Timeline Container -->
      <div class="relative">
        <!-- Desktop Timeline Line -->
        <div
          class="hidden lg:block absolute top-12 left-0 right-0 h-1 bg-gradient-to-r from-indigo-300 via-purple-400 to-pink-300 rounded-full"
        ></div>

        <!-- Steps Grid -->
        <div class="grid grid-cols-1 gap-8 md:grid-cols-5">
          <div v-for="(step, i) in steps" :key="i" class="group relative">
            <!-- Mobile Timeline Line -->
            <div
              v-if="i < steps.length - 1"
              class="md:hidden absolute left-10 top-24 h-8 w-1 bg-gradient-to-b from-indigo-400 to-purple-400 rounded-full"
            ></div>

            <!-- Step Card Container -->
            <div class="relative flex flex-col items-center">
              <!-- Circle Badge with Enhanced Styling -->
              <div
                class="relative mb-6 flex h-24 w-24 items-center justify-center rounded-full border-3 transition-all duration-300 text-4xl shadow-lg z-10"
                :class="[
                  step.highlight
                    ? 'bg-gradient-to-br from-indigo-400 to-purple-500 border-indigo-500 ring-4 ring-indigo-200/50 text-white shadow-xl group-hover:scale-110 group-hover:shadow-2xl'
                    : 'bg-gradient-to-br from-white to-gray-50 border-indigo-300 group-hover:from-indigo-50 group-hover:to-blue-50 group-hover:scale-105 group-hover:shadow-xl',
                ]"
              >
                <!-- Animated Background Glow -->
                <div
                  class="absolute inset-0 rounded-full bg-indigo-300/0 group-hover:bg-indigo-300/20 blur-xl transition-all duration-300"
                ></div>

                <!-- Icon -->
                <span class="relative">{{ step.emoji }}</span>
              </div>

              <!-- Step Content Card -->
              <div
                class="w-full px-4 py-6 rounded-2xl border border-gray-200/60 bg-gradient-to-br from-white/80 to-gray-50/50 backdrop-blur-sm text-center transition-all duration-300 group-hover:border-indigo-300/60 group-hover:shadow-lg group-hover:-translate-y-1"
                :class="step.highlight ? 'ring-2 ring-indigo-400/30 shadow-md' : 'shadow-sm'"
              >
                <!-- Step Number -->
                <div
                  class="mb-2 inline-flex h-6 w-6 items-center justify-center rounded-full text-xs font-bold text-white"
                  :class="
                    step.highlight
                      ? 'bg-gradient-to-r from-indigo-500 to-purple-500'
                      : 'bg-gradient-to-r from-indigo-400 to-blue-400'
                  "
                >
                  {{ i + 1 }}
                </div>

                <!-- Title -->
                <h3 class="text-lg font-bold text-gray-950">{{ step.title }}</h3>

                <!-- Description -->
                <p class="mt-2 text-sm text-gray-600 leading-relaxed">
                  {{ step.desc }}<br />
                  {{ step.desc2 }}
                </p>

                <!-- Bottom Accent -->
                <div
                  class="mt-4 h-1 w-8 bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 rounded-full mx-auto opacity-40 group-hover:opacity-100 transition-opacity"
                ></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- BOTTOM CTA -->
    <section class="mx-auto mt-24 max-w-6xl px-6 pb-20">
      <div
        class="relative overflow-hidden rounded-2xl bg-gradient-to-r from-indigo-600 via-purple-600 to-indigo-700 p-8 text-white shadow-xl md:p-12"
      >
        <!-- Decorative Elements -->
        <div
          class="pointer-events-none absolute -right-20 -top-20 h-56 w-56 rounded-full bg-white/10 blur-3xl"
        ></div>
        <div
          class="pointer-events-none absolute -left-20 -bottom-20 h-40 w-40 rounded-full bg-purple-400/10 blur-3xl"
        ></div>

        <!-- Content -->
        <div
          class="relative flex flex-col items-start justify-between gap-6 sm:flex-row sm:items-center"
        >
          <div>
            <h3 class="text-2xl font-black">모두를 위한 효율적인 민원 관리</h3>
            <p class="mt-3 text-base text-indigo-100/90">
              AI 자동 답변, 부서 협업, AI 리뷰, 처리 통계까지<br class="hidden sm:block" />
              AI가 전면에 나서 학교 행정의 디지털 혁신을 이끌어갑니다.
            </p>
          </div>
          <RouterLink
            :to="{ name: 'form' }"
            class="group inline-flex items-center justify-center gap-2 rounded-xl bg-white px-7 py-3.5 text-base font-bold text-indigo-600 shadow-lg transition-all hover:shadow-xl hover:-translate-y-0.5 active:translate-y-0 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white whitespace-nowrap flex-shrink-0"
            aria-label="민원 신청하기"
          >
            민원 신청하기
            <svg
              class="h-5 w-5 transition-transform group-hover:translate-x-1"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <path d="M5 12h14M12 5l7 7-7 7" />
            </svg>
          </RouterLink>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
/* Premium fade-up animation */
@keyframes fade-up {
  0% {
    opacity: 0;
    transform: translateY(20px);
  }
  100% {
    opacity: 1;
    transform: translateY(0);
  }
}

section {
  animation: fade-up 0.6s cubic-bezier(0.16, 1, 0.3, 1) both;
}

section:nth-of-type(1) {
  animation-delay: 0s;
}

section:nth-of-type(2) {
  animation-delay: 0.15s;
}

section:nth-of-type(3) {
  animation-delay: 0.25s;
}

section:nth-of-type(4) {
  animation-delay: 0.35s;
}

/* Badge animations */
@keyframes fade-in {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes slide-in-from-top {
  from {
    opacity: 0;
    transform: translateY(-12px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-in {
  animation: fade-in 400ms ease-out forwards;
}

.slide-in-from-top-2 {
  animation: slide-in-from-top 400ms cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

/* Motion reduction */
@media (prefers-reduced-motion: reduce) {
  section,
  .animate-in,
  .slide-in-from-top-2 {
    animation: none !important;
  }
}
</style>
