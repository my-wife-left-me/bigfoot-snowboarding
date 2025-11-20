<template>
  <div class="relative">
    <div class="flex items-center justify-between mb-2">
      <label class="block text-sm font-medium text-gray-700">
        {{ label }}
        <span v-if="required" class="text-red-500">*</span>
      </label>
      <button
        v-if="!hideToggle"
        type="button"
        @click="toggleVisibility"
        class="text-sm text-blue-600 hover:text-blue-800"
        :disabled="disabled"
      >
        {{ isVisible ? 'Hide' : 'Show' }}
      </button>
    </div>
    
    <!-- Selected Summary (when hidden) -->
    <div
      v-if="!isVisible && selectedOptions.length > 0"
      class="mb-2 flex flex-wrap gap-2"
    >
      <span
        v-for="option in selectedOptions"
        :key="getOptionValue(option)"
        class="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-blue-100 text-blue-800"
      >
        {{ getOptionLabel(option) }}
        <button
          type="button"
          @click.stop="removeOption(option)"
          class="ml-1 inline-flex items-center justify-center w-4 h-4 rounded-full hover:bg-blue-200"
          :disabled="disabled"
        >
          <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
          </svg>
        </button>
      </span>
    </div>
    
    <!-- Search Input (when visible) -->
    <div v-if="isVisible && searchable" class="mb-3">
      <input
        v-model="searchQuery"
        type="text"
        :placeholder="searchPlaceholder || 'Search options...'"
        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
        :disabled="disabled"
      />
    </div>
    
    <!-- Grid of Options (when visible) -->
    <div
      v-if="isVisible"
      class="border border-gray-300 rounded-md p-3 bg-white"
      :class="{
        'opacity-50 pointer-events-none': disabled
      }"
    >
      <div
        v-if="filteredOptions.length === 0"
        class="text-sm text-gray-500 text-center py-4"
      >
        No options found
      </div>
      <div
        v-else
        :class="[
          'grid gap-3',
          gridColsClass
        ]"
      >
        <label
          v-for="option in filteredOptions"
          :key="getOptionValue(option)"
          class="flex items-center space-x-2 cursor-pointer p-2 rounded-md hover:bg-gray-50 transition-colors"
          :class="{
            'opacity-50 cursor-not-allowed': isOptionDisabled(option)
          }"
        >
          <input
            type="checkbox"
            :checked="isSelected(option)"
            :disabled="disabled || isOptionDisabled(option)"
            class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            @change="toggleOption(option)"
          />
          <span class="text-sm text-gray-700 flex-1">{{ getOptionLabel(option) }}</span>
        </label>
      </div>
      
      <!-- Select All / Deselect All (optional) -->
      <div
        v-if="showSelectAll && filteredOptions.length > 0"
        class="mt-3 pt-3 border-t border-gray-200 flex justify-between"
      >
        <button
          type="button"
          @click="selectAll"
          class="text-sm text-blue-600 hover:text-blue-800"
          :disabled="disabled || allSelected"
        >
          Select All
        </button>
        <button
          type="button"
          @click="deselectAll"
          class="text-sm text-blue-600 hover:text-blue-800"
          :disabled="disabled || selectedOptions.length === 0"
        >
          Deselect All
        </button>
      </div>
    </div>
    
    <!-- Hidden input for form submission -->
    <input
      v-if="name"
      type="hidden"
      :name="name"
      :value="JSON.stringify(modelValue)"
    />
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  modelValue: {
    type: Array,
    default: () => []
  },
  options: {
    type: Array,
    required: true,
    default: () => []
  },
  optionValue: {
    type: String,
    default: 'value'
  },
  optionLabel: {
    type: String,
    default: 'label'
  },
  optionDisabled: {
    type: String,
    default: 'disabled'
  },
  name: {
    type: String,
    default: ''
  },
  label: {
    type: String,
    required: true
  },
  required: {
    type: Boolean,
    default: false
  },
  disabled: {
    type: Boolean,
    default: false
  },
  searchable: {
    type: Boolean,
    default: false
  },
  searchPlaceholder: {
    type: String,
    default: 'Search options...'
  },
  columns: {
    type: Number,
    default: 2,
    validator: (value) => value >= 1 && value <= 6
  },
  defaultVisible: {
    type: Boolean,
    default: true
  },
  hideToggle: {
    type: Boolean,
    default: false
  },
  showSelectAll: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'change'])

