<template>
  <div ref="dropdownRef" class="relative">
    <button
      type="button"
      @mousedown.prevent="isOpen = !isOpen"
      :class="[
        'rounded-lg border px-3 py-2 text-xs font-medium text-left flex items-center justify-between transition-all duration-200',
        isOpen
          ? 'border-indigo-500 ring-2 ring-indigo-500 bg-indigo-50'
          : 'border-gray-200 bg-white hover:border-gray-300',
        modelValue ? 'text-gray-900' : 'text-gray-500',
        buttonClass
      ]"
    >
      <span class="truncate">{{ modelValue || placeholder }}</span>
      <svg
        :class="[
          'h-4 w-4 transition-transform duration-200 flex-shrink-0 ml-2',
          isOpen ? 'rotate-180' : ''
        ]"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3" />
      </svg>
    </button>

    <transition
      enter-active-class="transition-all duration-200"
      enter-from-class="opacity-0 -translate-y-2"
      enter-to-class="opacity-100 translate-y-0"
      leave-active-class="transition-all duration-200"
      leave-from-class="opacity-100 translate-y-0"
      leave-to-class="opacity-0 -translate-y-2"
    >
      <div
        v-if="isOpen"
        class="absolute top-full left-0 right-0 mt-1 bg-white border border-gray-200 rounded-lg shadow-lg z-10"
      >
        <div
          v-for="option in options"
          :key="option.value"
          @mousedown.prevent="selectOption(option.value)"
          :class="[
            'px-3 py-2 text-xs cursor-pointer transition-colors duration-150 whitespace-nowrap',
            modelValue === option.value
              ? 'bg-indigo-100 text-indigo-700 font-semibold'
              : 'text-gray-700 hover:bg-gray-100'
          ]"
        >
          {{ option.label }}
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

interface Option {
  value: string | null
  label: string
}

defineProps<{
  modelValue: string | null
  placeholder?: string
  options: Option[]
  buttonClass?: string
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string | null]
}>()

const isOpen = ref(false)
const dropdownRef = ref<HTMLDivElement | null>(null)

const selectOption = (value: string | null) => {
  emit('update:modelValue', value)
  isOpen.value = false
}

const handleClickOutside = (event: MouseEvent) => {
  const target = event.target as Node
  if (dropdownRef.value && !dropdownRef.value.contains(target)) {
    isOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>
