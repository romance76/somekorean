<template>
  <div class="max-w-3xl mx-auto px-4 py-6 pb-20">
    <!-- Search Input -->
    <div class="relative mb-4">
      <svg class="w-5 h-5 text-gray-400 absolute left-4 top-1/2 -translate-y-1/2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
      </svg>
      <input v-model="query" @input="debounceSearch" @keyup.enter="doSearch" type="text"
        :placeholder="$t('search.placeholder')"
        class="w-full border border-gray-200 rounded-2xl pl-11 pr-12 py-3.5 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-red-400 focus:border-transparent transition"
        autofocus />
      <button v-if="query" @click="query = ''; results = {}; searched = false"
        class="absolute right-12 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
        </svg>
      </button>
      <button @click="doSearch" class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-red-500 transition">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
        </svg>
      </button>
    </div>

    <!-- Tabs -->
    <div v-if="searched" class="flex gap-1.5 mb-4 overflow-x-auto pb-1 scrollbar-hide">
      <button v-for="tab in tabList" :key="tab.key" @click="activeTab = tab.key"
        class="flex-shrink-0 px-3 py-1.5 rounded-full text-xs font-bold transition whitespace-nowrap"
        :class="activeTab === tab.key ? 'bg-red-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'">
        {{ tab.label }}
        <span v-if="tab.count" class="ml-1 opacity-70">({{ tab.count }})</span>
      </button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-center py-16 text-gray-400">
      <svg class="w-8 h-8 animate-spin mx-auto mb-3 text-gray-300" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
      </svg>
      {{ $t('search.searching') }}
    </div>

    <!-- No Results -->
    <div v-else-if="searched && !hasResults" class="text-center py-16">
      <svg class="w-16 h-16 mx-auto text-gray-300 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
      </svg>
      <p class="text-gray-500">"{{ query }}" {{ $t('search.no_results') }}</p>
    </div>

    <!-- Results -->
    <div v-else-if="hasResults" class="space-y-4">
      <!-- Posts -->
      <section v-if="(activeTab === 'all' || activeTab === 'posts') && filteredResults.posts?.length">
        <h2 class="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2 flex items-center gap-2">
          {{ $t('search.posts') }} ({{ filteredResults.posts.length }})
        </h2>
        <div class="space-y-2">
          <router-link v-for="p in filteredResults.posts" :key="'p'+p.id" :to="`/community/${p.board?.slug || 'general'}/${p.id}`"
            class="bg-white rounded-xl p-3.5 shadow-sm border border-gray-100 hover:shadow-md transition block">
            <div class="flex items-center gap-2 mb-1">
              <span class="text-xs bg-blue-50 text-blue-600 px-2 py-0.5 rounded-full font-semibold">{{ $t('search.post') }}</span>
              <span class="text-xs text-gray-400">{{ p.board?.name }}</span>
            </div>
            <p class="text-sm font-medium text-gray-800" v-html="highlight(p.title)"></p>
            <p class="text-xs text-gray-400 mt-1 line-clamp-1" v-html="highlight(stripHtml(p.content || '').slice(0, 100))"></p>
          </router-link>
        </div>
      </section>

      <!-- Jobs -->
      <section v-if="(activeTab === 'all' || activeTab === 'jobs') && filteredResults.jobs?.length">
        <h2 class="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">{{ $t('search.jobs') }} ({{ filteredResults.jobs.length }})</h2>
        <div class="space-y-2">
          <router-link v-for="j in filteredResults.jobs" :key="'j'+j.id" :to="`/jobs/${j.id}`"
            class="bg-white rounded-xl p-3.5 shadow-sm border border-gray-100 hover:shadow-md transition block">
            <span class="text-xs bg-green-50 text-green-600 px-2 py-0.5 rounded-full font-semibold">{{ $t('search.job') }}</span>
            <p class="text-sm font-medium text-gray-800 mt-1" v-html="highlight(j.title)"></p>
            <p class="text-xs text-gray-400 mt-0.5">{{ j.company || j.user?.name }}</p>
          </router-link>
        </div>
      </section>

      <!-- Market -->
      <section v-if="(activeTab === 'all' || activeTab === 'market') && filteredResults.market?.length">
        <h2 class="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">{{ $t('search.market') }} ({{ filteredResults.market.length }})</h2>
        <div class="space-y-2">
          <router-link v-for="m in filteredResults.market" :key="'m'+m.id" :to="`/market/${m.id}`"
            class="bg-white rounded-xl p-3.5 shadow-sm border border-gray-100 hover:shadow-md transition block">
            <span class="text-xs bg-orange-50 text-orange-600 px-2 py-0.5 rounded-full font-semibold">{{ $t('search.market_item') }}</span>
            <p class="text-sm font-medium text-gray-800 mt-1" v-html="highlight(m.title)"></p>
            <p class="text-xs text-gray-400 mt-0.5">${{ m.price?.toLocaleString() }}</p>
          </router-link>
        </div>
      </section>

      <!-- Business -->
      <section v-if="(activeTab === 'all' || activeTab === 'business') && filteredResults.businesses?.length">
        <h2 class="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">{{ $t('search.businesses') }} ({{ filteredResults.businesses.length }})</h2>
        <div class="space-y-2">
          <router-link v-for="b in filteredResults.businesses" :key="'b'+b.id" :to="`/business/${b.id}`"
            class="bg-white rounded-xl p-3.5 shadow-sm border border-gray-100 hover:shadow-md transition block">
            <span class="text-xs bg-purple-50 text-purple-600 px-2 py-0.5 rounded-full font-semibold">{{ $t('search.business') }}</span>
            <p class="text-sm font-medium text-gray-800 mt-1" v-html="highlight(b.name)"></p>
            <p class="text-xs text-gray-400 mt-0.5">{{ b.category }} · {{ b.city }}</p>
          </router-link>
        </div>
      </section>

      <!-- Events -->
      <section v-if="(activeTab === 'all' || activeTab === 'events') && filteredResults.events?.length">
        <h2 class="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">{{ $t('search.events') }} ({{ filteredResults.events.length }})</h2>
        <div class="space-y-2">
          <router-link v-for="e in filteredResults.events" :key="'e'+e.id" :to="`/events/${e.id}`"
            class="bg-white rounded-xl p-3.5 shadow-sm border border-gray-100 hover:shadow-md transition block">
            <span class="text-xs bg-pink-50 text-pink-600 px-2 py-0.5 rounded-full font-semibold">{{ $t('search.event') }}</span>
            <p class="text-sm font-medium text-gray-800 mt-1" v-html="highlight(e.title)"></p>
          </router-link>
        </div>
      </section>

      <!-- QA -->
      <section v-if="(activeTab === 'all' || activeTab === 'qa') && filteredResults.qa?.length">
        <h2 class="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Q&A ({{ filteredResults.qa.length }})</h2>
        <div class="space-y-2">
          <router-link v-for="q in filteredResults.qa" :key="'q'+q.id" :to="`/qa/${q.id}`"
            class="bg-white rounded-xl p-3.5 shadow-sm border border-gray-100 hover:shadow-md transition block">
            <span class="text-xs bg-indigo-50 text-indigo-600 px-2 py-0.5 rounded-full font-semibold">Q&A</span>
            <p class="text-sm font-medium text-gray-800 mt-1" v-html="highlight(q.title)"></p>
          </router-link>
        </div>
      </section>

      <!-- Recipes -->
      <section v-if="(activeTab === 'all' || activeTab === 'recipes') && filteredResults.recipes?.length">
        <h2 class="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">{{ $t('search.recipes') }} ({{ filteredResults.recipes.length }})</h2>
        <div class="space-y-2">
          <router-link v-for="r in filteredResults.recipes" :key="'r'+r.id" :to="`/recipes/${r.id}`"
            class="bg-white rounded-xl p-3.5 shadow-sm border border-gray-100 hover:shadow-md transition block">
            <span class="text-xs bg-yellow-50 text-yellow-700 px-2 py-0.5 rounded-full font-semibold">{{ $t('search.recipe') }}</span>
            <p class="text-sm font-medium text-gray-800 mt-1" v-html="highlight(r.title)"></p>
          </router-link>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useLangStore } from '../stores/lang'
