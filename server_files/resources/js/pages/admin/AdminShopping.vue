<template>
  <div class="p-6 space-y-6">
    <!-- Page Title -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">쇼핑정보 관리</h1>
        <p class="text-sm text-gray-500 mt-0.5">딜 및 파트너 업체를 관리합니다</p>
      </div>
      <div class="flex gap-2">
        <button @click="activeTab = 'deals'; showCreateDeal = true"
          class="flex items-center gap-2 bg-blue-600 text-white px-4 py-2.5 rounded-xl text-sm font-medium hover:bg-blue-700 transition">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          딜 등록
        </button>
      </div>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="bg-white rounded-2xl p-5 shadow-sm border border-gray-100">
        <p class="text-xs text-gray-500 mb-1">전체 딜</p>
        <p class="text-2xl font-bold text-gray-900">{{ stats.total }}</p>
        <p class="text-xs text-gray-400 mt-1">등록된 딜 전체</p>
      </div>
      <div class="bg-white rounded-2xl p-5 shadow-sm border border-gray-100">
        <p class="text-xs text-gray-500 mb-1">오늘 등록</p>
        <p class="text-2xl font-bold text-blue-600">{{ stats.today }}</p>
        <p class="text-xs text-gray-400 mt-1">오늘 신규 등록</p>
      </div>
      <div class="bg-white rounded-2xl p-5 shadow-sm border border-gray-100">
        <p class="text-xs text-gray-500 mb-1">만료 예정</p>
        <p class="text-2xl font-bold text-orange-500">{{ stats.expiring }}</p>
        <p class="text-xs text-gray-400 mt-1">7일 내 만료</p>
      </div>
      <div class="bg-white rounded-2xl p-5 shadow-sm border border-gray-100">
        <p class="text-xs text-gray-500 mb-1">파트너 업체</p>
        <p class="text-2xl font-bold text-purple-600">{{ stats.partners }}</p>
        <p class="text-xs text-gray-400 mt-1">등록 파트너</p>
      </div>
    </div>

    <!-- Tabs -->
    <div class="flex gap-1 bg-gray-100 p-1 rounded-xl w-fit">
      <button @click="activeTab = 'deals'"
        class="px-5 py-2 rounded-lg text-sm font-medium transition"
        :class="activeTab === 'deals' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500 hover:text-gray-700'">
        쇼핑 딜
      </button>
      <button @click="activeTab = 'partners'"
        class="px-5 py-2 rounded-lg text-sm font-medium transition"
        :class="activeTab === 'partners' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500 hover:text-gray-700'">
        파트너 업체
      </button>
    </div>

    <!-- Deals Tab -->
    <div v-if="activeTab === 'deals'" class="space-y-4">
      <!-- Filters -->
      <div class="bg-white rounded-2xl p-4 shadow-sm border border-gray-100">
        <div class="flex flex-wrap gap-3 items-center">
          <select v-model="dealFilter.category"
            class="border border-gray-200 rounded-xl px-3 py-2 text-sm focus:outline-none focus:border-blue-400 bg-gray-50">
            <option value="">전체 카테고리</option>
            <option value="식품">식품</option>
            <option value="뷰티">뷰티</option>
            <option value="전자">전자</option>
            <option value="패션">패션</option>
            <option value="생활">생활</option>
          </select>

          <select v-model="dealFilter.status"
            class="border border-gray-200 rounded-xl px-3 py-2 text-sm focus:outline-none focus:border-blue-400 bg-gray-50">
            <option value="">전체 상태</option>
            <option value="active">활성</option>
            <option value="expiring">만료 예정</option>
            <option value="expired">만료</option>
          </select>

          <div class="flex-1 min-w-[200px]">
            <input v-model="dealFilter.search" type="text" placeholder="딜 제목 또는 업체명 검색..."
              class="w-full border border-gray-200 rounded-xl px-3 py-2 text-sm focus:outline-none focus:border-blue-400 bg-gray-50" />
          </div>

          <button @click="dealFilter.category = ''; dealFilter.status = ''; dealFilter.search = ''"
            class="text-sm text-gray-500 hover:text-gray-700 px-3 py-2 rounded-xl hover:bg-gray-100 transition">
            초기화
          </button>
        </div>
      </div>

      <!-- Deals Table -->
      <div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead>
              <tr class="bg-gray-50 border-b border-gray-100">
                <th class="text-left px-5 py-3.5 text-xs font-semibold text-gray-500 uppercase tracking-wide">딜 정보</th>
                <th class="text-left px-4 py-3.5 text-xs font-semibold text-gray-500 uppercase tracking-wide">카테고리</th>
                <th class="text-left px-4 py-3.5 text-xs font-semibold text-gray-500 uppercase tracking-wide">할인율</th>
                <th class="text-left px-4 py-3.5 text-xs font-semibold text-gray-500 uppercase tracking-wide">원가/할인가</th>
                <th class="text-left px-4 py-3.5 text-xs font-semibold text-gray-500 uppercase tracking-wide">만료일</th>
                <th class="text-left px-4 py-3.5 text-xs font-semibold text-gray-500 uppercase tracking-wide">조회</th>
                <th class="text-left px-4 py-3.5 text-xs font-semibold text-gray-500 uppercase tracking-wide">상태</th>
                <th class="text-left px-4 py-3.5 text-xs font-semibold text-gray-500 uppercase tracking-wide">관리</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-50">
              <tr v-for="deal in filteredDeals" :key="deal.id" class="hover:bg-gray-50 transition">
                <td class="px-5 py-4">
                  <p class="font-medium text-gray-900 line-clamp-1 max-w-[260px]">{{ deal.title }}</p>
                  <p class="text-xs text-gray-400 mt-0.5">{{ deal.store }}</p>
                </td>
                <td class="px-4 py-4">
                  <span class="px-2.5 py-1 rounded-lg text-xs font-medium"
                    :class="categoryColors[deal.category] || 'bg-gray-100 text-gray-600'">
                    {{ deal.category }}
                  </span>
                </td>
                <td class="px-4 py-4">
                  <span class="text-red-600 font-bold">-{{ deal.discount }}%</span>
                </td>
                <td class="px-4 py-4">
                  <p class="text-gray-400 line-through text-xs">${{ deal.original }}</p>
                  <p class="font-semibold text-gray-900">${{ deal.sale_price }}</p>
                </td>
                <td class="px-4 py-4 text-gray-600 whitespace-nowrap">{{ deal.expires }}</td>
                <td class="px-4 py-4 text-gray-500">{{ deal.views.toLocaleString() }}</td>
                <td class="px-4 py-4">
                  <span class="px-2.5 py-1 rounded-full text-xs font-medium"
                    :class="dealStatusColors[deal.status] || 'bg-gray-100 text-gray-500'">
                    {{ dealStatusLabels[deal.status] || deal.status }}
                  </span>
                </td>
                <td class="px-4 py-4">
                  <div class="flex items-center gap-1.5">
                    <button @click="openDealDetail(deal)"
                      class="px-3 py-1.5 text-xs bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100 transition font-medium">
                      수정
                    </button>
                    <button @click="deleteDeal(deal.id)"
                      class="px-3 py-1.5 text-xs bg-red-50 text-red-500 rounded-lg hover:bg-red-100 transition font-medium">
                      삭제
                    </button>
                  </div>
                </td>
              </tr>
              <tr v-if="filteredDeals.length === 0">
                <td colspan="8" class="text-center py-12 text-gray-400">조건에 맞는 딜이 없습니다.</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="px-5 py-3 border-t border-gray-100">
          <span class="text-xs text-gray-400">총 {{ filteredDeals.length }}건</span>
        </div>
      </div>
    </div>

    <!-- Partners Tab -->
    <div v-if="activeTab === 'partners'" class="space-y-4">
      <div class="flex justify-end">
        <button @click="showCreatePartner = true"
          class="flex items-center gap-2 bg-purple-600 text-white px-4 py-2.5 rounded-xl text-sm font-medium hover:bg-purple-700 transition">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          업체 등록
        </button>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div v-for="partner in partners" :key="partner.id"
          class="bg-white rounded-2xl p-5 shadow-sm border border-gray-100">
          <div class="flex items-start justify-between mb-3">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 rounded-xl flex items-center justify-center text-xl"
                :style="{ backgroundColor: partner.iconBg }">
                {{ partner.icon }}
              </div>
              <div>
                <p class="font-semibold text-gray-900">{{ partner.name }}</p>
                <span class="text-xs px-2 py-0.5 rounded-md"
                  :class="categoryColors[partner.category] || 'bg-gray-100 text-gray-600'">
                  {{ partner.category }}
                </span>
              </div>
            </div>
            <!-- Toggle active -->
            <button @click="partner.active = !partner.active"
              class="relative inline-flex h-6 w-11 items-center rounded-full transition-colors"
              :class="partner.active ? 'bg-green-500' : 'bg-gray-200'">
              <span class="inline-block h-4 w-4 transform rounded-full bg-white shadow transition-transform"
                :class="partner.active ? 'translate-x-6' : 'translate-x-1'" />
            </button>
          </div>

          <div class="space-y-1.5 text-sm">
            <div class="flex items-center gap-2 text-gray-600">
              <svg class="w-4 h-4 text-gray-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
              </svg>
              {{ partner.contact }}
            </div>
            <div v-if="partner.rss" class="flex items-center gap-2 text-gray-500">
              <svg class="w-4 h-4 text-gray-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 5c7.18 0 13 5.82 13 13M6 11a7 7 0 017 7M6 17a1 1 0 110-2 1 1 0 010 2z" />
              </svg>
              <span class="text-xs truncate">{{ partner.rss }}</span>
            </div>
          </div>

          <div class="flex gap-2 mt-4">
            <button class="flex-1 py-1.5 text-xs border border-gray-200 text-gray-600 rounded-lg hover:bg-gray-50 transition">
              수정
            </button>
            <button @click="deletePartner(partner.id)"
              class="flex-1 py-1.5 text-xs bg-red-50 text-red-500 rounded-lg hover:bg-red-100 transition">
              삭제
            </button>
          </div>
        </div>

        <div v-if="partners.length === 0"
          class="col-span-2 text-center py-12 text-gray-400 bg-white rounded-2xl border border-gray-100">
          등록된 파트너 업체가 없습니다.
        </div>
      </div>
    </div>

    <!-- Create Deal Modal -->
    <div v-if="showCreateDeal" class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4" @click.self="showCreateDeal = false">
      <div class="bg-white rounded-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto shadow-2xl">
        <div class="flex items-center justify-between p-6 border-b border-gray-100">
          <h2 class="font-bold text-gray-900 text-lg">딜 등록</h2>
          <button @click="showCreateDeal = false" class="text-gray-400 hover:text-gray-600 transition">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <form @submit.prevent="submitDeal" class="p-6 space-y-4">
          <div>
            <label class="text-sm font-medium text-gray-700 block mb-1.5">딜 제목 *</label>
            <input v-model="dealForm.title" type="text" required placeholder="예: H마트 LA갈비 20% 할인"
              class="w-full border border-gray-200 rounded-xl px-3.5 py-2.5 text-sm focus:outline-none focus:border-blue-400" />
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="text-sm font-medium text-gray-700 block mb-1.5">업체명 *</label>
              <input v-model="dealForm.store" type="text" required placeholder="예: H마트 LA"
                class="w-full border border-gray-200 rounded-xl px-3.5 py-2.5 text-sm focus:outline-none focus:border-blue-400" />
            </div>
            <div>
              <label class="text-sm font-medium text-gray-700 block mb-1.5">카테고리 *</label>
              <select v-model="dealForm.category" required
                class="w-full border border-gray-200 rounded-xl px-3.5 py-2.5 text-sm focus:outline-none focus:border-blue-400 bg-white">
                <option value="">선택</option>
                <option value="식품">식품</option>
                <option value="뷰티">뷰티</option>
                <option value="전자">전자</option>
                <option value="패션">패션</option>
                <option value="생활">생활</option>
              </select>
            </div>
          </div>

          <div>
            <label class="text-sm font-medium text-gray-700 block mb-1.5">이미지 URL</label>
            <input v-model="dealForm.image_url" type="url" placeholder="https://..."
              class="w-full border border-gray-200 rounded-xl px-3.5 py-2.5 text-sm focus:outline-none focus:border-blue-400" />
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="text-sm font-medium text-gray-700 block mb-1.5">원가 ($) *</label>
              <input v-model="dealForm.original" type="number" required min="0" step="0.01" placeholder="0.00"
                class="w-full border border-gray-200 rounded-xl px-3.5 py-2.5 text-sm focus:outline-none focus:border-blue-400" />
            </div>
            <div>
              <label class="text-sm font-medium text-gray-700 block mb-1.5">할인율 (%) *</label>
              <input v-model="dealForm.discount" type="number" required min="1" max="100" placeholder="0"
                class="w-full border border-gray-200 rounded-xl px-3.5 py-2.5 text-sm focus:outline-none focus:border-blue-400" />
            </div>
          </div>

          <!-- Computed sale price preview -->
          <div v-if="dealForm.original && dealForm.discount"
            class="bg-blue-50 rounded-xl px-4 py-3 text-sm text-blue-700">
            할인가: <strong>${{ computedSalePrice }}</strong>
            ({{ dealForm.discount }}% 할인)
          </div>

          <div>
            <label class="text-sm font-medium text-gray-700 block mb-1.5">설명</label>
            <textarea v-model="dealForm.description" rows="2" placeholder="딜 설명을 입력하세요..."
              class="w-full border border-gray-200 rounded-xl px-3.5 py-2.5 text-sm focus:outline-none focus:border-blue-400 resize-none"></textarea>
          </div>

          <div>
            <label class="text-sm font-medium text-gray-700 block mb-1.5">링크 URL</label>
            <input v-model="dealForm.link_url" type="url" placeholder="https://..."
              class="w-full border border-gray-200 rounded-xl px-3.5 py-2.5 text-sm focus:outline-none focus:border-blue-400" />
          </div>

          <div>
            <label class="text-sm font-medium text-gray-700 block mb-1.5">만료일 *</label>
            <input v-model="dealForm.expires" type="date" required
              class="w-full border border-gray-200 rounded-xl px-3.5 py-2.5 text-sm focus:outline-none focus:border-blue-400" />
          </div>

          <div class="flex gap-3 pt-2">
            <button type="button" @click="showCreateDeal = false"
              class="flex-1 py-2.5 border border-gray-200 text-gray-600 rounded-xl text-sm font-medium hover:bg-gray-50 transition">
              취소
            </button>
            <button type="submit"
              class="flex-1 py-2.5 bg-blue-600 text-white rounded-xl text-sm font-medium hover:bg-blue-700 transition">
              등록하기
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Create Partner Modal -->
    <div v-if="showCreatePartner" class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4" @click.self="showCreatePartner = false">
      <div class="bg-white rounded-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto shadow-2xl">
        <div class="flex items-center justify-between p-6 border-b border-gray-100">
          <h2 class="font-bold text-gray-900 text-lg">파트너 업체 등록</h2>
          <button @click="showCreatePartner = false" class="text-gray-400 hover:text-gray-600 transition">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <form @submit.prevent="submitPartner" class="p-6 space-y-4">
          <div>
            <label class="text-sm font-medium text-gray-700 block mb-1.5">업체명 *</label>
            <input v-model="partnerForm.name" type="text" required placeholder="예: H마트 LA"
              class="w-full border border-gray-200 rounded-xl px-3.5 py-2.5 text-sm focus:outline-none focus:border-blue-400" />
          </div>

          <div>
            <label class="text-sm font-medium text-gray-700 block mb-1.5">카테고리 *</label>
            <select v-model="partnerForm.category" required
              class="w-full border border-gray-200 rounded-xl px-3.5 py-2.5 text-sm focus:outline-none focus:border-blue-400 bg-white">
              <option value="">선택</option>
              <option value="식품">식품</option>
              <option value="뷰티">뷰티</option>
              <option value="전자">전자</option>
              <option value="패션">패션</option>
              <option value="생활">생활</option>
            </select>
          </div>

          <div>
            <label class="text-sm font-medium text-gray-700 block mb-1.5">연락처</label>
            <input v-model="partnerForm.contact" type="text" placeholder="예: (213) 555-0100"
              class="w-full border border-gray-200 rounded-xl px-3.5 py-2.5 text-sm focus:outline-none focus:border-blue-400" />
          </div>

          <div>
            <label class="text-sm font-medium text-gray-700 block mb-1.5">RSS 피드 URL</label>
            <input v-model="partnerForm.rss" type="url" placeholder="https://..."
              class="w-full border border-gray-200 rounded-xl px-3.5 py-2.5 text-sm focus:outline-none focus:border-blue-400" />
          </div>

          <div class="flex gap-3 pt-2">
            <button type="button" @click="showCreatePartner = false"
              class="flex-1 py-2.5 border border-gray-200 text-gray-600 rounded-xl text-sm font-medium hover:bg-gray-50 transition">
              취소
            </button>
            <button type="submit"
              class="flex-1 py-2.5 bg-purple-600 text-white rounded-xl text-sm font-medium hover:bg-purple-700 transition">
              등록하기
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Deal Detail/Edit Modal -->
    <div v-if="selectedDeal" class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4" @click.self="selectedDeal = null">
      <div class="bg-white rounded-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto shadow-2xl">
        <div class="flex items-center justify-between p-6 border-b border-gray-100">
          <h2 class="font-bold text-gray-900 text-lg">딜 수정</h2>
          <button @click="selectedDeal = null" class="text-gray-400 hover:text-gray-600 transition">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="p-6 space-y-4">
          <div>
            <label class="text-sm font-medium text-gray-700 block mb-1.5">딜 제목</label>
            <input v-model="selectedDeal.title" type="text"
              class="w-full border border-gray-200 rounded-xl px-3.5 py-2.5 text-sm focus:outline-none focus:border-blue-400" />
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="text-sm font-medium text-gray-700 block mb-1.5">업체명</label>
              <input v-model="selectedDeal.store" type="text"
                class="w-full border border-gray-200 rounded-xl px-3.5 py-2.5 text-sm focus:outline-none focus:border-blue-400" />
            </div>
            <div>
              <label class="text-sm font-medium text-gray-700 block mb-1.5">할인율 (%)</label>
              <input v-model="selectedDeal.discount" type="number" min="1" max="100"
                class="w-full border border-gray-200 rounded-xl px-3.5 py-2.5 text-sm focus:outline-none focus:border-blue-400" />
            </div>
          </div>
          <div>
            <label class="text-sm font-medium text-gray-700 block mb-1.5">만료일</label>
            <input v-model="selectedDeal.expires" type="date"
              class="w-full border border-gray-200 rounded-xl px-3.5 py-2.5 text-sm focus:outline-none focus:border-blue-400" />
          </div>
          <div>
            <label class="text-sm font-medium text-gray-700 block mb-1.5">상태</label>
            <select v-model="selectedDeal.status"
              class="w-full border border-gray-200 rounded-xl px-3.5 py-2.5 text-sm focus:outline-none focus:border-blue-400 bg-white">
              <option value="active">활성</option>
              <option value="expiring">만료 예정</option>
              <option value="expired">만료</option>
            </select>
          </div>
          <div class="flex gap-3 pt-2">
            <button @click="selectedDeal = null"
              class="flex-1 py-2.5 border border-gray-200 text-gray-600 rounded-xl text-sm font-medium hover:bg-gray-50 transition">
              취소
            </button>
            <button @click="saveEditDeal"
              class="flex-1 py-2.5 bg-blue-600 text-white rounded-xl text-sm font-medium hover:bg-blue-700 transition">
              저장
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, reactive, onMounted } from 'vue'
import axios from 'axios'

