<template>
  <div class="relative">
    <label v-if="label" class="block text-sm font-medium text-gray-700 mb-2">
      {{ label }}
      <span v-if="required" class="text-red-500">*</span>
    </label>
    
    <!-- Searchable Dropdown -->
    <div v-if="searchable" class="relative">
      <div
        ref="dropdownRef"
        class="relative"
        @click="toggleDropdown"
      >
        <div
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus-within:ring-2 focus-within:ring-blue-500 focus-within:border-transparent text-sm cursor-pointer bg-white flex items-center justify-between"
          :class="{
            'opacity-50 cursor-not-allowed': disabled,
            'bg-gray-50': disabled
          }"
        >
          <div class="flex-1 min-w-0">
            <input
              v-if="isOpen"
              ref="searchInputRef"
              v-model="searchQuery"
              type="text"
              :placeholder="placeholder || 'Search...'"
              class="w-full outline-none bg-transparent"
              @click.stop
              @keydown.enter.prevent="handleEnterKey"
              @keydown.escape="closeDropdown"
              @keydown.down.prevent="navigateOptions(1)"
              @keydown.up.prevent="navigateOptions(-1)"
            />
            <span v-else class="block truncate">
              {{ displayValue }}
            </span>
          </div>
          <svg
            :class="['w-5 h-5 text-gray-400 transition-transform', isOpen ? 'transform rotate-180' : '']"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>
        </div>
        
        <!-- Dropdown Options -->
        <div
          v-if="isOpen && !disabled"
          class="absolute z-50 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg max-h-60 overflow-auto"
        >
          <div
            v-if="filteredOptions.length === 0"
            class="px-3 py-2 text-sm text-gray-500"
          >
            No options found
          </div>
          <div
            v-for="(option, index) in filteredOptions"
            :key="getOptionValue(option)"
            :ref="el => { if (el) optionRefs[index] = el }"
            class="px-3 py-2 text-sm cursor-pointer hover:bg-blue-50"
            :class="{
              'bg-blue-100': isSelected(option) || highlightedIndex === index,
              'font-semibold': isSelected(option)
            }"
            @click="selectOption(option)"
            @mouseenter="highlightedIndex = index"
          >
            <div class="flex items-center">
              <input
                v-if="multiple"
                type="checkbox"
                :checked="isSelected(option)"
                class="mr-2 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                @click.stop
                @change="toggleOption(option)"
              />
              <span>{{ getOptionLabel(option) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Standard Select (non-searchable) -->
    <select
      v-else
      :model-value="modelValue"
      :name="name"
      :disabled="disabled"
      :required="required"
      :multiple="multiple"
      :size="size"
      :autofocus="autofocus"
      :form="form"
      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
      :class="{
        'opacity-50 cursor-not-allowed': disabled,
        'bg-gray-50': disabled
      }"
      @change="handleChange"
      @blur="handleBlur"
      @focus="handleFocus"
    >
      <option
        v-if="placeholder && !multiple"
        :value="null"
        disabled
        selected
      >
        {{ placeholder }}
      </option>
      <option
        v-for="option in options"
        :key="getOptionValue(option)"
        :value="getOptionValue(option)"
        :disabled="isOptionDisabled(option)"
      >
        {{ getOptionLabel(option) }}
      </option>
    </select>
    
    <!-- Selected Tags (for multi-select) -->
    <div
      v-if="multiple && selectedOptions.length > 0 && !isOpen"
      class="mt-2 flex flex-wrap gap-2"
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
        >
          <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
          </svg>
        </button>
      </span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  modelValue: {
    type: [String, Number, Array, null],
    default: null
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
    default: ''
  },
  placeholder: {
    type: String,
    default: ''
  },
  disabled: {
    type: Boolean,
    default: false
  },
  required: {
    type: Boolean,
    default: false
  },
  multiple: {
    type: Boolean,
    default: false
  },
  size: {
    type: Number,
    default: undefined
  },
  autofocus: {
    type: Boolean,
    default: false
  },
  form: {
    type: String,
    default: ''
  },
  searchable: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'change', 'blur', 'focus'])

