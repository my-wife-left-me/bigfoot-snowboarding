<template>
  <div class="min-h-screen bg-gray-50">
    <div class="container mx-auto px-4 py-8">
      <!-- Header -->
      <div class="mb-8">
        <h1 class="text-4xl font-bold text-gray-900 mb-2">Snowboard Catalog</h1>
        <p class="text-gray-600">Browse our collection of snowboards</p>
      </div>

      <!-- Search Bar -->
      <div class="mb-6">
        <SearchBar
          v-model="searchQuery"
          placeholder="Search by model name, brand..."
          @input="handleSearch"
        />
      </div>

      <div class="flex flex-col lg:flex-row gap-6">
        <!-- Filter Panel -->
        <aside class="lg:w-80 flex-shrink-0">
          <div class="bg-purple-100 rounded-lg shadow-sm p-6 sticky top-4 max-h-[calc(100vh-2rem)] overflow-y-auto">
            <div class="flex items-center justify-between mb-4">
              <h2 class="text-xl font-semibold text-gray-900">Filters</h2>
              <button
                @click="clearFilters"
                class="text-sm text-blue-600 hover:text-blue-800"
              >
                Clear All
              </button>
            </div>

            <!-- Accordion Component -->
            <div class="space-y-2">
              <!-- Basic Info Accordion -->
              <FilterAccordion
                title="Basic Info"
                :open="openAccordions.basic"
                @toggle="toggleAccordion('basic')"
              >
                  <div class="space-y-4">
                    <div>
                      <MultiSelectGrid
                        v-model="filters.brandId"
                        :options="brands"
                        option-value="id"
                        option-label="name"
                        label="Brand"
                        @change="applyFilters"
                      />
                    </div>
                    <div>
                      <MultiSelectGrid
                        v-model="filters.year"
                        :options="availableYears"
                        option-value="year"
                        option-label="year"
                        label="Year"
                        @change="applyFilters"
                      />
                    </div>
                    <div>
                      <MultiSelectGrid
                        v-model="filters.gender"
                        :options="['Mens', 'Womens', 'Unisex', 'Kids']"
                        label="Gender"
                        @change="applyFilters"
                      />
                    </div>
                    <RangeInput
                      label="Price Range ($)"
                      :min-value="filters.priceMin"
                      :max-value="filters.priceMax"
                      step="1"
                      @update:min-value="filters.priceMin = $event; applyFilters()"
                      @update:max-value="filters.priceMax = $event; applyFilters()"
                    />
                  </div>
              </FilterAccordion>

              <!-- Profile & Shape Accordion -->
              <FilterAccordion
                title="Profile & Shape"
                :open="openAccordions.profile"
                @toggle="toggleAccordion('profile')"
              >
                  <div class="space-y-4">
                    <div>
                      <MultiSelectGrid
                        v-model="filters.profileId"
                        :options="profiles"
                        option-label="standard_name"
                        option-value="id"
                        label="Profile"
                        @change="applyFilters"
                      />
                    </div>
                    <div>
                      <MultiSelectGrid
                        v-model="filters.shapeId"
                        :options="shapes"
                        option-value="id"
                        option-label="standard_name"
                        label="Shape"
                        @change="applyFilters"
                      />
                    </div>
                    <div>
                      <MultiSelectGrid
                        v-model="filters.responseTypeId"
                        :options="responseTypes"
                        option-label="standard_name"
                        option-value="id"
                        label="Response Type"
                        @change="applyFilters"
                      />
                    </div>
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-2">
                        Flex Rating: {{ filters.flexMin || 1 }} - {{ filters.flexMax || 10 }}
                      </label>
                      <div class="space-y-2">
                        <input
                          v-model.number="filters.flexMin"
                          type="range"
                          min="1"
                          max="10"
                          step="0.5"
                          class="w-full"
                          @input="applyFilters"
                        />
                        <input
                          v-model.number="filters.flexMax"
                          type="range"
                          min="1"
                          max="10"
                          step="0.5"
                          class="w-full"
                          @input="applyFilters"
                        />
                      </div>
                    </div>
                  </div>
              </FilterAccordion>

              <!-- Ability & Terrain Accordion -->
              <FilterAccordion
                title="Ability & Terrain"
                :open="openAccordions.ability"
                @toggle="toggleAccordion('ability')"
              >
                  <div class="space-y-4">
                    <div>
                      <MultiSelectGrid
                        v-model="filters.abilityLevelIds"
                        :options="abilityLevels"
                        option-value="id"
                        option-label="name"
                        label="Ability Level"
                        @change="applyFilters"
                      />
                    </div>
                    <div>
                      <MultiSelectGrid
                        v-model="filters.terrainTypeIds"
                        :options="terrainTypes"
                        option-label="name"
                        option-value="id"
                        label="Terrain Type"
                        @change="applyFilters"
                      />
                    </div>
                  </div>
              </FilterAccordion>

              <!-- Board Dimensions Accordion -->
              <FilterAccordion
                title="Board Dimensions"
                :open="openAccordions.dimensions"
                @toggle="toggleAccordion('dimensions')"
              >
                  <div class="space-y-4">
                    <RangeInput
                      label="Size (cm)"
                      :min-value="filters.sizeMin"
                      :max-value="filters.sizeMax"
                      step="0.5"
                      @update:min-value="filters.sizeMin = $event; applyFilters()"
                      @update:max-value="filters.sizeMax = $event; applyFilters()"
                    />
                    <RangeInput
                      label="Waist Width (mm)"
                      :min-value="filters.waistWidthMin"
                      :max-value="filters.waistWidthMax"
                      step="0.1"
                      @update:min-value="filters.waistWidthMin = $event; applyFilters()"
                      @update:max-value="filters.waistWidthMax = $event; applyFilters()"
                    />
                    <RangeInput
                      label="Tip Width (mm)"
                      :min-value="filters.tipWidthMin"
                      :max-value="filters.tipWidthMax"
                      step="0.1"
                      @update:min-value="filters.tipWidthMin = $event; applyFilters()"
                      @update:max-value="filters.tipWidthMax = $event; applyFilters()"
                    />
                    <RangeInput
                      label="Tail Width (mm)"
                      :min-value="filters.tailWidthMin"
                      :max-value="filters.tailWidthMax"
                      step="0.1"
                      @update:min-value="filters.tailWidthMin = $event; applyFilters()"
                      @update:max-value="filters.tailWidthMax = $event; applyFilters()"
                    />
                    <RangeInput
                      label="Effective Edge (mm)"
                      :min-value="filters.effectiveEdgeMin"
                      :max-value="filters.effectiveEdgeMax"
                      step="0.1"
                      @update:min-value="filters.effectiveEdgeMin = $event; applyFilters()"
                      @update:max-value="filters.effectiveEdgeMax = $event; applyFilters()"
                    />
                    <RangeInput
                      label="Running Length (mm)"
                      :min-value="filters.runningLengthMin"
                      :max-value="filters.runningLengthMax"
                      step="0.1"
                      @update:min-value="filters.runningLengthMin = $event; applyFilters()"
                      @update:max-value="filters.runningLengthMax = $event; applyFilters()"
                    />
                    <div>
                      <label class="flex items-center space-x-2 cursor-pointer">
                        <input
                          type="checkbox"
                          v-model="filters.wide"
                          class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                          @change="applyFilters"
                        />
                        <span class="text-sm font-medium text-gray-700">Wide Only</span>
                      </label>
                    </div>
                  </div>
              </FilterAccordion>

              <!-- Sidecut Accordion -->
              <FilterAccordion
                title="Sidecut"
                :open="openAccordions.sidecut"
                @toggle="toggleAccordion('sidecut')"
              >
                  <div class="space-y-4">
                    <RangeInput
                      label="Sidecut Radius (m)"
                      :min-value="filters.sidecutRadiusMin"
                      :max-value="filters.sidecutRadiusMax"
                      step="0.01"
                      @update:min-value="filters.sidecutRadiusMin = $event; applyFilters()"
                      @update:max-value="filters.sidecutRadiusMax = $event; applyFilters()"
                    />
                    <RangeInput
                      label="Sidecut Depth (mm)"
                      :min-value="filters.sidecutDepthMin"
                      :max-value="filters.sidecutDepthMax"
                      step="0.1"
                      @update:min-value="filters.sidecutDepthMin = $event; applyFilters()"
                      @update:max-value="filters.sidecutDepthMax = $event; applyFilters()"
                    />
                  </div>
              </FilterAccordion>

              <!-- Stance Accordion -->
              <FilterAccordion
                title="Stance"
                :open="openAccordions.stance"
                @toggle="toggleAccordion('stance')"
              >
                  <div class="space-y-4">
                    <RangeInput
                      label="Min Stance (in)"
                      :min-value="filters.minStanceMin"
                      :max-value="filters.minStanceMax"
                      step="0.1"
                      @update:min-value="filters.minStanceMin = $event; applyFilters()"
                      @update:max-value="filters.minStanceMax = $event; applyFilters()"
                    />
                    <RangeInput
                      label="Max Stance (in)"
                      :min-value="filters.maxStanceMin"
                      :max-value="filters.maxStanceMax"
                      step="0.1"
                      @update:min-value="filters.maxStanceMin = $event; applyFilters()"
                      @update:max-value="filters.maxStanceMax = $event; applyFilters()"
                    />
                    <RangeInput
                      label="Setback (in)"
                      :min-value="filters.setbackMin"
                      :max-value="filters.setbackMax"
                      step="0.1"
                      @update:min-value="filters.setbackMin = $event; applyFilters()"
                      @update:max-value="filters.setbackMax = $event; applyFilters()"
                    />
                  </div>
              </FilterAccordion>

              <!-- Rider Weight Accordion -->
              <FilterAccordion
                title="Rider Weight"
                :open="openAccordions.weight"
                @toggle="toggleAccordion('weight')"
              >
                <div class="space-y-4">
                  <RangeInput
                    label="Weight Range (lbs)"
                    :min-value="filters.riderWeightMin"
                    :max-value="filters.riderWeightMax"
                    step="0.1"
                    @update:min-value="filters.riderWeightMin = $event; applyFilters()"
                    @update:max-value="filters.riderWeightMax = $event; applyFilters()"
                  />
                </div>
              </FilterAccordion>
            </div>
          </div>
        </aside>

        <!-- Main Content -->
        <main class="flex-1">
          <!-- Loading State -->
          <div v-if="loading" class="flex justify-center items-center py-20">
            <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
          </div>

          <!-- Error State -->
          <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <p class="text-red-800">{{ error }}</p>
          </div>

          <!-- Results -->
          <div v-else>
            <!-- Results Count -->
            <div class="mb-4 text-gray-600">
              Showing {{ startIndex + 1 }}-{{ endIndex }} of {{ totalCount }} snowboards
            </div>

            <!-- Grid -->
            <div
              v-if="snowboards.length > 0"
              class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6 mb-8"
            >
              <SnowboardCard
                v-for="board in snowboards"
                :key="board.id"
                :board="board"
              />
            </div>

            <!-- Empty State -->
            <div v-else class="text-center py-20">
              <p class="text-gray-500 text-lg">No snowboards found matching your criteria.</p>
            </div>

            <!-- Pagination -->
            <Pagination
              :current-page="currentPage"
              :total-pages="totalPages"
              @page-change="goToPage"
            />
          </div>
        </main>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { supabase } from '../lib/supabase'
