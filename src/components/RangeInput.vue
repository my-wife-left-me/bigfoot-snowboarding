<template>
  <div>
    <label class="block text-sm font-medium text-gray-700 mb-2">{{ label }}</label>
    <div class="grid grid-cols-2 gap-2">
      <input
        :model-value="minValue"
        type="number"
        :placeholder="minPlaceholder || 'Min'"
        :step="step"
        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
        @input="updateMin"
      />
      <input
        :model-value="maxValue"
        type="number"
        :placeholder="maxPlaceholder || 'Max'"
        :step="step"
        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
        @input="updateMax"
      />
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  label: {
    type: String,
    required: true
  },
  minValue: {
    type: Number,
    default: null
  },
  maxValue: {
    type: Number,
    default: null
  },
  step: {
    type: [String, Number],
    default: 0.1
  },
  minPlaceholder: {
    type: String,
    default: 'Min'
  },
  maxPlaceholder: {
    type: String,
    default: 'Max'
  }
})

const emit = defineEmits(['update:minValue', 'update:maxValue', 'change'])

const updateMin = (event) => {
  const value = event.target.value ? parseFloat(event.target.value) : null
  emit('update:minValue', value)
  emit('change')
}

const updateMax = (event) => {
  const value = event.target.value ? parseFloat(event.target.value) : null
  emit('update:maxValue', value)
  emit('change')
}
</script>

