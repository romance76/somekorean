<template>
  <DetailTemplate
    :item="job"
    :loading="loading"
    :breadcrumb="breadcrumb"
    :images="jobImages"
    :showAuthor="false"
    :showActions="true"
    :showComments="false"
    commentType="job"
    @like="toggleLike"
    @bookmark="toggleBookmark"
  >
    <template #header>
      <!-- Company Info Grid -->
      <div v-if="job" class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-5">
        <div class="flex items-center gap-2 mb-4">
          <span v-if="job.job_type" class="text-xs bg-blue-50 dark:bg-blue-900/30 text-blue-600 px-2 py-1 rounded-full font-medium">
            {{ jobTypeLabel(job.job_type) }}
          </span>
          <span v-if="job.is_urgent" class="text-xs bg-red-50 text-red-600 px-2 py-1 rounded-full font-medium">
            {{ locale === 'ko' ? '급구' : 'Urgent' }}
          </span>
          <div v-if="canEdit" class="ml-auto flex gap-2">
            <router-link :to="`/jobs/write?edit=${job.id}`" class="text-xs text-gray-400 hover:text-gray-600">{{ locale === 'ko' ? '수정' : 'Edit' }}</router-link>
            <button @click="deleteJob" class="text-xs text-red-400 hover:text-red-600">{{ locale === 'ko' ? '삭제' : 'Delete' }}</button>
          </div>
        </div>
        <h1 class="text-lg font-bold text-gray-900 dark:text-white mb-3">{{ job.title }}</h1>

        <div class="grid grid-cols-2 md:grid-cols-3 gap-3 bg-gray-50 dark:bg-gray-700 rounded-lg p-4 text-sm">
          <div>
            <span class="text-gray-500 dark:text-gray-400 text-xs">{{ locale === 'ko' ? '회사명' : 'Company' }}</span>
            <p class="font-medium text-gray-800 dark:text-white mt-0.5">{{ job.company_name || (locale === 'ko' ? '비공개' : 'Private') }}</p>
          </div>
          <div>
            <span class="text-gray-500 dark:text-gray-400 text-xs">{{ locale === 'ko' ? '지역' : 'Location' }}</span>
            <p class="font-medium text-gray-800 dark:text-white mt-0.5">{{ job.region || '-' }}</p>
          </div>
          <div>
            <span class="text-gray-500 dark:text-gray-400 text-xs">{{ locale === 'ko' ? '급여' : 'Salary' }}</span>
            <p class="font-medium text-green-600 dark:text-green-400 mt-0.5">{{ job.salary_range || (locale === 'ko' ? '협의' : 'Negotiable') }}</p>
          </div>
          <div>
            <span class="text-gray-500 dark:text-gray-400 text-xs">{{ locale === 'ko' ? '마감일' : 'Deadline' }}</span>
            <p class="font-medium text-gray-800 dark:text-white mt-0.5">{{ job.deadline || (locale === 'ko' ? '상시' : 'Open') }}</p>
          </div>
          <div v-if="job.work_hours">
            <span class="text-gray-500 dark:text-gray-400 text-xs">{{ locale === 'ko' ? '근무시간' : 'Work Hours' }}</span>
            <p class="font-medium text-gray-800 dark:text-white mt-0.5">{{ job.work_hours }}</p>
          </div>
        </div>
      </div>
    </template>

    <template #body>
      <!-- Description -->
      <div class="prose prose-sm max-w-none text-gray-800 dark:text-gray-200 whitespace-pre-wrap leading-relaxed mb-6">
        {{ job?.content }}
      </div>

      <!-- Contact Info -->
      <div v-if="job?.contact_email || job?.contact_phone" class="border-t border-gray-100 dark:border-gray-700 pt-4 space-y-2 text-sm">
        <h3 class="font-semibold text-gray-700 dark:text-gray-200 mb-2">{{ locale === 'ko' ? '연락처 정보' : 'Contact' }}</h3>
        <div v-if="job.contact_email" class="flex items-center gap-2 text-gray-600 dark:text-gray-400">
          <span>📧</span><span>{{ job.contact_email }}</span>
        </div>
        <div v-if="job.contact_phone" class="flex items-center gap-2 text-gray-600 dark:text-gray-400">
          <span>📞</span><span>{{ job.contact_phone }}</span>
        </div>
      </div>

      <!-- Apply Button -->
      <div class="mt-6 flex gap-3">
        <a v-if="job?.contact_email" :href="`mailto:${job.contact_email}`"
          class="flex-1 flex items-center justify-center gap-2 py-3 bg-blue-600 text-white rounded-xl font-medium text-sm hover:bg-blue-700 transition">
          📧 {{ locale === 'ko' ? '이메일로 지원하기' : 'Apply via Email' }}
        </a>
        <a v-if="job?.contact_phone" :href="`tel:${job.contact_phone}`"
          class="flex-1 flex items-center justify-center gap-2 py-3 bg-green-600 text-white rounded-xl font-medium text-sm hover:bg-green-700 transition">
          📞 {{ locale === 'ko' ? '전화하기' : 'Call' }}
        </a>
      </div>
    </template>

    <template #sidebar>
      <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 overflow-hidden">
        <h3 class="font-bold text-gray-800 dark:text-white text-sm px-4 py-3 border-b border-gray-100 dark:border-gray-700">
          {{ locale === 'ko' ? '최신 채용공고' : 'Latest Jobs' }}
        </h3>
        <div v-if="sidebarJobs.length">
          <router-link v-for="(rj, idx) in sidebarJobs" :key="rj.id" :to="`/jobs/${rj.id}`"
            class="flex gap-3 py-3 px-3 hover:bg-blue-50/40 dark:hover:bg-gray-700/50 transition border-b border-gray-50 dark:border-gray-700 last:border-0"
            :class="rj.id == job?.id ? 'bg-blue-50 dark:bg-gray-700' : ''">
            <span class="flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center text-xs font-black mt-0.5"
              :class="rj.id === job?.id ? 'bg-blue-600 text-white' : 'bg-gray-100 dark:bg-gray-600 text-gray-500'">
              {{ idx + 1 }}
            </span>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium text-gray-800 dark:text-gray-200 line-clamp-2 leading-snug">{{ rj.title }}</p>
              <p class="text-[11px] text-gray-400 mt-0.5">{{ rj.company_name || '' }} · {{ rj.region || '' }}</p>
              <span class="text-[11px] text-green-600 font-medium">{{ rj.salary_range || '' }}</span>
            </div>
          </router-link>
        </div>
        <div v-else class="text-center py-10 text-gray-400 text-sm">{{ locale === 'ko' ? '채용공고가 없습니다' : 'No jobs' }}</div>
      </div>
    </template>
  </DetailTemplate>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { useLangStore } from '../../stores/lang'