import FilterAccordion from '../components/FilterAccordion.vue'
import RangeInput from '../components/RangeInput.vue'
import SearchBar from '../components/SearchBar.vue'
import SnowboardCard from '../components/SnowboardCard.vue'
import Pagination from '../components/Pagination.vue'
import CustomSelect from '../components/CustomSelect.vue'
import MultiSelectGrid from '../components/MultiSelectGrid.vue'

// Debounce helper
let searchTimeout = null

// State
const snowboards = ref([])
const brands = ref([])
const profiles = ref([])
const shapes = ref([])
const responseTypes = ref([])
const abilityLevels = ref([])
const terrainTypes = ref([])
const loading = ref(false)
const error = ref(null)
const searchQuery = ref('')
const currentPage = ref(1)
const totalCount = ref(0)
const itemsPerPage = 12

// Accordion state
const openAccordions = ref({
  basic: true,
  profile: false,
  ability: false,
  dimensions: false,
  sidecut: false,
  stance: false,
  weight: false
})

const toggleAccordion = (key) => {
  openAccordions.value[key] = !openAccordions.value[key]
}

// Filters - comprehensive filter object
const filters = ref({
  // Basic
  brandId: [],
  year: [],
  gender: [],
  priceMin: null,
  priceMax: null,
  
  // Profile & Shape
  profileId: [],
  shapeId: [],
  responseTypeId: [],
  flexMin: 1,
  flexMax: 10,
  
  // Ability & Terrain
  abilityLevelIds: [],
  terrainTypeIds: [],
  
  // Board Dimensions
  sizeMin: null,
  sizeMax: null,
  waistWidthMin: null,
  waistWidthMax: null,
  tipWidthMin: null,
  tipWidthMax: null,
  tailWidthMin: null,
  tailWidthMax: null,
  effectiveEdgeMin: null,
  effectiveEdgeMax: null,
  runningLengthMin: null,
  runningLengthMax: null,
  wide: false,
  
  // Sidecut
  sidecutRadiusMin: null,
  sidecutRadiusMax: null,
  sidecutDepthMin: null,
  sidecutDepthMax: null,
  
  // Stance
  minStanceMin: null,
  minStanceMax: null,
  maxStanceMin: null,
  maxStanceMax: null,
  setbackMin: null,
  setbackMax: null,
  
  // Rider Weight
  riderWeightMin: null,
  riderWeightMax: null
})

