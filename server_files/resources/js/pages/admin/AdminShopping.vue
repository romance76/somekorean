<template>
  <div class="p-6 max-w-7xl mx-auto">
    <h1 class="text-2xl font-bold mb-6">쇼핑/마트 관리</h1>

    <!-- Tabs -->
    <div class="flex border-b mb-6">
      <button v-for="(tab, i) in tabs" :key="i"
        @click="activeTab = i"
        :class="['px-4 py-2 font-medium border-b-2 -mb-px transition', activeTab === i ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700']">
        {{ tab }}
      </button>
    </div>

    <!-- Tab 0: 마트 관리 -->
    <div v-if="activeTab === 0">
      <div class="flex justify-between items-center mb-4">
        <h2 class="text-lg font-semibold">마트 목록</h2>
        <button @click="openStoreModal()" class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">+ 마트 추가</button>
      </div>
      <div class="overflow-x-auto bg-white rounded shadow">
        <table class="w-full text-sm">
          <thead class="bg-gray-50">
            <tr>
              <th class="p-3 text-left">로고</th>
              <th class="p-3 text-left">마트명</th>
              <th class="p-3 text-left">카테고리</th>
              <th class="p-3 text-center">지점수</th>
              <th class="p-3 text-left">스크래핑</th>
              <th class="p-3 text-left">마지막수집</th>
              <th class="p-3 text-center">상태</th>
              <th class="p-3 text-center">관리</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="s in stores" :key="s.id" class="border-t hover:bg-gray-50">
              <td class="p-3"><img v-if="s.logo_url || s.logo" :src="s.logo_url || s.logo" class="w-8 h-8 rounded object-cover" /><span v-else class="text-gray-300">-</span></td>
              <td class="p-3">
                <div class="font-medium">{{ s.name }}</div>
                <div class="text-xs text-gray-400">{{ s.name_en }}</div>
              </td>
              <td class="p-3"><span class="px-2 py-0.5 bg-gray-100 rounded text-xs">{{ s.category || '-' }}</span></td>
              <td class="p-3 text-center">{{ s.locations_count || 0 }}</td>
              <td class="p-3 text-xs">{{ s.scrape_method || '-' }}</td>
              <td class="p-3 text-xs text-gray-500">{{ s.last_scraped_at ? new Date(s.last_scraped_at).toLocaleDateString() : '-' }}</td>
              <td class="p-3 text-center">
                <span :class="s.is_active ? 'text-green-500' : 'text-red-400'" class="text-xs font-medium">{{ s.is_active ? '활성' : '비활성' }}</span>
              </td>
              <td class="p-3 text-center space-x-1">
                <button @click="openStoreModal(s)" class="text-blue-500 hover:underline text-xs">수정</button>
                <button @click="openLocationModal(s)" class="text-purple-500 hover:underline text-xs">지점</button>
                <button @click="deleteStore(s.id)" class="text-red-500 hover:underline text-xs">삭제</button>
              </td>
            </tr>
            <tr v-if="!stores.length"><td colspan="8" class="p-8 text-center text-gray-400">등록된 마트가 없습니다</td></tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Tab 1: 딜/세일 관리 -->
    <div v-if="activeTab === 1">
      <div class="flex justify-between items-center mb-4">
        <div class="flex gap-2 items-center">
          <h2 class="text-lg font-semibold">딜/세일 목록</h2>
          <select v-model="dealFilter.store_id" @change="loadDeals" class="border rounded px-2 py-1 text-sm">
            <option value="">전체 마트</option>
            <option v-for="s in stores" :key="s.id" :value="s.id">{{ s.name }}</option>
          </select>
          <select v-model="dealFilter.category" @change="loadDeals" class="border rounded px-2 py-1 text-sm">
            <option value="">전체 카테고리</option>
            <option v-for="c in dealCategories" :key="c" :value="c">{{ c }}</option>
          </select>
          <label class="flex items-center gap-1 text-sm">
            <input type="checkbox" v-model="dealFilter.has_error" @change="loadDeals" />
            가격오류만
          </label>
        </div>
        <div class="flex gap-2">
          <button @click="bulkDeleteErrors" class="bg-red-500 text-white px-3 py-2 rounded text-sm hover:bg-red-600">일괄삭제 - 오류항목</button>
          <button @click="openDealModal()" class="bg-blue-500 text-white px-3 py-2 rounded text-sm hover:bg-blue-600">+ 딜 수동등록</button>
        </div>
      </div>
      <div class="overflow-x-auto bg-white rounded shadow">
        <table class="w-full text-sm">
          <thead class="bg-gray-50">
            <tr>
              <th class="p-3 text-left">마트</th>
              <th class="p-3 text-left">타이틀</th>
              <th class="p-3 text-right">가격</th>
              <th class="p-3 text-right">세일가</th>
              <th class="p-3 text-right">할인율</th>
              <th class="p-3 text-left">카테고리</th>
              <th class="p-3 text-left">유효기간</th>
              <th class="p-3 text-center">관리</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="d in deals" :key="d.id" class="border-t hover:bg-gray-50">
              <td class="p-3 text-xs">{{ d.store?.name || '-' }}</td>
              <td class="p-3">
                <div class="max-w-xs truncate">{{ d.title }}</div>
              </td>
              <td class="p-3 text-right" :class="{'text-red-500 font-bold': !d.price || d.price == 0}">${{ d.price || '0' }}</td>
              <td class="p-3 text-right" :class="{'text-red-500 font-bold': !d.sale_price || d.sale_price == 0}">${{ d.sale_price || '0' }}</td>
              <td class="p-3 text-right" :class="{'text-red-500 font-bold': !d.discount_percent || d.discount_percent == 0}">{{ d.discount_percent || 0 }}%</td>
              <td class="p-3 text-xs">{{ d.category || '-' }}</td>
              <td class="p-3 text-xs text-gray-500">{{ d.valid_until ? d.valid_until.substring(0,10) : '무기한' }}</td>
              <td class="p-3 text-center space-x-1">
                <button @click="openDealModal(d)" class="text-blue-500 hover:underline text-xs">수정</button>
                <button @click="deleteDeal(d.id)" class="text-red-500 hover:underline text-xs">삭제</button>
              </td>
            </tr>
            <tr v-if="!deals.length"><td colspan="8" class="p-8 text-center text-gray-400">딜이 없습니다</td></tr>
          </tbody>
        </table>
      </div>
      <div v-if="dealsPagination.last_page > 1" class="flex justify-center gap-2 mt-4">
        <button v-for="p in dealsPagination.last_page" :key="p" @click="loadDeals(p)"
          :class="['px-3 py-1 rounded text-sm', dealsPagination.current_page === p ? 'bg-blue-500 text-white' : 'bg-gray-100 hover:bg-gray-200']">
          {{ p }}
        </button>
      </div>
    </div>

    <!-- Tab 2: 전단지 관리 -->
    <div v-if="activeTab === 2">
      <div class="flex justify-between items-center mb-4">
        <h2 class="text-lg font-semibold">전단지 관리</h2>
        <button @click="openFlyerModal()" class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">+ 전단지 등록</button>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div v-for="f in flyers" :key="f.id" class="bg-white rounded shadow overflow-hidden">
          <img :src="f.image_url" class="w-full h-48 object-cover" @error="$event.target.src='/images/placeholder.png'" />
          <div class="p-3">
            <div class="font-medium text-sm">{{ f.store?.name }} - {{ f.title || '전단지' }}</div>
            <div class="text-xs text-gray-500 mt-1">{{ f.valid_from?.substring(0,10) || '-' }} ~ {{ f.valid_until?.substring(0,10) || '-' }}</div>
            <div class="mt-2 flex justify-end">
              <button @click="deleteFlyer(f.id)" class="text-red-500 text-xs hover:underline">삭제</button>
            </div>
          </div>
        </div>
        <div v-if="!flyers.length" class="col-span-3 text-center text-gray-400 py-12">등록된 전단지가 없습니다</div>
      </div>
    </div>

    <!-- Tab 3: 스크래핑 현황 -->
    <div v-if="activeTab === 3">
      <h2 class="text-lg font-semibold mb-4">스크래핑 현황</h2>

      <div class="bg-white rounded shadow mb-6">
        <table class="w-full text-sm">
          <thead class="bg-gray-50">
            <tr>
              <th class="p-3 text-left">마트</th>
              <th class="p-3 text-left">스크래핑 방식</th>
              <th class="p-3 text-left">마지막 수집</th>
              <th class="p-3 text-center">활성 딜</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="s in stores.filter(s => s.scrape_method)" :key="s.id" class="border-t">
              <td class="p-3 font-medium">{{ s.name }}</td>
              <td class="p-3 text-xs">{{ s.scrape_method }}</td>
              <td class="p-3 text-xs">{{ s.last_scraped_at ? new Date(s.last_scraped_at).toLocaleString() : '-' }}</td>
              <td class="p-3 text-center">{{ s.deals_count || 0 }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <h3 class="font-semibold mb-3">최근 스크래핑 로그 (50개)</h3>
      <div class="bg-white rounded shadow overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="bg-gray-50">
            <tr>
              <th class="p-3 text-left">마트</th>
              <th class="p-3 text-center">상태</th>
              <th class="p-3 text-center">수집 딜</th>
              <th class="p-3 text-left">시작</th>
              <th class="p-3 text-left">종료</th>
              <th class="p-3 text-left">에러</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="l in scrapeLogs" :key="l.id" class="border-t">
              <td class="p-3">{{ l.store?.name || '-' }}</td>
              <td class="p-3 text-center">
                <span :class="l.status === 'success' ? 'text-green-500' : 'text-red-500'" class="text-xs font-medium">{{ l.status }}</span>
              </td>
              <td class="p-3 text-center">{{ l.deals_count || 0 }}</td>
              <td class="p-3 text-xs">{{ l.started_at ? new Date(l.started_at).toLocaleString() : '-' }}</td>
              <td class="p-3 text-xs">{{ l.finished_at ? new Date(l.finished_at).toLocaleString() : '-' }}</td>
              <td class="p-3 text-xs text-red-400 max-w-xs truncate">{{ l.error_message || '-' }}</td>
            </tr>
            <tr v-if="!scrapeLogs.length"><td colspan="6" class="p-8 text-center text-gray-400">스크래핑 로그가 없습니다</td></tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Store Modal -->
    <div v-if="showStoreModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50" @click.self="showStoreModal=false">
      <div class="bg-white rounded-lg shadow-xl w-full max-w-lg mx-4 max-h-[90vh] overflow-y-auto">
        <div class="p-6">
          <h3 class="text-lg font-bold mb-4">{{ storeForm.id ? '마트 수정' : '마트 추가' }}</h3>
          <div class="space-y-3">
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">마트명 (한)</label>
                <input v-model="storeForm.name" class="w-full border rounded px-3 py-2 text-sm" />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">마트명 (영)</label>
                <input v-model="storeForm.name_en" class="w-full border rounded px-3 py-2 text-sm" />
              </div>
            </div>
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">체인코드</label>
                <input v-model="storeForm.chain_name" class="w-full border rounded px-3 py-2 text-sm" />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">카테고리</label>
                <select v-model="storeForm.category" class="w-full border rounded px-3 py-2 text-sm">
                  <option value="">선택</option>
                  <option value="korean_mart">한인마트</option>
                  <option value="us_mart">미국마트</option>
                  <option value="asian_mart">아시안마트</option>
                  <option value="online">온라인</option>
                </select>
              </div>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">웹사이트</label>
              <input v-model="storeForm.website" class="w-full border rounded px-3 py-2 text-sm" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">로고 URL</label>
              <input v-model="storeForm.logo_url" class="w-full border rounded px-3 py-2 text-sm" />
            </div>
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">주간광고 URL</label>
                <input v-model="storeForm.weekly_ad_url" class="w-full border rounded px-3 py-2 text-sm" />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">RSS URL</label>
                <input v-model="storeForm.rss_url" class="w-full border rounded px-3 py-2 text-sm" />
              </div>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">스크래핑 방식</label>
              <select v-model="storeForm.scrape_method" class="w-full border rounded px-3 py-2 text-sm">
                <option value="">없음</option>
                <option value="rss">RSS</option>
                <option value="api">API</option>
                <option value="scrape">웹 스크래핑</option>
                <option value="manual">수동</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">메모</label>
              <textarea v-model="storeForm.memo" rows="2" class="w-full border rounded px-3 py-2 text-sm"></textarea>
            </div>
            <div class="flex items-center gap-2">
              <input type="checkbox" v-model="storeForm.is_active" id="store_active" />
              <label for="store_active" class="text-sm">활성</label>
            </div>
          </div>
          <div class="flex justify-end gap-2 mt-6">
            <button @click="showStoreModal=false" class="px-4 py-2 border rounded text-sm hover:bg-gray-50">취소</button>
            <button @click="saveStore" class="px-4 py-2 bg-blue-500 text-white rounded text-sm hover:bg-blue-600">저장</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Location Modal -->
    <div v-if="showLocationModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50" @click.self="showLocationModal=false">
      <div class="bg-white rounded-lg shadow-xl w-full max-w-2xl mx-4 max-h-[90vh] overflow-y-auto">
        <div class="p-6">
          <h3 class="text-lg font-bold mb-4">{{ locationStore?.name }} - 지점 관리</h3>

          <div class="mb-4">
            <button @click="showLocationForm=!showLocationForm" class="bg-green-500 text-white px-3 py-1.5 rounded text-sm hover:bg-green-600">
              {{ showLocationForm ? '폼 닫기' : '+ 지점 추가' }}
            </button>
          </div>

          <!-- Location Add/Edit Form -->
          <div v-if="showLocationForm" class="bg-gray-50 rounded p-4 mb-4 space-y-3">
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block text-xs font-medium text-gray-600 mb-1">지점명</label>
                <input v-model="locationForm.branch_name" class="w-full border rounded px-3 py-2 text-sm" />
              </div>
              <div>
                <label class="block text-xs font-medium text-gray-600 mb-1">전화</label>
                <input v-model="locationForm.phone" class="w-full border rounded px-3 py-2 text-sm" />
              </div>
            </div>
            <div>
              <label class="block text-xs font-medium text-gray-600 mb-1">주소</label>
              <input v-model="locationForm.address" class="w-full border rounded px-3 py-2 text-sm" />
            </div>
            <div class="grid grid-cols-3 gap-3">
              <div>
                <label class="block text-xs font-medium text-gray-600 mb-1">도시</label>
                <input v-model="locationForm.city" class="w-full border rounded px-3 py-2 text-sm" />
              </div>
              <div>
                <label class="block text-xs font-medium text-gray-600 mb-1">주</label>
                <input v-model="locationForm.state" class="w-full border rounded px-3 py-2 text-sm" maxlength="2" />
              </div>
              <div>
                <label class="block text-xs font-medium text-gray-600 mb-1">우편번호</label>
                <input v-model="locationForm.zip_code" class="w-full border rounded px-3 py-2 text-sm" />
              </div>
            </div>
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block text-xs font-medium text-gray-600 mb-1">영업시작</label>
                <input v-model="locationForm.open_time" type="time" class="w-full border rounded px-3 py-2 text-sm" />
              </div>
              <div>
                <label class="block text-xs font-medium text-gray-600 mb-1">영업종료</label>
                <input v-model="locationForm.close_time" type="time" class="w-full border rounded px-3 py-2 text-sm" />
              </div>
            </div>
            <div class="flex items-center gap-4">
              <label class="flex items-center gap-1 text-sm"><input type="checkbox" v-model="locationForm.is_24h" /> 24시간</label>
              <label class="flex items-center gap-1 text-sm"><input type="checkbox" v-model="locationForm.is_active" /> 활성</label>
            </div>
            <div class="flex justify-end gap-2">
              <button @click="showLocationForm=false" class="px-3 py-1.5 border rounded text-sm">취소</button>
              <button @click="saveLocation" class="px-3 py-1.5 bg-blue-500 text-white rounded text-sm hover:bg-blue-600">저장</button>
            </div>
          </div>

          <!-- Location List -->
          <table class="w-full text-sm">
            <thead class="bg-gray-50">
              <tr>
                <th class="p-2 text-left">지점명</th>
                <th class="p-2 text-left">주소</th>
                <th class="p-2 text-left">전화</th>
                <th class="p-2 text-center">영업시간</th>
                <th class="p-2 text-center">상태</th>
                <th class="p-2 text-center">관리</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="loc in locations" :key="loc.id" class="border-t">
                <td class="p-2">{{ loc.branch_name || '-' }}</td>
                <td class="p-2 text-xs">{{ loc.address }}, {{ loc.city }} {{ loc.state }} {{ loc.zip_code }}</td>
                <td class="p-2 text-xs">{{ loc.phone || '-' }}</td>
                <td class="p-2 text-center text-xs">{{ loc.is_24h ? '24시간' : `${loc.open_time || '-'} ~ ${loc.close_time || '-'}` }}</td>
                <td class="p-2 text-center"><span :class="loc.is_active ? 'text-green-500' : 'text-red-400'" class="text-xs">{{ loc.is_active ? '활성' : '비활성' }}</span></td>
                <td class="p-2 text-center space-x-1">
                  <button @click="editLocation(loc)" class="text-blue-500 text-xs hover:underline">수정</button>
                  <button @click="deleteLocation(loc.id)" class="text-red-500 text-xs hover:underline">삭제</button>
                </td>
              </tr>
              <tr v-if="!locations.length"><td colspan="6" class="p-6 text-center text-gray-400">등록된 지점이 없습니다</td></tr>
            </tbody>
          </table>

          <div class="flex justify-end mt-4">
            <button @click="showLocationModal=false" class="px-4 py-2 border rounded text-sm hover:bg-gray-50">닫기</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Deal Modal -->
    <div v-if="showDealModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50" @click.self="showDealModal=false">
      <div class="bg-white rounded-lg shadow-xl w-full max-w-lg mx-4 max-h-[90vh] overflow-y-auto">
        <div class="p-6">
          <h3 class="text-lg font-bold mb-4">{{ dealForm.id ? '딜 수정' : '딜 수동등록' }}</h3>
          <div class="space-y-3">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">마트</label>
              <select v-model="dealForm.store_id" class="w-full border rounded px-3 py-2 text-sm">
                <option value="">선택</option>
                <option v-for="s in stores" :key="s.id" :value="s.id">{{ s.name }}</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">타이틀</label>
              <input v-model="dealForm.title" class="w-full border rounded px-3 py-2 text-sm" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">설명</label>
              <textarea v-model="dealForm.description" rows="2" class="w-full border rounded px-3 py-2 text-sm"></textarea>
            </div>
            <div class="grid grid-cols-3 gap-3">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">원가</label>
                <input v-model="dealForm.original_price" type="number" step="0.01" class="w-full border rounded px-3 py-2 text-sm" />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">세일가</label>
                <input v-model="dealForm.sale_price" type="number" step="0.01" class="w-full border rounded px-3 py-2 text-sm" />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">할인율(%)</label>
                <input v-model="dealForm.discount_percent" type="number" class="w-full border rounded px-3 py-2 text-sm" />
              </div>
            </div>
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">카테고리</label>
                <input v-model="dealForm.category" class="w-full border rounded px-3 py-2 text-sm" />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">단위</label>
                <input v-model="dealForm.unit" class="w-full border rounded px-3 py-2 text-sm" placeholder="예: lb, ea, pack" />
              </div>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">이미지 URL</label>
              <input v-model="dealForm.image_url" class="w-full border rounded px-3 py-2 text-sm" />
            </div>
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">유효 시작</label>
                <input v-model="dealForm.valid_from" type="date" class="w-full border rounded px-3 py-2 text-sm" />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">유효 종료</label>
                <input v-model="dealForm.valid_until" type="date" class="w-full border rounded px-3 py-2 text-sm" />
              </div>
            </div>
            <div class="flex items-center gap-4">
              <label class="flex items-center gap-1 text-sm"><input type="checkbox" v-model="dealForm.is_active" /> 활성</label>
              <label class="flex items-center gap-1 text-sm"><input type="checkbox" v-model="dealForm.is_featured" /> 추천</label>
              <label class="flex items-center gap-1 text-sm"><input type="checkbox" v-model="dealForm.is_special" /> 특가</label>
            </div>
          </div>
          <div class="flex justify-end gap-2 mt-6">
            <button @click="showDealModal=false" class="px-4 py-2 border rounded text-sm hover:bg-gray-50">취소</button>
            <button @click="saveDeal" class="px-4 py-2 bg-blue-500 text-white rounded text-sm hover:bg-blue-600">저장</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Flyer Modal -->
    <div v-if="showFlyerModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50" @click.self="showFlyerModal=false">
      <div class="bg-white rounded-lg shadow-xl w-full max-w-md mx-4">
        <div class="p-6">
          <h3 class="text-lg font-bold mb-4">전단지 등록</h3>
          <div class="space-y-3">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">마트</label>
              <select v-model="flyerForm.store_id" class="w-full border rounded px-3 py-2 text-sm">
                <option value="">선택</option>
                <option v-for="s in stores" :key="s.id" :value="s.id">{{ s.name }}</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">제목</label>
              <input v-model="flyerForm.title" class="w-full border rounded px-3 py-2 text-sm" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">이미지 URL</label>
              <input v-model="flyerForm.image_url" class="w-full border rounded px-3 py-2 text-sm" />
            </div>
            <div v-if="flyerForm.image_url" class="border rounded p-2">
              <img :src="flyerForm.image_url" class="max-h-40 mx-auto" @error="$event.target.style.display='none'" />
            </div>
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">세일 시작</label>
                <input v-model="flyerForm.valid_from" type="date" class="w-full border rounded px-3 py-2 text-sm" />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">세일 종료</label>
                <input v-model="flyerForm.valid_until" type="date" class="w-full border rounded px-3 py-2 text-sm" />
              </div>
            </div>
          </div>
          <div class="flex justify-end gap-2 mt-6">
            <button @click="showFlyerModal=false" class="px-4 py-2 border rounded text-sm hover:bg-gray-50">취소</button>
            <button @click="saveFlyer" class="px-4 py-2 bg-blue-500 text-white rounded text-sm hover:bg-blue-600">등록</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';

const tabs = ['마트 관리', '딜/세일 관리', '전단지 관리', '스크래핑 현황'];
const activeTab = ref(0);

// Data
const stores = ref([]);
const deals = ref([]);
const dealsPagination = ref({});
const dealCategories = ref([]);
const flyers = ref([]);
const scrapeLogs = ref([]);
const locations = ref([]);

// Filters
const dealFilter = ref({ store_id: '', category: '', has_error: false });

// Modals
const showStoreModal = ref(false);
const showLocationModal = ref(false);
const showLocationForm = ref(false);
const showDealModal = ref(false);
const showFlyerModal = ref(false);

const locationStore = ref(null);

// Forms
const defaultStore = { name: '', name_en: '', chain_name: '', category: '', website: '', logo_url: '', weekly_ad_url: '', rss_url: '', scrape_method: '', memo: '', is_active: true };
const storeForm = ref({ ...defaultStore });

const defaultLocation = { branch_name: '', address: '', city: '', state: '', zip_code: '', phone: '', open_time: '09:00', close_time: '21:00', is_24h: false, is_active: true };
const locationForm = ref({ ...defaultLocation });

const defaultDeal = { store_id: '', title: '', description: '', original_price: '', sale_price: '', discount_percent: '', category: '', unit: '', image_url: '', valid_from: '', valid_until: '', is_active: true, is_featured: false, is_special: false };
const dealForm = ref({ ...defaultDeal });

const flyerForm = ref({ store_id: '', title: '', image_url: '', valid_from: '', valid_until: '' });

// API helpers
const api = axios.create({ baseURL: '/api/admin/shopping' });
api.interceptors.request.use(c => {
  const t = localStorage.getItem('sk_token');
  if (t) c.headers.Authorization = `Bearer ${t}`;
  return c;
});

// Load data
async function loadStores() {
  try {
    const { data } = await api.get('/stores');
    stores.value = data;
  } catch (e) { console.error('loadStores', e); }
}

async function loadDeals(page = 1) {
  try {
    const params = { page };
    if (dealFilter.value.store_id) params.store_id = dealFilter.value.store_id;
    if (dealFilter.value.category) params.category = dealFilter.value.category;
    if (dealFilter.value.has_error) params.has_error = 1;
    const { data } = await api.get('/deals', { params });
    deals.value = data.data;
    dealsPagination.value = { current_page: data.current_page, last_page: data.last_page };
  } catch (e) { console.error('loadDeals', e); }
}

async function loadDealCategories() {
  try {
    const { data } = await axios.get('/api/shopping/categories');
    dealCategories.value = data;
  } catch (e) { console.error(e); }
}

async function loadFlyers() {
  try {
    const { data } = await api.get('/flyers');
    flyers.value = data.data || data;
  } catch (e) { console.error('loadFlyers', e); }
}

async function loadScrapeLogs() {
  try {
    const { data } = await api.get('/scrape-logs');
    scrapeLogs.value = data;
  } catch (e) { console.error('loadScrapeLogs', e); }
}

async function loadLocations(storeId) {
  try {
    const { data } = await api.get(`/stores/${storeId}/locations`);
    locations.value = data;
  } catch (e) { console.error('loadLocations', e); }
}

// Store CRUD
function openStoreModal(s = null) {
  storeForm.value = s ? { ...s } : { ...defaultStore };
  showStoreModal.value = true;
}

async function saveStore() {
  try {
    if (storeForm.value.id) {
      await api.put(`/stores/${storeForm.value.id}`, storeForm.value);
    } else {
      await api.post('/stores', storeForm.value);
    }
    showStoreModal.value = false;
    loadStores();
  } catch (e) { alert('저장 실패: ' + (e.response?.data?.message || e.message)); }
}

async function deleteStore(id) {
  if (!confirm('이 마트를 삭제하시겠습니까?')) return;
  try {
    await api.delete(`/stores/${id}`);
    loadStores();
  } catch (e) { alert('삭제 실패'); }
}

// Location CRUD
function openLocationModal(s) {
  locationStore.value = s;
  showLocationForm.value = false;
  locationForm.value = { ...defaultLocation };
  showLocationModal.value = true;
  loadLocations(s.id);
}

function editLocation(loc) {
  locationForm.value = { ...loc };
  showLocationForm.value = true;
}

async function saveLocation() {
  try {
    if (locationForm.value.id) {
      await api.put(`/locations/${locationForm.value.id}`, locationForm.value);
    } else {
      await api.post(`/stores/${locationStore.value.id}/locations`, locationForm.value);
    }
    showLocationForm.value = false;
    locationForm.value = { ...defaultLocation };
    loadLocations(locationStore.value.id);
    loadStores();
  } catch (e) { alert('저장 실패: ' + (e.response?.data?.message || e.message)); }
}

async function deleteLocation(id) {
  if (!confirm('이 지점을 삭제하시겠습니까?')) return;
  try {
    await api.delete(`/locations/${id}`);
    loadLocations(locationStore.value.id);
    loadStores();
  } catch (e) { alert('삭제 실패'); }
}

// Deal CRUD
function openDealModal(d = null) {
  dealForm.value = d ? { ...d } : { ...defaultDeal };
  showDealModal.value = true;
}

async function saveDeal() {
  try {
    if (dealForm.value.id) {
      await api.put(`/deals/${dealForm.value.id}`, dealForm.value);
    } else {
      await api.post('/deals', dealForm.value);
    }
    showDealModal.value = false;
    loadDeals();
  } catch (e) { alert('저장 실패: ' + (e.response?.data?.message || e.message)); }
}

async function deleteDeal(id) {
  if (!confirm('이 딜을 삭제하시겠습니까?')) return;
  try {
    await api.delete(`/deals/${id}`);
    loadDeals();
  } catch (e) { alert('삭제 실패'); }
}

async function bulkDeleteErrors() {
  if (!confirm('가격 오류 항목을 모두 삭제하시겠습니까?')) return;
  try {
    const { data } = await api.delete('/deals-bulk-errors');
    alert(`${data.count}개 오류 항목 삭제됨`);
    loadDeals();
  } catch (e) { alert('삭제 실패'); }
}

// Flyer CRUD
function openFlyerModal() {
  flyerForm.value = { store_id: '', title: '', image_url: '', valid_from: '', valid_until: '' };
  showFlyerModal.value = true;
}

async function saveFlyer() {
  try {
    await api.post('/flyers', { ...flyerForm.value, is_active: true });
    showFlyerModal.value = false;
    loadFlyers();
  } catch (e) { alert('등록 실패: ' + (e.response?.data?.message || e.message)); }
}

async function deleteFlyer(id) {
  if (!confirm('이 전단지를 삭제하시겠습니까?')) return;
  try {
    await api.delete(`/flyers/${id}`);
    loadFlyers();
  } catch (e) { alert('삭제 실패'); }
}

onMounted(() => {
  loadStores();
  loadDeals();
  loadDealCategories();
  loadFlyers();
  loadScrapeLogs();
});
</script>