const activeTab = ref('deals')
const loadingDeals = ref(false)

// Deals data - 더미 데이터 (API 실패시 폴백)
const deals = ref([
  { id:1, title:'H마트 주간 세일 - LA갈비 20% 할인', store:'H마트 LA', discount:20, original:35, sale_price:28, category:'식품', expires:'2026-04-05', views:245, status:'active', image_url:null },
  { id:2, title:'설화수 윤조에센스 15% 할인', store:'면세닷컴', discount:15, original:95, sale_price:80.75, category:'뷰티', expires:'2026-04-15', views:189, status:'active', image_url:null },
  { id:3, title:'삼성 갤럭시 S24 $150 할인', store:'베스트바이', discount:10, original:1200, sale_price:1050, category:'전자', expires:'2026-03-31', views:412, status:'active', image_url:null },
  { id:4, title:'한국 과자 박스 세트', store:'아마존', discount:25, original:40, sale_price:30, category:'식품', expires:'2026-04-20', views:78, status:'active', image_url:null },
  { id:5, title:'라네즈 수분크림 세트', store:'세포라', discount:20, original:65, sale_price:52, category:'뷰티', expires:'2026-04-10', views:156, status:'active', image_url:null },
  { id:6, title:'코스트코 한우 갈비 특가', store:'코스트코', discount:30, original:58, sale_price:40.6, category:'식품', expires:'2026-03-30', views:534, status:'expiring', image_url:null },
])

