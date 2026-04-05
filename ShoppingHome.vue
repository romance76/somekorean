<template>
  <div class="max-w-[1200px] mx-auto px-4 py-4">
    <!-- 헤더 -->
    <div class="flex items-center justify-between mb-4">
      <div>
        <h1 class="text-xl font-bold text-gray-900">쇼핑 정보</h1>
        <p class="text-xs text-gray-500 mt-0.5">한인 / 미국 마트 주간 세일 & 특가</p>
      </div>
      <div class="text-xs text-gray-400">매주 업데이트</div>
    </div>

    <!-- 위치 배너 (위치 없을 때) -->
    <div v-if="!userLat && !locationLoading" class="bg-orange-50 border border-orange-200 rounded-xl p-3 mb-4 flex items-center gap-3">
      <svg class="w-5 h-5 text-orange-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/>
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/>
      </svg>
      <div class="flex-1">
        <p class="text-sm font-medium text-orange-800">위치를 설정하면 내 주변 마트를 볼 수 있어요</p>
        <p class="text-xs text-orange-600 mt-0.5">브라우저 위치 권한을 허용하거나 직접 설정해주세요</p>
      </div>
      <button @click="detectLocation" class="px-3 py-1.5 bg-orange-500 text-white text-xs rounded-lg font-medium hover:bg-orange-600 transition-colors flex-shrink-0">
        위치 감지
      </button>
    </div>

    <!-- 위치 로딩 -->
    <div v-if="locationLoading" class="bg-blue-50 border border-blue-200 rounded-xl p-3 mb-4 flex items-center gap-3">
      <div class="w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin flex-shrink-0"></div>
      <p class="text-sm text-blue-700">현재 위치를 감지하고 있습니다...</p>
    </div>

    <!-- 위치 + 거리 필터 바 -->
    <div class="bg-white rounded-xl border border-gray-100 shadow-sm p-3 mb-4">
      <div class="flex flex-wrap gap-2 items-center">
        <!-- 위치 표시 + 재감지 -->
        <button @click="detectLocation" class="flex items-center gap-1.5 text-sm text-gray-600 hover:text-blue-600 transition-colors"
          :title="userLat ? '현재 위치 재감지' : '위치 감지'">
          <svg class="w-4 h-4" :class="userLat ? 'text-blue-500' : 'text-gray-400'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/>
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/>
          </svg>
          <span v-if="userLat" class="text-xs text-blue-600 font-medium">내 주변</span>
          <span v-else class="text-xs text-gray-400">전체 지역</span>
        </button>

        <!-- 거리 슬라이더 버튼 -->
        <div v-if="userLat" class="flex gap-1">
          <button v-for="d in distanceOptions" :key="d"
            @click="setRadius(d)"
            :class="radiusMiles === d ? 'bg-blue-500 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'"
            class="px-2.5 py-1 rounded-full text-xs font-medium transition-colors">
            {{ d }}mi
          </button>
        </div>

        <!-- 검색 -->
        <div class="flex-1 min-w-[140px] ml-auto">
          <div class="relative">
            <input v-model="searchQuery" @input="debouncedSearch" type="text"
              placeholder="상품명 검색..."
              class="w-full border border-gray-200 rounded-lg px-3 py-1.5 text-sm pr-8 focus:outline-none focus:ring-2 focus:ring-blue-400" />
            <svg class="w-4 h-4 absolute right-2.5 top-1/2 -translate-y-1/2 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
            </svg>
          </div>
        </div>
      </div>
    </div>

    <!-- 카테고리 필터 탭 -->
    <div class="flex gap-1.5 overflow-x-auto pb-2 mb-3 scrollbar-hide">
      <button v-for="t in storeCategories" :key="t.value"
        @click="setStoreCategory(t.value)"
        :class="activeStoreCategory === t.value ? 'bg-blue-500 text-white shadow-md' : 'bg-white text-gray-600 border border-gray-200 hover:bg-gray-50'"
        class="flex-shrink-0 px-3 py-1.5 rounded-full text-xs font-medium transition-all">
        {{ t.label }}
      </button>
    </div>

    <!-- 마트 슬라이더 -->
    <div class="flex gap-3 overflow-x-auto pb-2 mb-4 scrollbar-hide">
      <button @click="selectStore(null)"
        :class="!selectedStoreId ? 'bg-blue-500 text-white border-blue-500 shadow-md' : 'bg-white text-gray-600 border-gray-200 hover:border-blue-300'"
        class="flex-shrink-0 flex flex-col items-center gap-1 border rounded-xl px-4 py-2.5 transition-all min-w-[72px]">
        <span class="text-lg">🏪</span>
        <span class="text-xs font-medium whitespace-nowrap">전체</span>
      </button>

      <button v-for="store in displayStores" :key="store.id"
        @click="selectStore(store)"
        :class="[
          selectedStoreId === store.id ? 'bg-blue-500 text-white border-blue-500 shadow-md' : 'bg-white text-gray-600 border-gray-200 hover:border-blue-300',
          !store._hasData ? 'opacity-50' : ''
        ]"
        class="flex-shrink-0 flex flex-col items-center gap-1 border rounded-xl px-4 py-2.5 transition-all min-w-[84px]">
        <div class="w-8 h-8 rounded-full overflow-hidden bg-gray-100 flex items-center justify-center">
          <img v-if="store.logo_url || store.logo" :src="store.logo_url || store.logo" :alt="store.name"
            class="w-full h-full object-contain" @error="$event.target.style.display='none'" />
          <span v-else class="text-sm font-bold text-gray-400">{{ (store.name || '?')[0] }}</span>
        </div>
        <span class="text-xs font-medium whitespace-nowrap truncate max-w-[72px]"
          :class="selectedStoreId === store.id ? 'text-white' : ''">{{ store.name }}</span>
        <div class="flex gap-1">
          <span v-if="store._nearbyCount > 0" class="text-[10px] opacity-70">{{ store._nearbyCount }}개</span>
          <span v-if="store.active_deals_count" class="text-[10px] opacity-70">{{ store.active_deals_count }}딜</span>
        </div>
      </button>
    </div>

    <!-- 마트 상세 섹션 (마트 선택 시) -->
    <div v-if="selectedStoreId && storeDetail" class="bg-white rounded-xl border border-gray-100 shadow-sm mb-5 overflow-hidden">
      <!-- 마트 헤더 -->
      <div class="p-4 border-b border-gray-100">
        <div class="flex items-center gap-3">
          <div class="w-12 h-12 rounded-xl overflow-hidden bg-gray-100 flex items-center justify-center flex-shrink-0">
            <img v-if="storeDetail.store?.logo_url || storeDetail.store?.logo"
              :src="storeDetail.store?.logo_url || storeDetail.store?.logo"
              class="w-full h-full object-contain" @error="$event.target.style.display='none'" />
            <span v-else class="text-lg font-bold text-gray-400">{{ (storeDetail.store?.name || '?')[0] }}</span>
          </div>
          <div class="flex-1">
            <h2 class="text-lg font-bold text-gray-900">{{ storeDetail.store?.name }}</h2>
            <p v-if="storeDetail.store?.name_en" class="text-xs text-gray-400">{{ storeDetail.store?.name_en }}</p>
          </div>
          <button @click="selectStore(null)" class="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center text-gray-500 hover:bg-gray-200 transition-colors">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>

        <!-- 가장 가까운 지점 정보 -->
        <div v-if="storeDetail.nearest_location" class="mt-3 bg-gray-50 rounded-lg p-3">
          <div class="flex items-center gap-2 mb-1.5">
            <span class="text-xs font-semibold text-gray-700">가장 가까운 지점</span>
            <span v-if="storeDetail.nearest_location.distance" class="text-xs text-blue-500 font-medium">
              {{ storeDetail.nearest_location.distance }} mi
            </span>
            <span v-if="storeDetail.nearest_location.is_open_now"
              class="inline-flex items-center gap-0.5 text-[10px] font-medium text-green-600 bg-green-50 px-1.5 py-0.5 rounded-full">
              <span class="w-1.5 h-1.5 bg-green-500 rounded-full"></span> 영업중
            </span>
            <span v-else
              class="inline-flex items-center gap-0.5 text-[10px] font-medium text-red-600 bg-red-50 px-1.5 py-0.5 rounded-full">
              <span class="w-1.5 h-1.5 bg-red-500 rounded-full"></span> 마감
            </span>
          </div>
          <p v-if="storeDetail.nearest_location.address" class="text-xs text-gray-600 mb-1">
            {{ storeDetail.nearest_location.address }}
            <span v-if="storeDetail.nearest_location.city">, {{ storeDetail.nearest_location.city }}</span>
            <span v-if="storeDetail.nearest_location.state"> {{ storeDetail.nearest_location.state }}</span>
            <span v-if="storeDetail.nearest_location.zip_code"> {{ storeDetail.nearest_location.zip_code }}</span>
          </p>
          <div class="flex flex-wrap items-center gap-3 text-xs text-gray-500">
            <span v-if="storeDetail.nearest_location.phone" class="flex items-center gap-1">
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"/>
              </svg>
              {{ storeDetail.nearest_location.phone }}
            </span>
            <span v-if="storeDetail.nearest_location.open_time" class="flex items-center gap-1">
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
              {{ storeDetail.nearest_location.open_time }} - {{ storeDetail.nearest_location.close_time }}
            </span>
            <a v-if="storeDetail.nearest_location.lat && storeDetail.nearest_location.lng"
              :href="'https://www.google.com/maps/dir/?api=1&destination=' + storeDetail.nearest_location.lat + ',' + storeDetail.nearest_location.lng"
              target="_blank" rel="noopener"
              class="flex items-center gap-1 text-blue-500 hover:text-blue-700 font-medium">
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"/>
              </svg>
              길찾기
            </a>
          </div>
        </div>

        <!-- 지점이 여러 개일 때 -->
        <div v-if="storeDetail.store?.locations?.length > 1" class="mt-2">
          <button @click="showAllLocations = !showAllLocations"
            class="text-xs text-blue-500 hover:text-blue-700 font-medium">
            {{ showAllLocations ? '접기' : '전체 ' + storeDetail.store.locations.length + '개 지점 보기' }}
          </button>
          <div v-if="showAllLocations" class="mt-2 space-y-2">
            <div v-for="loc in storeDetail.store.locations" :key="loc.id"
              class="flex items-center gap-2 p-2 bg-gray-50 rounded-lg text-xs text-gray-600">
              <span class="flex-1">
                <span v-if="loc.branch_name" class="font-medium">{{ loc.branch_name }} - </span>
                {{ loc.address }}<span v-if="loc.city">, {{ loc.city }}</span>
              </span>
              <a v-if="loc.lat && loc.lng"
                :href="'https://www.google.com/maps/dir/?api=1&destination=' + loc.lat + ',' + loc.lng"
                target="_blank" rel="noopener"
                class="text-blue-500 hover:text-blue-700 flex-shrink-0">
                지도
              </a>
            </div>
          </div>
        </div>
      </div>

      <!-- 탭: 이번주 세일 / 전단지 -->
      <div class="flex border-b border-gray-100">
        <button @click="storeTab = 'deals'"
          :class="storeTab === 'deals' ? 'text-blue-600 border-b-2 border-blue-600 font-semibold' : 'text-gray-500'"
          class="flex-1 py-2.5 text-sm text-center transition-colors">
          이번주 세일 ({{ storeDetail.deals?.length || 0 }})
        </button>
        <button @click="storeTab = 'flyers'"
          :class="storeTab === 'flyers' ? 'text-blue-600 border-b-2 border-blue-600 font-semibold' : 'text-gray-500'"
          class="flex-1 py-2.5 text-sm text-center transition-colors">
          전단지 ({{ storeDetail.flyers?.length || 0 }})
        </button>
      </div>

      <!-- 세일 탭 내용 -->
      <div v-if="storeTab === 'deals'" class="p-4">
        <!-- 카테고리 필터 (딜 안에서) -->
        <div class="flex gap-1.5 overflow-x-auto pb-2 mb-3 scrollbar-hide">
          <button @click="storeDealCategory = ''"
            :class="!storeDealCategory ? 'bg-blue-500 text-white' : 'bg-gray-100 text-gray-600'"
            class="flex-shrink-0 px-2.5 py-1 rounded-full text-xs font-medium transition-colors">
            전체
          </button>
          <button v-for="cat in storeDealCategories" :key="cat"
            @click="storeDealCategory = cat"
            :class="storeDealCategory === cat ? 'bg-blue-500 text-white' : 'bg-gray-100 text-gray-600'"
            class="flex-shrink-0 px-2.5 py-1 rounded-full text-xs font-medium transition-colors">
            {{ categoryEmoji(cat) }} {{ cat }}
          </button>
        </div>

        <div v-if="filteredStoreDeals.length === 0" class="text-center py-8 text-gray-400">
          <p class="text-sm">해당 카테고리의 세일 정보가 없습니다.</p>
        </div>

        <div v-else class="grid grid-cols-2 md:grid-cols-3 gap-3">
          <DealCard v-for="deal in filteredStoreDeals" :key="deal.id" :deal="deal" @click="openDeal(deal)" />
        </div>
      </div>

      <!-- 전단지 탭 내용 -->
      <div v-if="storeTab === 'flyers'" class="p-4">
        <div v-if="!storeDetail.flyers?.length" class="text-center py-8 text-gray-400">
          <p class="text-sm">등록된 전단지가 없습니다.</p>
        </div>
        <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-3">
          <a v-for="flyer in storeDetail.flyers" :key="flyer.id"
            :href="flyer.image_url || flyer.url" target="_blank" rel="noopener"
            class="block border border-gray-200 rounded-xl overflow-hidden hover:shadow-md transition-shadow">
            <img v-if="flyer.image_url" :src="flyer.image_url" class="w-full h-auto" @error="$event.target.style.display='none'" />
            <div class="p-3">
              <p class="text-sm font-medium text-gray-700">{{ flyer.title || '전단지' }}</p>
              <p v-if="flyer.valid_until" class="text-xs text-gray-400 mt-1">~ {{ formatDate(flyer.valid_until) }}</p>
            </div>
          </a>
        </div>
      </div>
    </div>

    <!-- 이번 주 특가 섹션 -->
    <div v-if="!selectedStoreId && specialDeals.length > 0" class="mb-5">
      <div class="flex items-center justify-between mb-3">
        <h2 class="text-base font-bold text-gray-900">이번 주 특가</h2>
        <span class="text-xs text-orange-500 font-medium">30%+ 할인</span>
      </div>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
        <div v-for="deal in specialDeals" :key="deal.id"
          @click="onSpecialDealClick(deal)"
          class="bg-white rounded-xl border border-orange-100 shadow-sm overflow-hidden cursor-pointer hover:shadow-md hover:-translate-y-0.5 transition-all relative">
          <div class="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-orange-400 to-red-500"></div>
          <div class="relative">
            <img v-if="deal.image_url" :src="deal.image_url" :alt="deal.title"
              class="w-full h-32 object-cover" @error="$event.target.style.display='none'" />
            <div v-else class="w-full h-32 bg-gradient-to-br from-orange-50 to-red-50 flex items-center justify-center">
              <span class="text-3xl">{{ categoryEmoji(deal.category) }}</span>
            </div>
            <div v-if="discountRate(deal)"
              class="absolute top-2 left-2 bg-red-500 text-white text-xs font-bold px-2 py-0.5 rounded-lg shadow">
              {{ discountRate(deal) }}%
            </div>
          </div>
          <div class="p-2.5">
            <div class="text-[10px] text-blue-500 font-medium mb-0.5">{{ deal.store?.name }}</div>
            <div class="text-xs font-semibold text-gray-900 line-clamp-2 mb-1.5 leading-tight">{{ deal.title }}</div>
            <div class="flex items-baseline gap-1.5">
              <span v-if="deal.sale_price" class="text-sm font-bold text-red-500">${{ deal.sale_price }}</span>
              <span v-if="deal.unit" class="text-[10px] text-gray-400">/ {{ deal.unit }}</span>
              <span v-if="deal.original_price" class="text-[10px] text-gray-400 line-through ml-auto">${{ deal.original_price }}</span>
            </div>
            <div v-if="deal.valid_until" class="text-[10px] text-gray-400 mt-1">~ {{ formatDate(deal.valid_until) }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 전체 딜 목록 -->
    <div v-if="!selectedStoreId">
      <div class="flex items-center justify-between mb-3">
        <h2 class="text-base font-bold text-gray-900">전체 세일 정보</h2>
        <span class="text-xs text-gray-400">{{ totalCount }}개</span>
      </div>

      <!-- 카테고리 필터 -->
      <div v-if="categories.length" class="flex gap-1.5 overflow-x-auto pb-2 mb-3 scrollbar-hide">
        <button @click="dealCategoryFilter = ''; loadDeals(true)"
          :class="!dealCategoryFilter ? 'bg-blue-500 text-white' : 'bg-gray-100 text-gray-600'"
          class="flex-shrink-0 px-2.5 py-1 rounded-full text-xs font-medium transition-colors">
          전체
        </button>
        <button v-for="cat in categories" :key="cat"
          @click="dealCategoryFilter = cat; loadDeals(true)"
          :class="dealCategoryFilter === cat ? 'bg-blue-500 text-white' : 'bg-gray-100 text-gray-600'"
          class="flex-shrink-0 px-2.5 py-1 rounded-full text-xs font-medium transition-colors">
          {{ categoryEmoji(cat) }} {{ cat }}
        </button>
      </div>

      <!-- 로딩 스켈레톤 -->
      <div v-if="dealsLoading && deals.length === 0" class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
        <div v-for="n in 8" :key="n" class="bg-white rounded-xl border border-gray-100 overflow-hidden">
          <div class="w-full h-36 bg-gray-100 animate-pulse"></div>
          <div class="p-2.5 space-y-2">
            <div class="h-3 bg-gray-100 rounded animate-pulse w-1/3"></div>
            <div class="h-3 bg-gray-100 rounded animate-pulse w-2/3"></div>
            <div class="h-4 bg-gray-100 rounded animate-pulse w-1/2"></div>
          </div>
        </div>
      </div>

      <!-- 빈 상태 -->
      <div v-else-if="!dealsLoading && deals.length === 0" class="text-center py-12 text-gray-400">
        <svg class="w-12 h-12 mx-auto mb-3 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 100 4 2 2 0 000-4z"/>
        </svg>
        <p class="text-sm">세일 정보가 없습니다.</p>
        <p v-if="userLat" class="text-xs mt-1">거리를 늘려보세요</p>
      </div>

      <!-- 딜 그리드 -->
      <div v-else class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
        <DealCard v-for="deal in deals" :key="deal.id" :deal="deal" @click="openDeal(deal)" />
      </div>

      <!-- 더 보기 -->
      <div v-if="hasMore && !dealsLoading && deals.length > 0" class="text-center mt-5">
        <button @click="loadMore"
          :disabled="dealsLoading"
          class="px-6 py-2.5 bg-gray-100 text-gray-600 rounded-full text-sm font-medium hover:bg-gray-200 transition-colors disabled:opacity-50">
          더 보기
        </button>
      </div>
      <div v-if="dealsLoading && deals.length > 0" class="text-center mt-5">
        <div class="w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
      </div>
    </div>

    <!-- 딜 상세 모달 -->
    <div v-if="selectedDeal" class="fixed inset-0 z-50 bg-black/50 flex items-end md:items-center justify-center p-4" @click.self="selectedDeal = null">
      <div class="bg-white rounded-2xl w-full max-w-md max-h-[85vh] overflow-y-auto">
        <div class="relative">
          <img v-if="selectedDeal.image_url" :src="selectedDeal.image_url"
            class="w-full h-48 object-cover rounded-t-2xl" @error="$event.target.style.display='none'" />
          <div v-else class="w-full h-48 bg-gradient-to-br from-blue-50 to-blue-100 rounded-t-2xl flex items-center justify-center">
            <span class="text-5xl">{{ categoryEmoji(selectedDeal.category) }}</span>
          </div>
          <button @click="selectedDeal = null"
            class="absolute top-3 right-3 w-8 h-8 bg-black/40 rounded-full flex items-center justify-center text-white hover:bg-black/60 transition-colors">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
          <div v-if="discountRate(selectedDeal)"
            class="absolute bottom-3 left-3 bg-red-500 text-white font-bold px-3 py-1 rounded-full text-sm shadow">
            {{ discountRate(selectedDeal) }}% 할인
          </div>
        </div>
        <div class="p-5">
          <div class="flex items-center gap-2 mb-2">
            <div class="w-6 h-6 rounded-full bg-gray-100 overflow-hidden flex-shrink-0">
              <img v-if="selectedDeal.store?.logo_url || selectedDeal.store?.logo"
                :src="selectedDeal.store?.logo_url || selectedDeal.store?.logo"
                class="w-full h-full object-contain" @error="$event.target.style.display='none'" />
            </div>
            <span class="text-sm font-semibold text-blue-600">{{ selectedDeal.store?.name }}</span>
          </div>
          <h3 class="text-lg font-bold text-gray-900 mb-2">{{ selectedDeal.title }}</h3>
          <div class="flex items-baseline gap-2 mb-3">
            <span v-if="selectedDeal.sale_price" class="text-2xl font-bold text-red-500">${{ selectedDeal.sale_price }}</span>
            <span v-else-if="selectedDeal.price" class="text-2xl font-bold text-red-500">{{ selectedDeal.price }}</span>
            <span v-if="selectedDeal.unit" class="text-sm text-gray-500">/ {{ selectedDeal.unit }}</span>
            <span v-if="selectedDeal.original_price" class="text-sm text-gray-400 line-through">${{ selectedDeal.original_price }}</span>
          </div>
          <p v-if="selectedDeal.description" class="text-sm text-gray-600 mb-3">{{ selectedDeal.description }}</p>
          <div v-if="selectedDeal.valid_from || selectedDeal.valid_until" class="text-xs text-orange-500 mb-4">
            <span v-if="selectedDeal.valid_from">{{ formatDate(selectedDeal.valid_from) }}</span>
            <span v-if="selectedDeal.valid_until"> ~ {{ formatDate(selectedDeal.valid_until) }}</span>
          </div>
          <div class="flex gap-2">
            <a v-if="dealLink(selectedDeal)" :href="dealLink(selectedDeal)" target="_blank" rel="noopener"
              class="flex-1 bg-blue-500 text-white text-center py-3 rounded-xl font-semibold hover:bg-blue-600 transition-colors">
              딜 바로가기
            </a>
            <a v-if="selectedDeal.store?.website" :href="selectedDeal.store.website" target="_blank" rel="noopener"
              :class="dealLink(selectedDeal) ? 'flex-1' : 'w-full'"
              class="bg-gray-100 text-gray-700 text-center py-3 rounded-xl font-semibold hover:bg-gray-200 transition-colors">
              {{ selectedDeal.store?.name }} 홈페이지
            </a>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue';
import { storeToRefs } from 'pinia';
import { useAuthStore } from '../../stores/auth';
import axios from 'axios';

// ==================== DealCard 인라인 컴포넌트 대체 (render 함수 사용 불가 -> template에서 직접) ====================
// DealCard는 아래 defineComponent로 정의

// ==================== Auth Store ====================
const authStore = useAuthStore();
const { user, isLoggedIn } = storeToRefs(authStore);

// ==================== State ====================
const userLat = ref(null);
const userLng = ref(null);
const radiusMiles = ref(30);
const locationLoading = ref(false);
const searchQuery = ref('');
const activeStoreCategory = ref('all');
const selectedStoreId = ref(null);

// Stores
const allStores = ref([]);
const nearbyData = ref([]);

// Store Detail
const storeDetail = ref(null);
const storeDetailLoading = ref(false);
const storeTab = ref('deals');
const storeDealCategory = ref('');
const showAllLocations = ref(false);

// Deals
const deals = ref([]);
const dealsLoading = ref(false);
const totalCount = ref(0);
const hasMore = ref(true);
const currentPage = ref(1);
const dealCategoryFilter = ref('');

// Special deals
const specialDeals = ref([]);

// Categories
const categories = ref([]);

// Selected deal modal
const selectedDeal = ref(null);

// ==================== Constants ====================
const distanceOptions = [10, 20, 30, 50];
const storeCategories = [
  { value: 'all', label: '전체' },
  { value: 'korean', label: '한인마트' },
  { value: 'american', label: '미국마트' },
  { value: 'asian', label: '아시안마트' },
  { value: 'online', label: '온라인' },
];

let debounceTimer = null;

// ==================== Computed ====================
const displayStores = computed(() => {
  let stores = allStores.value;
  if (activeStoreCategory.value !== 'all') {
    stores = stores.filter(s => s.type === activeStoreCategory.value);
  }

  // Merge nearby data
  return stores.map(s => {
    const nearbyInfo = nearbyData.value.find(n => (n.store?.id || n.store_id) === s.id);
    return {
      ...s,
      _nearbyCount: nearbyInfo ? nearbyInfo.locations_count : 0,
      _hasData: (s.active_deals_count || 0) > 0,
    };
  });
});

const storeDealCategories = computed(() => {
  if (!storeDetail.value?.deals) return [];
  const cats = [...new Set(storeDetail.value.deals.map(d => d.category).filter(Boolean))];
  return cats;
});

const filteredStoreDeals = computed(() => {
  if (!storeDetail.value?.deals) return [];
  if (!storeDealCategory.value) return storeDetail.value.deals;
  return storeDetail.value.deals.filter(d => d.category === storeDealCategory.value);
});

// ==================== Location ====================
function detectLocation() {
  if (!navigator.geolocation) return;
  locationLoading.value = true;
  navigator.geolocation.getCurrentPosition(
    (pos) => {
      userLat.value = pos.coords.latitude;
      userLng.value = pos.coords.longitude;
      locationLoading.value = false;
      loadNearbyStores();
      loadDeals(true);
      loadSpecialDeals();
    },
    () => {
      locationLoading.value = false;
    },
    { timeout: 10000, enableHighAccuracy: false }
  );
}

function setRadius(d) {
  radiusMiles.value = d;
  if (userLat.value) {
    loadNearbyStores();
    loadDeals(true);
    loadSpecialDeals();
  }
}

function setStoreCategory(val) {
  activeStoreCategory.value = val;
}

// ==================== API Calls ====================
async function loadStores() {
  try {
    const { data } = await axios.get('/api/shopping/stores');
    allStores.value = data;
  } catch (e) {
    console.error('loadStores error', e);
  }
}

async function loadNearbyStores() {
  if (!userLat.value || !userLng.value) return;
  try {
    const { data } = await axios.get('/api/shopping/nearby-stores', {
      params: { lat: userLat.value, lng: userLng.value, radius_miles: radiusMiles.value }
    });
    nearbyData.value = data;
  } catch (e) {
    console.error('loadNearbyStores error', e);
  }
}

async function loadDeals(reset = false) {
  if (reset) {
    deals.value = [];
    currentPage.value = 1;
    hasMore.value = true;
  }
  if (dealsLoading.value || !hasMore.value) return;
  dealsLoading.value = true;
  try {
    const params = {
      page: currentPage.value,
      category: dealCategoryFilter.value || undefined,
      search: searchQuery.value || undefined,
      lat: userLat.value || undefined,
      lng: userLng.value || undefined,
      radius_miles: userLat.value ? radiusMiles.value : undefined,
    };
    const { data } = await axios.get('/api/shopping/deals', { params });
    deals.value.push(...data.data);
    totalCount.value = data.total;
    hasMore.value = !!data.next_page_url;
    currentPage.value++;
  } catch (e) {
    console.error('loadDeals error', e);
  }
  dealsLoading.value = false;
}

async function loadSpecialDeals() {
  try {
    const params = {
      is_special: 1,
      lat: userLat.value || undefined,
      lng: userLng.value || undefined,
      radius_miles: userLat.value ? radiusMiles.value : undefined,
    };
    const { data } = await axios.get('/api/shopping/deals', { params });
    // 30% 이상 할인만
    specialDeals.value = (data.data || []).filter(d => {
      const rate = discountRate(d);
      return rate && rate >= 30;
    }).slice(0, 8);
  } catch (e) {
    console.error('loadSpecialDeals error', e);
  }
}

async function loadStoreDetail(storeId) {
  storeDetailLoading.value = true;
  storeTab.value = 'deals';
  storeDealCategory.value = '';
  showAllLocations.value = false;
  try {
    const params = {};
    if (userLat.value && userLng.value) {
      params.lat = userLat.value;
      params.lng = userLng.value;
    }
    const { data } = await axios.get(`/api/shopping/stores/${storeId}`, { params });
    storeDetail.value = data;
  } catch (e) {
    console.error('loadStoreDetail error', e);
  }
  storeDetailLoading.value = false;
}

async function loadCategories() {
  try {
    const { data } = await axios.get('/api/shopping/categories');
    categories.value = data;
  } catch (e) {
    console.error('loadCategories error', e);
  }
}

// ==================== Actions ====================
function selectStore(store) {
  if (!store) {
    selectedStoreId.value = null;
    storeDetail.value = null;
    return;
  }
  selectedStoreId.value = store.id;
  loadStoreDetail(store.id);
}

function onSpecialDealClick(deal) {
  if (deal.store_id || deal.store?.id) {
    const storeId = deal.store_id || deal.store?.id;
    const store = allStores.value.find(s => s.id === storeId);
    if (store) {
      selectStore(store);
      return;
    }
  }
  openDeal(deal);
}

function openDeal(deal) {
  selectedDeal.value = deal;
}

function loadMore() {
  loadDeals();
}

function debouncedSearch() {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(() => loadDeals(true), 400);
}

// ==================== Helpers ====================
function discountRate(deal) {
  if (deal.discount_percent) return deal.discount_percent;
  if (deal.original_price && deal.sale_price && deal.original_price > 0) {
    return Math.round((1 - deal.sale_price / deal.original_price) * 100);
  }
  return null;
}

function categoryEmoji(cat) {
  const map = {
    '정육': '🥩', '수산': '🐟', '채소': '🥬', '과일': '🍎',
    '과자': '🍪', '음료': '🥤', '냉동': '🧊', '유제품': '🥛',
    '정육/수산': '🥩', '채소/과일': '🥬',
    '전자기기': '💻', '생활용품': '🧴', '패션/의류': '👕',
    '건강/뷰티': '💊', '식품/음료': '🍜', '스포츠': '⚽',
    '냉동식품': '❄️', '기타': '🛒',
  };
  return map[cat] || '🛒';
}

function formatDate(d) {
  if (!d) return '';
  return new Date(d).toLocaleDateString('ko-KR', { month: 'short', day: 'numeric' });
}

function dealLink(deal) {
  if (deal.source_url && deal.source_url.startsWith('http')) return deal.source_url;
  if (deal.url && deal.url.startsWith('http') && !deal.url.includes('somekorean.com/shopping/deal-')) {
    return deal.url;
  }
  return null;
}

// ==================== Init ====================
onMounted(async () => {
  // 로그인 유저 위치 사용
  if (isLoggedIn.value && user.value?.lat && user.value?.lng) {
    userLat.value = user.value.lat;
    userLng.value = user.value.lng;
    if (user.value.default_radius) {
      radiusMiles.value = user.value.default_radius;
    }
  } else {
    // 브라우저 Geolocation 시도
    detectLocation();
  }

  // 병렬 로드
  await Promise.all([
    loadStores(),
    loadDeals(true),
    loadSpecialDeals(),
    loadCategories(),
  ]);

  // 위치가 있으면 nearby도 로드
  if (userLat.value && userLng.value) {
    loadNearbyStores();
  }
});
</script>

<script>
// DealCard 인라인 컴포넌트
const DealCard = {
  name: 'DealCard',
  props: { deal: Object },
  emits: ['click'],
  template: `
    <div @click="$emit('click')"
      class="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden cursor-pointer hover:shadow-md hover:-translate-y-0.5 transition-all">
      <div class="relative">
        <img v-if="deal.image_url" :src="deal.image_url" :alt="deal.title"
          class="w-full h-36 object-cover" @error="$event.target.style.display='none'" />
        <div v-else class="w-full h-36 bg-gradient-to-br from-gray-50 to-gray-100 flex items-center justify-center">
          <span class="text-4xl">{{ emoji }}</span>
        </div>
        <div v-if="rate"
          class="absolute top-2 left-2 bg-red-500 text-white text-xs font-bold px-2 py-0.5 rounded-lg shadow">
          {{ rate }}%
        </div>
        <div v-if="deal.valid_until"
          class="absolute top-2 right-2 bg-black/50 text-white text-[10px] px-1.5 py-0.5 rounded">
          ~ {{ fmtDate(deal.valid_until) }}
        </div>
      </div>
      <div class="p-2.5">
        <div class="flex items-center gap-1 mb-0.5">
          <span class="text-[10px] text-blue-500 font-medium">{{ deal.store?.name }}</span>
        </div>
        <div class="text-xs font-semibold text-gray-900 line-clamp-2 mb-1.5 leading-tight">{{ deal.title }}</div>
        <div class="flex items-baseline gap-1">
          <span v-if="deal.sale_price" class="text-sm font-bold text-red-500">\${{ deal.sale_price }}</span>
          <span v-else-if="deal.original_price" class="text-sm font-bold text-gray-800">\${{ deal.original_price }}</span>
          <span v-else-if="deal.price" class="text-sm font-bold text-gray-800">{{ deal.price }}</span>
          <span v-else class="text-xs text-gray-400">가격 문의</span>
          <span v-if="deal.unit" class="text-[10px] text-gray-400">/ {{ deal.unit }}</span>
        </div>
        <div v-if="deal.original_price && deal.sale_price" class="text-[10px] text-gray-400 line-through">
          원가 \${{ deal.original_price }}
        </div>
      </div>
    </div>
  `,
  computed: {
    rate() {
      if (this.deal.discount_percent) return this.deal.discount_percent;
      if (this.deal.original_price && this.deal.sale_price && this.deal.original_price > 0) {
        return Math.round((1 - this.deal.sale_price / this.deal.original_price) * 100);
      }
      return null;
    },
    emoji() {
      const map = {
        '정육':'🥩','수산':'🐟','채소':'🥬','과일':'🍎','과자':'🍪','음료':'🥤',
        '냉동':'🧊','유제품':'🥛','정육/수산':'🥩','채소/과일':'🥬',
        '전자기기':'💻','생활용품':'🧴','패션/의류':'👕','건강/뷰티':'💊',
        '식품/음료':'🍜','스포츠':'⚽','냉동식품':'❄️','기타':'🛒',
      };
      return map[this.deal.category] || '🛒';
    },
  },
  methods: {
    fmtDate(d) {
      if (!d) return '';
      return new Date(d).toLocaleDateString('ko-KR', { month: 'short', day: 'numeric' });
    }
  }
};

export default {
  components: { DealCard },
};
</script>
