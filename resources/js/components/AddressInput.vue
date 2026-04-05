<template>
  <div class="space-y-2">
    <!-- Address Line 1 -->
    <div>
      <label class="block text-xs text-gray-500 dark:text-gray-400 mb-1">\uC8FC\uC18C (Address) *</label>
      <input v-model="addr.address" type="text" placeholder="123 Main Street"
        class="w-full border border-gray-200 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400" />
    </div>

    <!-- City, State, ZIP -->
    <div class="grid grid-cols-3 gap-2">
      <div class="relative">
        <label class="block text-xs text-gray-500 dark:text-gray-400 mb-1">\uB3C4\uC2DC (City) *</label>
        <input v-model="addr.city" type="text" placeholder="Atlanta"
          @input="onCityInput" @focus="onCityInput" @blur="hideSuggestions"
          autocomplete="off"
          class="w-full border border-gray-200 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400" />
        <!-- Autocomplete dropdown -->
        <div v-if="suggestions.length"
          class="absolute z-50 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg shadow-lg max-h-40 overflow-y-auto w-full mt-1">
          <div v-for="s in suggestions" :key="s.city + s.state"
            @mousedown.prevent="selectCity(s)"
            class="px-3 py-2 text-sm hover:bg-blue-50 dark:hover:bg-gray-600 cursor-pointer dark:text-white">
            {{ s.city }}, {{ s.state }}
          </div>
        </div>
      </div>
      <div>
        <label class="block text-xs text-gray-500 dark:text-gray-400 mb-1">\uC8FC (State) *</label>
        <select v-model="addr.state"
          class="w-full border border-gray-200 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-lg px-2 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400">
          <option value="">\uC120\uD0DD</option>
          <option v-for="s in US_STATES" :key="s" :value="s">{{ s }}</option>
        </select>
      </div>
      <div>
        <label class="block text-xs text-gray-500 dark:text-gray-400 mb-1">\uC6B0\uD3B8\uBC88\uD638 (ZIP)</label>
        <input v-model="addr.zipcode" type="text" placeholder="30301" maxlength="10"
          class="w-full border border-gray-200 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, watch } from 'vue'

const props = defineProps({
  modelValue: {
    type: Object,
    default: () => ({ address: '', city: '', state: '', zipcode: '', lat: null, lng: null })
  }
})

const emit = defineEmits(['update:modelValue'])

const US_STATES = [
  'AL','AK','AZ','AR','CA','CO','CT','DE','DC','FL',
  'GA','HI','ID','IL','IN','IA','KS','KY','LA','ME',
  'MD','MA','MI','MN','MS','MO','MT','NE','NV','NH',
  'NJ','NM','NY','NC','ND','OH','OK','OR','PA','RI',
  'SC','SD','TN','TX','UT','VT','VA','WA','WV','WI','WY'
]

const addr = reactive({
  address: props.modelValue?.address || '',
  city: props.modelValue?.city || '',
  state: props.modelValue?.state || '',
  zipcode: props.modelValue?.zipcode || '',
  lat: props.modelValue?.lat || null,
  lng: props.modelValue?.lng || null,
})

const suggestions = ref([])

// Korean-American major cities for autocomplete
const MAJOR_CITIES = [
  { city: 'Los Angeles', state: 'CA' }, { city: 'Koreatown', state: 'CA' },
  { city: 'Garden Grove', state: 'CA' }, { city: 'Fullerton', state: 'CA' },
  { city: 'Irvine', state: 'CA' }, { city: 'Torrance', state: 'CA' },
  { city: 'Cerritos', state: 'CA' }, { city: 'San Francisco', state: 'CA' },
  { city: 'San Jose', state: 'CA' }, { city: 'San Diego', state: 'CA' },
  { city: 'New York', state: 'NY' }, { city: 'Flushing', state: 'NY' },
  { city: 'Bayside', state: 'NY' }, { city: 'Fort Lee', state: 'NJ' },
  { city: 'Palisades Park', state: 'NJ' }, { city: 'Edison', state: 'NJ' },
  { city: 'Atlanta', state: 'GA' }, { city: 'Duluth', state: 'GA' },
  { city: 'Suwanee', state: 'GA' }, { city: 'Johns Creek', state: 'GA' },
  { city: 'Doraville', state: 'GA' }, { city: 'Norcross', state: 'GA' },
  { city: 'Annandale', state: 'VA' }, { city: 'Centreville', state: 'VA' },
  { city: 'Fairfax', state: 'VA' }, { city: 'Washington', state: 'DC' },
  { city: 'Ellicott City', state: 'MD' }, { city: 'Rockville', state: 'MD' },
  { city: 'Chicago', state: 'IL' }, { city: 'Houston', state: 'TX' },
  { city: 'Dallas', state: 'TX' }, { city: 'Austin', state: 'TX' },
  { city: 'Seattle', state: 'WA' }, { city: 'Bellevue', state: 'WA' },
  { city: 'Federal Way', state: 'WA' }, { city: 'Boston', state: 'MA' },
  { city: 'Miami', state: 'FL' }, { city: 'Orlando', state: 'FL' },
  { city: 'Philadelphia', state: 'PA' }, { city: 'Phoenix', state: 'AZ' },
  { city: 'Denver', state: 'CO' }, { city: 'Las Vegas', state: 'NV' },
  { city: 'Portland', state: 'OR' }, { city: 'Nashville', state: 'TN' },
  { city: 'Charlotte', state: 'NC' }, { city: 'Raleigh', state: 'NC' },
  { city: 'Honolulu', state: 'HI' }, { city: 'Sacramento', state: 'CA' },
  { city: 'Minneapolis', state: 'MN' }, { city: 'Detroit', state: 'MI' },
  { city: 'Columbus', state: 'OH' }, { city: 'Indianapolis', state: 'IN' },
  { city: 'Kansas City', state: 'MO' }, { city: 'Salt Lake City', state: 'UT' },
]

function onCityInput() {
  const q = addr.city.trim().toLowerCase()
  if (q.length < 2) { suggestions.value = []; return }
  suggestions.value = MAJOR_CITIES.filter(c => c.city.toLowerCase().includes(q)).slice(0, 8)
}

function selectCity(s) {
  addr.city = s.city
  addr.state = s.state
  suggestions.value = []
}

function hideSuggestions() {
  setTimeout(() => { suggestions.value = [] }, 150)
}

// Emit structured data on any change
watch(addr, () => {
  emit('update:modelValue', { ...addr })
}, { deep: true })
</script>