async function loadDeals() {
  loadingDeals.value = true
  try {
    const { data } = await axios.get('/api/admin/shopping/deals')
    const items = data.data || data
    if (Array.isArray(items) && items.length > 0) {
      deals.value = items.map(d => ({
        ...d,
        discount: d.discount_percent || d.discount || 0,
        original: d.original_price || d.original || 0,
        sale_price: d.sale_price || 0,
        store: d.store || d.source || '-',
        expires: d.expires_at ? d.expires_at.slice(0, 10) : '',
        views: d.views || 0,
        status: d.is_active ? (d.expires_at && new Date(d.expires_at) < new Date(Date.now() + 7 * 86400000) ? 'expiring' : 'active') : 'expired',
      }))
    }
  } catch { /* API 미구현시 더미 유지 */ } finally {
    loadingDeals.value = false
  }
}

onMounted(() => loadDeals())

// Partners data
const partners = ref([
  { id:1, name:'H마트 LA', category:'식품', contact:'(213) 388-3400', rss:'https://hmart.com/rss/deals', active:true, icon:'🛒', iconBg:'#dcfce7' },
  { id:2, name:'면세닷컴', category:'뷰티', contact:'support@meonse.com', rss:'https://meonse.com/feed', active:true, icon:'💄', iconBg:'#fce7f3' },
  { id:3, name:'코리안 마트', category:'식품', contact:'(310) 555-0192', rss:'', active:false, icon:'🏪', iconBg:'#fef9c3' },
])