// State
const isVisible = ref(props.defaultVisible)
const searchQuery = ref('')

// Computed
const selectedOptions = computed(() => {
  if (!Array.isArray(props.modelValue)) return []
  return props.options.filter(opt => props.modelValue.includes(getOptionValue(opt)))
})

const filteredOptions = computed(() => {
  if (!props.searchable || !searchQuery.value) {
    return props.options
  }
  
  const query = searchQuery.value.toLowerCase()
  return props.options.filter(option => {
    const label = getOptionLabel(option).toLowerCase()
    return label.includes(query)
  })
})

const gridColsClass = computed(() => {
  const colsMap = {
    1: 'grid-cols-1',
    2: 'grid-cols-1 sm:grid-cols-2',
    3: 'grid-cols-1 sm:grid-cols-2 md:grid-cols-3',
    4: 'grid-cols-1 sm:grid-cols-2 md:grid-cols-4',
    5: 'grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5',
    6: 'grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-6'
  }
  return colsMap[props.columns] || colsMap[2]
})

const allSelected = computed(() => {
  return filteredOptions.value.length > 0 &&
    filteredOptions.value.every(opt => isSelected(opt) && !isOptionDisabled(opt))
})

// Methods
const getOptionValue = (option) => {
  if (typeof option === 'object' && option !== null) {
    return option[props.optionValue]
  }
  return option
}

const getOptionLabel = (option) => {
  if (typeof option === 'object' && option !== null) {
    return option[props.optionLabel] || option[props.optionValue] || String(option)
  }
  return String(option)
}

const isOptionDisabled = (option) => {
  if (typeof option === 'object' && option !== null) {
    return option[props.optionDisabled] === true
  }
  return false
}

const isSelected = (option) => {
  const value = getOptionValue(option)
  return Array.isArray(props.modelValue) && props.modelValue.includes(value)
}

const toggleOption = (option) => {
  if (isOptionDisabled(option) || props.disabled) return
  
  const value = getOptionValue(option)
  const currentValues = Array.isArray(props.modelValue) ? [...props.modelValue] : []
  
  if (currentValues.includes(value)) {
    const newValues = currentValues.filter(v => v !== value)
    emit('update:modelValue', newValues)
    emit('change', newValues)
  } else {
    const newValues = [...currentValues, value]
    emit('update:modelValue', newValues)
    emit('change', newValues)
  }
}

const removeOption = (option) => {
  if (props.disabled) return
  toggleOption(option)
}

const toggleVisibility = () => {
  isVisible.value = !isVisible.value
  if (!isVisible.value) {
    searchQuery.value = ''
  }
}

const selectAll = () => {
  if (props.disabled) return
  
  const currentValues = Array.isArray(props.modelValue) ? [...props.modelValue] : []
  const newValues = [...currentValues]
  
  filteredOptions.value.forEach(option => {
    if (!isOptionDisabled(option)) {
      const value = getOptionValue(option)
      if (!newValues.includes(value)) {
        newValues.push(value)
      }
    }
  })
  
  emit('update:modelValue', newValues)
  emit('change', newValues)
}

const deselectAll = () => {
  if (props.disabled) return
  
  const currentValues = Array.isArray(props.modelValue) ? [...props.modelValue] : []
  const filteredValues = filteredOptions.value.map(opt => getOptionValue(opt))
  const newValues = currentValues.filter(v => !filteredValues.includes(v))
  
  emit('update:modelValue', newValues)
  emit('change', newValues)
}

// Watch for visibility changes to clear search
watch(() => isVisible.value, (visible) => {
  if (!visible) {
    searchQuery.value = ''
  }
})
</script>