// State
const isOpen = ref(false)
const searchQuery = ref('')
const highlightedIndex = ref(-1)
const dropdownRef = ref(null)
const searchInputRef = ref(null)
const optionRefs = ref([])

// Computed
const selectedOptions = computed(() => {
  if (!props.multiple) {
    const selected = props.options.find(opt => getOptionValue(opt) === props.modelValue)
    return selected ? [selected] : []
  }
  if (!Array.isArray(props.modelValue)) return []
  return props.options.filter(opt => props.modelValue.includes(getOptionValue(opt)))
})

const displayValue = computed(() => {
  if (props.multiple) {
    if (selectedOptions.value.length === 0) {
      return props.placeholder || 'Select options...'
    }
    if (selectedOptions.value.length === 1) {
      return getOptionLabel(selectedOptions.value[0])
    }
    return `${selectedOptions.value.length} selected`
  }
  
  if (props.modelValue === null || props.modelValue === undefined || props.modelValue === '') {
    return props.placeholder || 'Select an option...'
  }
  
  const selected = props.options.find(opt => getOptionValue(opt) === props.modelValue)
  return selected ? getOptionLabel(selected) : props.placeholder || 'Select an option...'
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
  if (props.multiple) {
    return Array.isArray(props.modelValue) && props.modelValue.includes(value)
  }
  return props.modelValue === value
}

const toggleDropdown = () => {
  if (props.disabled) return
  isOpen.value = !isOpen.value
  if (isOpen.value && props.searchable) {
    nextTick(() => {
      searchInputRef.value?.focus()
    })
  }
}

const closeDropdown = () => {
  isOpen.value = false
  searchQuery.value = ''
  highlightedIndex.value = -1
}

const selectOption = (option) => {
  if (isOptionDisabled(option)) return
  
  const value = getOptionValue(option)
  
  if (props.multiple) {
    const currentValues = Array.isArray(props.modelValue) ? [...props.modelValue] : []
    if (currentValues.includes(value)) {
      emit('update:modelValue', currentValues.filter(v => v !== value))
    } else {
      emit('update:modelValue', [...currentValues, value])
    }
  } else {
    emit('update:modelValue', value)
    emit('change', value)
    closeDropdown()
  }
}

const toggleOption = (option) => {
  selectOption(option)
}

const removeOption = (option) => {
  if (props.multiple) {
    const value = getOptionValue(option)
    const currentValues = Array.isArray(props.modelValue) ? [...props.modelValue] : []
    emit('update:modelValue', currentValues.filter(v => v !== value))
  }
}

const handleChange = (event) => {
  const value = props.multiple
    ? Array.from(event.target.selectedOptions, opt => opt.value)
    : event.target.value
  emit('update:modelValue', value)
  emit('change', value)
}

const handleBlur = (event) => {
  emit('blur', event)
}

const handleFocus = (event) => {
  emit('focus', event)
}

const handleEnterKey = () => {
  if (highlightedIndex.value >= 0 && highlightedIndex.value < filteredOptions.value.length) {
    selectOption(filteredOptions.value[highlightedIndex.value])
  } else if (filteredOptions.value.length === 1) {
    selectOption(filteredOptions.value[0])
  }
}

const navigateOptions = (direction) => {
  const maxIndex = filteredOptions.value.length - 1
  highlightedIndex.value = Math.max(0, Math.min(maxIndex, highlightedIndex.value + direction))
  
  nextTick(() => {
    if (optionRefs.value[highlightedIndex.value]) {
      optionRefs.value[highlightedIndex.value].scrollIntoView({
        block: 'nearest',
        behavior: 'smooth'
      })
    }
  })
}

// Click outside handler
const handleClickOutside = (event) => {
  if (dropdownRef.value && !dropdownRef.value.contains(event.target)) {
    closeDropdown()
  }
}

// Watch for modelValue changes to close dropdown if needed
watch(() => props.modelValue, () => {
  if (!props.multiple && isOpen.value) {
    closeDropdown()
  }
})

// Lifecycle
onMounted(() => {
  if (props.searchable) {
    document.addEventListener('click', handleClickOutside)
  }
})

onUnmounted(() => {
  if (props.searchable) {
    document.removeEventListener('click', handleClickOutside)
  }
})
</script>

