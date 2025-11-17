<template>
  <div class="border border-gray-200 rounded-md">
    <button
      @click="$emit('toggle')"
      class="w-full px-4 py-3 flex items-center justify-between text-left hover:bg-gray-50 transition-colors"
    >
      <span class="font-medium text-gray-900 text-sm">{{ title }}</span>
      <svg
        :class="['w-5 h-5 text-gray-500 transition-transform', open ? 'transform rotate-180' : '']"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
      </svg>
    </button>
    <div v-if="open" class="px-4 py-4 border-t border-gray-200">
      <slot />
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    required: true
  },
  open: {
    type: Boolean,
    default: false
  }
})

defineEmits(['toggle'])
</script>

