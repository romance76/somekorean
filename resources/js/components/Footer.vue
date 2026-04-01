<template>
  <footer class="bg-gray-900 text-gray-300 mt-8">
    <div class="max-w-[1200px] mx-auto px-4 py-10">
      <div class="grid grid-cols-2 md:grid-cols-4 gap-8">
        <!-- Brand -->
        <div class="col-span-2 md:col-span-1">
          <div class="flex items-center gap-2 mb-3">
            <span class="text-2xl">🇰🇷</span>
            <span class="text-white font-black text-lg">SomeKorean</span>
          </div>
          <p class="text-sm text-gray-400 leading-relaxed">
            {{ locale === 'ko'
              ? '미국 한인 커뮤니티의 모든 것. 구인구직부터 부동산, 친목까지 한 곳에서.'
              : 'Everything for Korean Americans. Jobs, real estate, community and more in one place.' }}
          </p>
          <div class="flex gap-3 mt-4">
            <a href="#" class="w-8 h-8 bg-gray-700 hover:bg-blue-600 rounded-full flex items-center justify-center transition text-xs">f</a>
            <a href="#" class="w-8 h-8 bg-gray-700 hover:bg-sky-500 rounded-full flex items-center justify-center transition text-xs">𝕏</a>
            <a href="#" class="w-8 h-8 bg-gray-700 hover:bg-pink-600 rounded-full flex items-center justify-center transition text-sm">▶</a>
          </div>
        </div>

        <!-- Services -->
        <div>
          <h4 class="text-white font-bold text-sm mb-3">{{ locale === 'ko' ? '서비스' : 'Services' }}</h4>
          <ul class="space-y-2 text-sm">
            <li><RouterLink to="/community" class="hover:text-white transition">{{ locale === 'ko' ? '커뮤니티' : 'Community' }}</RouterLink></li>
            <li><RouterLink to="/jobs" class="hover:text-white transition">{{ locale === 'ko' ? '구인구직' : 'Jobs' }}</RouterLink></li>
            <li><RouterLink to="/market" class="hover:text-white transition">{{ locale === 'ko' ? '중고장터' : 'Marketplace' }}</RouterLink></li>
            <li><RouterLink to="/realestate" class="hover:text-white transition">{{ locale === 'ko' ? '부동산' : 'Real Estate' }}</RouterLink></li>
            <li><RouterLink to="/directory" class="hover:text-white transition">{{ locale === 'ko' ? '업소록' : 'Directory' }}</RouterLink></li>
            <li><RouterLink to="/ride" class="hover:text-white transition">{{ locale === 'ko' ? '알바 라이드' : 'Ride Service' }}</RouterLink></li>
          </ul>
        </div>

        <!-- Community -->
        <div>
          <h4 class="text-white font-bold text-sm mb-3">{{ locale === 'ko' ? '커뮤니티' : 'Community' }}</h4>
          <ul class="space-y-2 text-sm">
            <li><RouterLink to="/chat" class="hover:text-white transition">{{ locale === 'ko' ? '실시간 채팅' : 'Live Chat' }}</RouterLink></li>
            <li><RouterLink to="/clubs" class="hover:text-white transition">{{ locale === 'ko' ? '동호회' : 'Clubs' }}</RouterLink></li>
            <li><RouterLink to="/events" class="hover:text-white transition">{{ locale === 'ko' ? '이벤트' : 'Events' }}</RouterLink></li>
            <li><RouterLink to="/friends" class="hover:text-white transition">{{ locale === 'ko' ? '친구 찾기' : 'Find Friends' }}</RouterLink></li>
            <li><RouterLink to="/match" class="hover:text-white transition">{{ locale === 'ko' ? '매칭' : 'Matching' }}</RouterLink></li>
            <li><RouterLink to="/news" class="hover:text-white transition">{{ locale === 'ko' ? '한인 뉴스' : 'Korean News' }}</RouterLink></li>
          </ul>
        </div>

        <!-- Info -->
        <div>
          <h4 class="text-white font-bold text-sm mb-3">{{ locale === 'ko' ? '정보' : 'Info' }}</h4>
          <ul class="space-y-2 text-sm">
            <li><RouterLink to="/elder" class="hover:text-white transition">{{ locale === 'ko' ? '노인 안심 서비스' : 'Elder Care' }}</RouterLink></li>
            <li><RouterLink to="/mentor" class="hover:text-white transition">{{ locale === 'ko' ? '멘토링' : 'Mentoring' }}</RouterLink></li>
            <li><RouterLink to="/groupbuy" class="hover:text-white transition">{{ locale === 'ko' ? '공동구매' : 'Group Buy' }}</RouterLink></li>
            <li><RouterLink to="/games" class="hover:text-white transition">{{ locale === 'ko' ? '게임 & 포인트' : 'Games & Points' }}</RouterLink></li>
            <li><RouterLink to="/shorts" class="hover:text-white transition">{{ locale === 'ko' ? '숏츠' : 'Shorts' }}</RouterLink></li>
            <li><RouterLink to="/ai" class="hover:text-white transition">{{ locale === 'ko' ? 'AI 검색' : 'AI Search' }}</RouterLink></li>
          </ul>
        </div>
      </div>

      <!-- Bottom Bar -->
      <div class="border-t border-gray-700 mt-8 pt-6 flex flex-col sm:flex-row items-center justify-between gap-3">
        <p class="text-xs text-gray-500">
          © {{ new Date().getFullYear() }} SomeKorean. {{ locale === 'ko' ? '모든 권리 보유.' : 'All rights reserved.' }}
        </p>
        <div class="flex gap-4 text-xs text-gray-500">
          <a href="#" class="hover:text-gray-300 transition">{{ locale === 'ko' ? '이용약관' : 'Terms' }}</a>
          <a href="#" class="hover:text-gray-300 transition">{{ locale === 'ko' ? '개인정보처리방침' : 'Privacy' }}</a>
          <a href="#" class="hover:text-gray-300 transition">{{ locale === 'ko' ? '고객지원' : 'Support' }}</a>
        </div>
      </div>
    </div>
  </footer>
</template>

<script setup>
import { computed } from 'vue'
import { useLangStore } from '../stores/lang'

const langStore = useLangStore()
const locale = computed(() => langStore.locale)
</script>