// Computed
const totalPages = computed(() => Math.ceil(totalCount.value / itemsPerPage))
const startIndex = computed(() => (currentPage.value - 1) * itemsPerPage)
const endIndex = computed(() =>
  Math.min(startIndex.value + itemsPerPage, totalCount.value)
)

const availableYears = computed(() => {
  const currentYear = new Date().getFullYear() + 1
  const PREVIOUS_CATALOG_YEARS = 1;
  const years = []
  for (let i = currentYear; i >= currentYear - PREVIOUS_CATALOG_YEARS; i--) {
    years.push(i)
  }
  return years
})

// Methods
const handleSearch = () => {
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }
  searchTimeout = setTimeout(() => {
    currentPage.value = 1
    fetchSnowboards()
  }, 300)
}

const applyFilters = () => {
  currentPage.value = 1
  fetchSnowboards()
}

const clearFilters = () => {
  filters.value = {
    brandId: null,
    year: null,
    gender: null,
    priceMin: null,
    priceMax: null,
    profileId: null,
    shapeId: null,
    responseTypeId: null,
    flexMin: 1,
    flexMax: 10,
    abilityLevelIds: [],
    terrainTypeIds: [],
    sizeMin: null,
    sizeMax: null,
    waistWidthMin: null,
    waistWidthMax: null,
    tipWidthMin: null,
    tipWidthMax: null,
    tailWidthMin: null,
    tailWidthMax: null,
    effectiveEdgeMin: null,
    effectiveEdgeMax: null,
    runningLengthMin: null,
    runningLengthMax: null,
    wide: false,
    sidecutRadiusMin: null,
    sidecutRadiusMax: null,
    sidecutDepthMin: null,
    sidecutDepthMax: null,
    minStanceMin: null,
    minStanceMax: null,
    maxStanceMin: null,
    maxStanceMax: null,
    setbackMin: null,
    setbackMax: null,
    riderWeightMin: null,
    riderWeightMax: null
  }
  searchQuery.value = ''
  currentPage.value = 1
  fetchSnowboards()
}