const dealFilter = reactive({ category: '', status: '', search: '' })
const showCreateDeal = ref(false)
const showCreatePartner = ref(false)
const selectedDeal = ref(null)

const dealForm = reactive({
  title: '', store: '', category: '', image_url: '', original: '', discount: '',
  description: '', link_url: '', expires: ''
})

const partnerForm = reactive({
  name: '', category: '', contact: '', rss: ''
})

const categoryColors = {
  '식품':  'bg-green-100 text-green-700',
  '뷰티':  'bg-pink-100 text-pink-700',
  '전자':  'bg-blue-100 text-blue-700',
  '패션':  'bg-purple-100 text-purple-700',
  '생활':  'bg-yellow-100 text-yellow-700',
}

const dealStatusColors = {
  'active':   'bg-green-100 text-green-700',
  'expiring': 'bg-orange-100 text-orange-700',
  'expired':  'bg-gray-100 text-gray-500',
}

const dealStatusLabels = {
  'active':   '활성',
  'expiring': '만료 예정',
  'expired':  '만료',
}

const stats = computed(() => ({
  total: deals.value.length,
  today: 0, // Would be computed from created_at in real data
  expiring: deals.value.filter(d => d.status === 'expiring').length,
  partners: partners.value.filter(p => p.active).length,
}))

