<template>
  <div
    class="mx-auto flex min-h-[60vh] max-w-3xl flex-col items-center justify-center p-6 text-center"
  >
    <h1 class="text-3xl font-extrabold text-gray-900">페이지를 찾을 수 없어요</h1>
    <p class="mt-2 text-gray-600">주소를 다시 확인하거나 홈으로 돌아가 주세요.</p>
    <RouterLink
      :to="{ name: 'home' }"
      class="mt-6 inline-flex items-center justify-center rounded-xl bg-sky-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm hover:brightness-110"
    >
      홈으로
    </RouterLink>
  </div>
</template>