const goToPage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

const fetchFilterOptions = async () => {
  try {
    // Fetch all filter options in parallel
    const [
      { data: brandsData, error: brandsError },
      { data: profilesData, error: profilesError },
      { data: shapesData, error: shapesError },
      { data: responseTypesData, error: responseTypesError },
      { data: abilityLevelsData, error: abilityLevelsError },
      { data: terrainTypesData, error: terrainTypesError }
    ] = await Promise.all([
      supabase.from('brand').select('id, name').order('name'),
      supabase.from('profile').select('id, standard_name').order('standard_name'),
      supabase.from('shape').select('id, standard_name').order('standard_name'),
      supabase.from('response_type').select('id, standard_name').order('standard_name'),
      supabase.from('ability_level').select('id, name').order('sort_order'),
      supabase.from('terrain_type').select('id, name').order('name')
    ])

    if (brandsError) throw brandsError
    if (profilesError) throw profilesError
    if (shapesError) throw shapesError
    if (responseTypesError) throw responseTypesError
    if (abilityLevelsError) throw abilityLevelsError
    if (terrainTypesError) throw terrainTypesError

    brands.value = brandsData || []
    profiles.value = profilesData || []
    shapes.value = shapesData || []
    responseTypes.value = responseTypesData || []
    abilityLevels.value = abilityLevelsData || []
    terrainTypes.value = terrainTypesData || []
  } catch (err) {
    console.error('Error fetching filter options:', err)
  }
}