import DetailTemplate from '../../components/templates/DetailTemplate.vue'
import axios from 'axios'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const langStore = useLangStore()
const locale = computed(() => langStore.locale)

const job = ref(null)
const loading = ref(true)
const sidebarJobs = ref([])

const canEdit = computed(() => auth.user && (auth.user.id === job.value?.user_id || auth.user.is_admin))
const breadcrumb = computed(() => [
  { label: locale.value === 'ko' ? '구인구직' : 'Jobs', to: '/jobs' },
  { label: job.value?.title || '' }
])
const jobImages = computed(() => job.value?.images?.length ? job.value.images : null)

function jobTypeLabel(type) {
  const ko = locale.value === 'ko'
  return { full_time: ko ? '풀타임' : 'Full-time', part_time: ko ? '파트타임' : 'Part-time', contract: ko ? '계약직' : 'Contract' }[type] ?? type
}

async function toggleLike() {
  if (!auth.isLoggedIn) { router.push('/auth/login'); return }
  try {
    const { data } = await axios.post(`/api/jobs/${job.value.id}/like`)
    job.value.is_liked = data.liked
    job.value.like_count = data.like_count
  } catch { /* empty */ }
}

async function toggleBookmark() {
  if (!auth.isLoggedIn) { router.push('/auth/login'); return }
  try {
    const { data } = await axios.post(`/api/jobs/${job.value.id}/bookmark`)
    job.value.is_bookmarked = data.bookmarked
  } catch { /* empty */ }
}

async function deleteJob() {
  if (!confirm(locale.value === 'ko' ? '공고를 삭제하시겠습니까?' : 'Delete this job post?')) return
  try {
    await axios.delete(`/api/jobs/${job.value.id}`)
    router.push('/jobs')
  } catch { /* empty */ }
}

async function loadSidebarJobs() {
  try {
    const { data } = await axios.get('/api/jobs', { params: { per_page: 5 } })
    sidebarJobs.value = (data.data || data || []).slice(0, 5)
  } catch { /* empty */ }
}

watch(() => route.params.id, () => { if (route.params.id) loadJob() })

async function loadJob() {
  loading.value = true
  try {
    const { data } = await axios.get(`/api/jobs/${route.params.id}`)
    job.value = data
    loadSidebarJobs()
  } catch { job.value = null }
  loading.value = false
}

onMounted(loadJob)
</script>