import axios from 'axios'

const { $t } = useLangStore()

const query = ref('')
const results = ref({})
const loading = ref(false)
const searched = ref(false)
const activeTab = ref('all')

let debounceTimer = null

const hasResults = computed(() => {
  return Object.values(results.value).some(arr => arr?.length > 0)
})

const tabList = computed(() => {
  const tabs = [{ key: 'all', label: $t('search.all'), count: 0 }]
  const sections = [
    { key: 'posts', label: $t('search.posts'), data: results.value.posts },
    { key: 'jobs', label: $t('search.jobs'), data: results.value.jobs },
    { key: 'market', label: $t('search.market'), data: results.value.market },
    { key: 'business', label: $t('search.businesses'), data: results.value.businesses },
    { key: 'events', label: $t('search.events'), data: results.value.events },
    { key: 'qa', label: 'Q&A', data: results.value.qa },
    { key: 'recipes', label: $t('search.recipes'), data: results.value.recipes },
  ]
  let total = 0
  sections.forEach(s => {
    const count = s.data?.length || 0
    total += count
    if (count > 0) tabs.push({ key: s.key, label: s.label, count })
  })
  tabs[0].count = total
  return tabs
})

const filteredResults = computed(() => results.value)

function debounceSearch() {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    if (query.value.trim().length >= 2) doSearch()
  }, 400)
}

function stripHtml(html) {
  return (html || '').replace(/<[^>]*>/g, '')
}

function highlight(text) {
  if (!text || !query.value) return text || ''
  const q = query.value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  return text.replace(new RegExp(`(${q})`, 'gi'), '<mark class="bg-yellow-200 rounded px-0.5">$1</mark>')
}

async function doSearch() {
  if (!query.value.trim()) return
  loading.value = true
  searched.value = true
  try {
    const { data } = await axios.get('/api/search', { params: { q: query.value } })
    results.value = data
  } catch {
    results.value = {}
  }
  loading.value = false
}
</script>