const fetchSnowboards = async () => {
  loading.value = true
  error.value = null

  try {
    // First, get board IDs that match board_size filters (if any)
    let boardModelIds = null
    
    const hasSizeFilters = 
      filters.value.sizeMin !== null || filters.value.sizeMax !== null ||
      filters.value.waistWidthMin !== null || filters.value.waistWidthMax !== null ||
      filters.value.tipWidthMin !== null || filters.value.tipWidthMax !== null ||
      filters.value.tailWidthMin !== null || filters.value.tailWidthMax !== null ||
      filters.value.effectiveEdgeMin !== null || filters.value.effectiveEdgeMax !== null ||
      filters.value.runningLengthMin !== null || filters.value.runningLengthMax !== null ||
      filters.value.sidecutRadiusMin !== null || filters.value.sidecutRadiusMax !== null ||
      filters.value.sidecutDepthMin !== null || filters.value.sidecutDepthMax !== null ||
      filters.value.minStanceMin !== null || filters.value.minStanceMax !== null ||
      filters.value.maxStanceMin !== null || filters.value.maxStanceMax !== null ||
      filters.value.setbackMin !== null || filters.value.setbackMax !== null ||
      filters.value.riderWeightMin !== null || filters.value.riderWeightMax !== null ||
      filters.value.wide === true

    if (hasSizeFilters) {
      let sizeQuery = supabase
        .from('board_size')
        .select('board_model_id')

      if (filters.value.sizeMin !== null) {
        sizeQuery = sizeQuery.gte('size_cm', filters.value.sizeMin)
      }
      if (filters.value.sizeMax !== null) {
        sizeQuery = sizeQuery.lte('size_cm', filters.value.sizeMax)
      }
      if (filters.value.waistWidthMin !== null) {
        sizeQuery = sizeQuery.gte('waist_width_mm', filters.value.waistWidthMin)
      }
      if (filters.value.waistWidthMax !== null) {
        sizeQuery = sizeQuery.lte('waist_width_mm', filters.value.waistWidthMax)
      }
      if (filters.value.tipWidthMin !== null) {
        sizeQuery = sizeQuery.gte('tip_width_mm', filters.value.tipWidthMin)
      }
      if (filters.value.tipWidthMax !== null) {
        sizeQuery = sizeQuery.lte('tip_width_mm', filters.value.tipWidthMax)
      }
      if (filters.value.tailWidthMin !== null) {
        sizeQuery = sizeQuery.gte('tail_width_mm', filters.value.tailWidthMin)
      }
      if (filters.value.tailWidthMax !== null) {
        sizeQuery = sizeQuery.lte('tail_width_mm', filters.value.tailWidthMax)
      }
      if (filters.value.effectiveEdgeMin !== null) {
        sizeQuery = sizeQuery.gte('effective_edge_mm', filters.value.effectiveEdgeMin)
      }
      if (filters.value.effectiveEdgeMax !== null) {
        sizeQuery = sizeQuery.lte('effective_edge_mm', filters.value.effectiveEdgeMax)
      }
      if (filters.value.runningLengthMin !== null) {
        sizeQuery = sizeQuery.gte('running_length_mm', filters.value.runningLengthMin)
      }
      if (filters.value.runningLengthMax !== null) {
        sizeQuery = sizeQuery.lte('running_length_mm', filters.value.runningLengthMax)
      }
      if (filters.value.sidecutRadiusMin !== null) {
        sizeQuery = sizeQuery.gte('sidecut_radius_m', filters.value.sidecutRadiusMin)
      }
      if (filters.value.sidecutRadiusMax !== null) {
        sizeQuery = sizeQuery.lte('sidecut_radius_m', filters.value.sidecutRadiusMax)
      }
      if (filters.value.sidecutDepthMin !== null) {
        sizeQuery = sizeQuery.gte('sidecut_depth_mm', filters.value.sidecutDepthMin)
      }
      if (filters.value.sidecutDepthMax !== null) {
        sizeQuery = sizeQuery.lte('sidecut_depth_mm', filters.value.sidecutDepthMax)
      }
      if (filters.value.minStanceMin !== null) {
        sizeQuery = sizeQuery.gte('min_stance_in', filters.value.minStanceMin)
      }
      if (filters.value.minStanceMax !== null) {
        sizeQuery = sizeQuery.lte('min_stance_in', filters.value.minStanceMax)
      }
      if (filters.value.maxStanceMin !== null) {
        sizeQuery = sizeQuery.gte('max_stance_in', filters.value.maxStanceMin)
      }
      if (filters.value.maxStanceMax !== null) {
        sizeQuery = sizeQuery.lte('max_stance_in', filters.value.maxStanceMax)
      }
      if (filters.value.setbackMin !== null) {
        sizeQuery = sizeQuery.gte('setback_in', filters.value.setbackMin)
      }
      if (filters.value.setbackMax !== null) {
        sizeQuery = sizeQuery.lte('setback_in', filters.value.setbackMax)
      }
      if (filters.value.riderWeightMin !== null) {
        sizeQuery = sizeQuery.gte('rider_weight_max_lbs', filters.value.riderWeightMin)
      }
      if (filters.value.riderWeightMax !== null) {
        sizeQuery = sizeQuery.lte('rider_weight_min_lbs', filters.value.riderWeightMax)
      }
      if (filters.value.wide === true) {
        sizeQuery = sizeQuery.eq('wide', true)
      }

      const { data: sizeData, error: sizeError } = await sizeQuery
      if (sizeError) throw sizeError
      
      // Get unique board_model_ids
      boardModelIds = [...new Set((sizeData || []).map(s => s.board_model_id).filter(Boolean))]
      
      if (boardModelIds.length === 0) {
        // No boards match size filters
        snowboards.value = []
        totalCount.value = 0
        loading.value = false
        return
      }
    }

    // Now query board_model with all filters
    let query = supabase
      .from('board_model')
      .select(
        `
        id,
        model_name,
        model_year,
        flex_rating,
        gender,
        msrp,
        image_url,
        brand:brand_id (
          id,
          name
        ),
        profile:profile_id (
          id,
          standard_name
        ),
        shape:shape_id (
          id,
          standard_name
        ),
        response_type:response_type_id (
          id,
          standard_name
        )
      `,
        { count: 'exact' }
      )

    // Apply board_size filter if we have matching IDs
    if (boardModelIds !== null) {
      query = query.in('id', boardModelIds)
    }

    // Apply search
    if (searchQuery.value.trim()) {
      const searchTerm = `%${searchQuery.value.trim()}%`
      query = query.ilike('model_name', searchTerm)
    }

    // Apply basic filters
    if (filters.value.brandId.length > 0) {
      query = query.in('brand_id', filters.value.brandId)
    }

    if (filters.value.profileId.length > 0) {
      query = query.in('profile_id', filters.value.profileId)
    }

    if (filters.value.shapeId.length > 0) {
      query = query.in('shape_id', filters.value.shapeId)
    }

    if (filters.value.responseTypeId.length > 0) {
      query = query.in('response_type_id', filters.value.responseTypeId)
    }

    if (filters.value.year.length > 0) {
      query = query.in('model_year', filters.value.year)
    }

    // Flex rating filter
    const isDefaultFlexRange = filters.value.flexMin === 1 && filters.value.flexMax === 10
    if (!isDefaultFlexRange) {
      if (filters.value.flexMin !== null) {
        query = query.gte('flex_rating', filters.value.flexMin)
      }
      if (filters.value.flexMax !== null) {
        query = query.lte('flex_rating', filters.value.flexMax)
      }
    }

    if (filters.value.gender.length > 0) {
      query = query.in('gender', filters.value.gender)
    }

    // Price filter
    if (filters.value.priceMin !== null) {
      query = query.gte('msrp', filters.value.priceMin)
    }
    if (filters.value.priceMax !== null) {
      query = query.lte('msrp', filters.value.priceMax)
    }

    // Ability level filter (junction table)
    if (filters.value.abilityLevelIds.length > 0) {
      const { data: abilityData, error: abilityError } = await supabase
        .from('board_model_ability_level')
        .select('board_model_id')
        .in('ability_level_id', filters.value.abilityLevelIds)
      
      if (abilityError) throw abilityError
      const abilityBoardIds = [...new Set((abilityData || []).map(a => a.board_model_id).filter(Boolean))]
      
      if (abilityBoardIds.length === 0) {
        snowboards.value = []
        totalCount.value = 0
        loading.value = false
        return
      }
      
      // Intersect with existing boardModelIds or use abilityBoardIds
      if (boardModelIds !== null) {
        boardModelIds = boardModelIds.filter(id => abilityBoardIds.includes(id))
        if (boardModelIds.length === 0) {
          snowboards.value = []
          totalCount.value = 0
          loading.value = false
          return
        }
        query = query.in('id', boardModelIds)
      } else {
        query = query.in('id', abilityBoardIds)
      }
    }

    // Terrain type filter (junction table)
    if (filters.value.terrainTypeIds.length > 0) {
      const { data: terrainData, error: terrainError } = await supabase
        .from('board_model_terrain_type')
        .select('board_model_id')
        .in('terrain_type_id', filters.value.terrainTypeIds)
      
      if (terrainError) throw terrainError
      const terrainBoardIds = [...new Set((terrainData || []).map(t => t.board_model_id).filter(Boolean))]
      
      if (terrainBoardIds.length === 0) {
        snowboards.value = []
        totalCount.value = 0
        loading.value = false
        return
      }
      
      // Intersect with existing boardModelIds or use terrainBoardIds
      if (boardModelIds !== null) {
        boardModelIds = boardModelIds.filter(id => terrainBoardIds.includes(id))
        if (boardModelIds.length === 0) {
          snowboards.value = []
          totalCount.value = 0
          loading.value = false
          return
        }
        query = query.in('id', boardModelIds)
      } else {
        query = query.in('id', terrainBoardIds)
      }
    }

    // Apply pagination
    const from = startIndex.value
    const to = startIndex.value + itemsPerPage - 1

    query = query.range(from, to).order('model_name', { ascending: true })

    const { data, error: queryError, count } = await query

    if (queryError) throw queryError

    snowboards.value = data || []
    totalCount.value = count || 0
  } catch (err) {
    console.error('Error fetching snowboards:', err)
    error.value = 'Failed to load snowboards. Please try again later.'
    snowboards.value = []
    totalCount.value = 0
  } finally {
    loading.value = false
  }
}

// Watch for page changes
watch(currentPage, () => {
  fetchSnowboards()
})

// Lifecycle
onMounted(async () => {
  await fetchFilterOptions()
  await fetchSnowboards()
})
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