const filteredDeals = computed(() => {
  return deals.value.filter(d => {
    if (dealFilter.category && d.category !== dealFilter.category) return false
    if (dealFilter.status && d.status !== dealFilter.status) return false
    if (dealFilter.search) {
      const q = dealFilter.search.toLowerCase()
      if (!d.title.toLowerCase().includes(q) && !d.store.toLowerCase().includes(q)) return false
    }
    return true
  })
})

const computedSalePrice = computed(() => {
  if (!dealForm.original || !dealForm.discount) return 0
  const orig = parseFloat(dealForm.original)
  const disc = parseFloat(dealForm.discount)
  return (orig * (1 - disc / 100)).toFixed(2)
})

function openDealDetail(deal) {
  selectedDeal.value = { ...deal }
}

function saveEditDeal() {
  const idx = deals.value.findIndex(d => d.id === selectedDeal.value.id)
  if (idx !== -1) {
    deals.value[idx] = { ...selectedDeal.value }
  }
  selectedDeal.value = null
}

function deleteDeal(id) {
  if (!confirm('이 딜을 삭제하시겠습니까?')) return
  deals.value = deals.value.filter(d => d.id !== id)
}

function deletePartner(id) {
  if (!confirm('이 파트너 업체를 삭제하시겠습니까?')) return
  partners.value = partners.value.filter(p => p.id !== id)
}

