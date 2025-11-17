<template>
  <div class="bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow overflow-hidden">
    <div class="aspect-w-16 aspect-h-9 bg-gray-200">
      <img
        v-if="board.image_url"
        :src="board.image_url"
        :alt="board.model_name"
        class="w-full h-48 object-cover"
        @error="handleImageError"
      />
      <div
        v-else
        class="w-full h-48 flex items-center justify-center text-gray-400"
      >
        <svg
          class="w-16 h-16"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
          />
        </svg>
      </div>
    </div>
    <div class="p-4">
      <div class="flex items-start justify-between mb-2">
        <div>
          <h3 class="text-lg font-semibold text-gray-900">{{ board.model_name }}</h3>
          <p class="text-sm text-gray-600">{{ board.brand?.name }}</p>
        </div>
        <span
          v-if="board.model_year"
          class="text-xs font-medium text-gray-500 bg-gray-100 px-2 py-1 rounded"
        >
          {{ board.model_year }}
        </span>
      </div>
      <div class="space-y-1 text-sm text-gray-600">
        <p v-if="board.profile?.standard_name">
          <span class="font-medium">Profile:</span> {{ board.profile.standard_name }}
        </p>
        <p v-if="board.shape?.standard_name">
          <span class="font-medium">Shape:</span> {{ board.shape.standard_name }}
        </p>
        <p v-if="board.flex_rating">
          <span class="font-medium">Flex:</span> {{ board.flex_rating }}/10
        </p>
        <p v-if="board.gender">
          <span class="font-medium">Gender:</span> {{ board.gender }}
        </p>
        <p v-if="board.msrp" class="text-lg font-semibold text-gray-900 mt-2">
          ${{ board.msrp.toFixed(2) }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  board: {
    type: Object,
    required: true
  }
})

const handleImageError = (event) => {
  event.target.style.display = 'none'
}
</script>

<style scoped>
.aspect-w-16 {
  position: relative;
  padding-bottom: 56.25%;
}

.aspect-w-16 > * {
  position: absolute;
  height: 100%;
  width: 100%;
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
}
</style>