function submitDeal() {
  const orig = parseFloat(dealForm.original) || 0
  const disc = parseFloat(dealForm.discount) || 0
  const newDeal = {
    id: Date.now(),
    title: dealForm.title,
    store: dealForm.store,
    discount: disc,
    original: orig,
    sale_price: parseFloat((orig * (1 - disc / 100)).toFixed(2)),
    category: dealForm.category,
    expires: dealForm.expires,
    views: 0,
    status: 'active',
  }
  deals.value.unshift(newDeal)
  showCreateDeal.value = false
  Object.assign(dealForm, { title:'', store:'', category:'', image_url:'', original:'', discount:'', description:'', link_url:'', expires:'' })
}

function submitPartner() {
  const icons = { '식품':'🛒', '뷰티':'💄', '전자':'💻', '패션':'👗', '생활':'🏠' }
  const bgs   = { '식품':'#dcfce7', '뷰티':'#fce7f3', '전자':'#dbeafe', '패션':'#f3e8ff', '생활':'#fef9c3' }
  const newPartner = {
    id: Date.now(),
    name: partnerForm.name,
    category: partnerForm.category,
    contact: partnerForm.contact || '-',
    rss: partnerForm.rss || '',
    active: true,
    icon: icons[partnerForm.category] || '🏪',
    iconBg: bgs[partnerForm.category] || '#f3f4f6',
  }
  partners.value.unshift(newPartner)
  showCreatePartner.value = false
  Object.assign(partnerForm, { name:'', category:'', contact:'', rss:'' })
}
</script>
