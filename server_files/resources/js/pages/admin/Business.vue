<template>
  <div class="space-y-5">

    <!-- 통계 카드 -->
    <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
        <div class="text-xs text-gray-400 mb-1">전체 업소</div>
        <div class="text-2xl font-bold text-gray-800">{{ stats.total }}</div>
      </div>
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
        <div class="text-xs text-gray-400 mb-1">활성</div>
        <div class="text-2xl font-bold text-green-600">{{ stats.active }}</div>
      </div>
      <div class="bg-white rounded-xl shadow-sm border border-yellow-200 p-4 bg-yellow-50">
        <div class="text-xs text-yellow-600 mb-1">승인대기</div>
        <div class="text-2xl font-bold text-yellow-600">{{ stats.pending }}</div>
      </div>
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
        <div class="text-xs text-gray-400 mb-1">비활성</div>
        <div class="text-2xl font-bold text-gray-500">{{ stats.inactive }}</div>
      </div>
      <div class="bg-white rounded-xl shadow-sm border border-blue-200 p-4 bg-blue-50">
        <div class="text-xs text-blue-500 mb-1">이번달 신규</div>
        <div class="text-2xl font-bold text-blue-600">{{ stats.newThisMonth }}</div>
      </div>
    </div>

    <!-- 필터 & 검색 -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
      <div class="flex flex-col sm:flex-row gap-3">
        <input v-model="search" @keyup.enter="loadFirst" type="text" placeholder="업소명, 주소, 전화번호 검색..."
          class="flex-1 border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-400" />
        <select v-model="filterCategory" @change="loadFirst"
          class="border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-400">
          <option value="">전체 카테고리</option>
          <option v-for="cat in categories" :key="cat" :value="cat">{{ cat }}</option>
        </select>
        <select v-model="filterStatus" @change="loadFirst"
          class="border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-400">
          <option value="">전체 상태</option>
          <option value="active">활성</option>
          <option value="pending">승인대기</option>
          <option value="inactive">비활성</option>
        </select>
        <select v-model="sortBy" @change="loadFirst"
          class="border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-400">
          <option value="latest">최신등록순</option>
          <option value="name">이름순</option>
          <option value="reviews">리뷰많은순</option>
        </select>
        <button @click="loadFirst"
          class="bg-blue-500 hover:bg-blue-600 text-white px-5 py-2 rounded-lg text-sm font-semibold transition">
          검색
        </button>
      </div>
    </div>

    <!-- 업소 테이블 -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <div v-if="loading" class="text-center py-10 text-gray-400 text-sm">불러오는 중...</div>
      <div v-else-if="filtered.length === 0" class="text-center py-10 text-gray-400 text-sm">업소가 없습니다.</div>
      <div v-else class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="bg-gray-50 border-b border-gray-100">
            <tr>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">업소명 / 주소</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500 hidden sm:table-cell">카테고리</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500 hidden md:table-cell">대표자</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500 hidden lg:table-cell">전화번호</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500 hidden lg:table-cell">리뷰/평점</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">상태</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500 hidden md:table-cell">등록일</th>
              <th class="text-right px-4 py-3 text-xs font-semibold text-gray-500">관리</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-50">
            <tr v-for="b in paginated" :key="b.id"
              :class="['hover:bg-gray-50 transition', b.status === 'pending' ? 'bg-yellow-50/40' : '']">
              <td class="px-4 py-3">
                <div class="text-sm font-medium text-gray-800">{{ b.name }}</div>
                <div class="text-xs text-gray-400 truncate max-w-[220px]">{{ b.address }}</div>
              </td>
              <td class="px-4 py-3 hidden sm:table-cell">
                <span class="text-xs px-2 py-0.5 rounded-full font-medium"
                  :class="categoryBadgeClass(b.category)">{{ b.category }}</span>
              </td>
              <td class="px-4 py-3 text-xs text-gray-600 hidden md:table-cell">{{ b.owner_name }}</td>
              <td class="px-4 py-3 text-xs text-gray-600 hidden lg:table-cell">{{ b.phone }}</td>
              <td class="px-4 py-3 hidden lg:table-cell">
                <div class="flex items-center gap-1">
                  <span class="text-yellow-500 text-xs">&#9733;</span>
                  <span class="text-xs text-gray-700 font-medium">{{ b.rating > 0 ? b.rating.toFixed(1) : '-' }}</span>
                  <span class="text-xs text-gray-400">({{ b.reviews_count }})</span>
                </div>
              </td>
              <td class="px-4 py-3">
                <span :class="['text-xs px-2 py-0.5 rounded-full font-semibold',
                  b.status === 'active' ? 'bg-green-100 text-green-600' :
                  b.status === 'pending' ? 'bg-yellow-100 text-yellow-600' :
                  'bg-gray-100 text-gray-500']">
                  {{ statusLabel(b.status) }}
                </span>
              </td>
              <td class="px-4 py-3 text-xs text-gray-500 hidden md:table-cell">{{ b.created_at }}</td>
              <td class="px-4 py-3">
                <div class="flex items-center justify-end gap-1 flex-wrap">
                  <button v-if="b.status === 'pending'" @click="approveBusiness(b)"
                    class="text-xs bg-green-50 hover:bg-green-100 text-green-600 px-2 py-1 rounded-lg transition font-semibold">
                    승인
                  </button>
                  <button v-if="b.status === 'pending'" @click="openRejectModal(b)"
                    class="text-xs bg-orange-50 hover:bg-orange-100 text-orange-600 px-2 py-1 rounded-lg transition font-semibold">
                    반려
                  </button>
                  <button @click="openDetail(b)"
                    class="text-xs bg-blue-50 hover:bg-blue-100 text-blue-600 px-2 py-1 rounded-lg transition">
                    상세
                  </button>
                  <button @click="openEdit(b)"
                    class="text-xs bg-indigo-50 hover:bg-indigo-100 text-indigo-600 px-2 py-1 rounded-lg transition">
                    수정
                  </button>
                  <button @click="toggleStatus(b)"
                    :class="['text-xs px-2 py-1 rounded-lg transition',
                      b.status === 'active' ? 'bg-gray-100 hover:bg-gray-200 text-gray-600' : 'bg-green-50 hover:bg-green-100 text-green-600']">
                    {{ b.status === 'active' ? '비활성' : '활성' }}
                  </button>
                  <button @click="deleteBusiness(b)"
                    class="text-xs bg-red-50 hover:bg-red-100 text-red-500 px-2 py-1 rounded-lg transition">
                    삭제
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 페이지네이션 -->
      <div v-if="totalPages > 1" class="flex items-center justify-center gap-2 px-4 py-3 border-t border-gray-100">
        <button @click="page = page - 1" :disabled="page <= 1"
          class="px-3 py-1.5 text-xs rounded-lg border border-gray-200 disabled:opacity-40 hover:bg-gray-50 transition">
          &lsaquo; 이전
        </button>
        <template v-for="p in pageNumbers" :key="p">
          <button v-if="p !== '...'" @click="page = p"
            :class="['px-3 py-1.5 text-xs rounded-lg border transition',
              p === page ? 'border-blue-400 bg-blue-50 text-blue-600 font-semibold' : 'border-gray-200 hover:bg-gray-50']">
            {{ p }}
          </button>
          <span v-else class="text-xs text-gray-400 px-1">...</span>
        </template>
        <button @click="page = page + 1" :disabled="page >= totalPages"
          class="px-3 py-1.5 text-xs rounded-lg border border-gray-200 disabled:opacity-40 hover:bg-gray-50 transition">
          다음 &rsaquo;
        </button>
      </div>
    </div>

    <!-- 상세/수정 모달 -->
    <div v-if="modal.open" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40" @click.self="closeModal">
      <div class="bg-white rounded-2xl shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto m-4">
        <!-- 모달 헤더 -->
        <div class="flex items-center justify-between px-6 py-4 border-b border-gray-100">
          <h3 class="text-lg font-bold text-gray-800">
            {{ modal.mode === 'edit' ? '업소 수정' : '업소 상세' }}
          </h3>
          <div class="flex items-center gap-2">
            <button v-if="modal.mode === 'view'" @click="modal.mode = 'edit'"
              class="text-xs bg-indigo-50 hover:bg-indigo-100 text-indigo-600 px-3 py-1.5 rounded-lg transition font-semibold">
              수정모드
            </button>
            <button v-if="modal.mode === 'edit'" @click="modal.mode = 'view'"
              class="text-xs bg-gray-100 hover:bg-gray-200 text-gray-600 px-3 py-1.5 rounded-lg transition font-semibold">
              보기모드
            </button>
            <button @click="closeModal" class="text-gray-400 hover:text-gray-600 text-xl leading-none">&times;</button>
          </div>
        </div>

        <!-- 모달 본문: 보기 모드 -->
        <div v-if="modal.mode === 'view'" class="px-6 py-5 space-y-5">
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <div class="text-xs text-gray-400 mb-0.5">업소명</div>
              <div class="text-sm font-semibold text-gray-800">{{ modal.data.name }}</div>
            </div>
            <div>
              <div class="text-xs text-gray-400 mb-0.5">영문명</div>
              <div class="text-sm text-gray-700">{{ modal.data.english_name || '-' }}</div>
            </div>
            <div>
              <div class="text-xs text-gray-400 mb-0.5">카테고리</div>
              <span class="text-xs px-2 py-0.5 rounded-full font-medium"
                :class="categoryBadgeClass(modal.data.category)">{{ modal.data.category }}</span>
            </div>
            <div>
              <div class="text-xs text-gray-400 mb-0.5">대표자명</div>
              <div class="text-sm text-gray-700">{{ modal.data.owner_name || '-' }}</div>
            </div>
            <div>
              <div class="text-xs text-gray-400 mb-0.5">사업자등록번호</div>
              <div class="text-sm text-gray-700">{{ modal.data.business_number || '-' }}</div>
            </div>
            <div>
              <div class="text-xs text-gray-400 mb-0.5">상태</div>
              <span :class="['text-xs px-2 py-0.5 rounded-full font-semibold',
                modal.data.status === 'active' ? 'bg-green-100 text-green-600' :
                modal.data.status === 'pending' ? 'bg-yellow-100 text-yellow-600' :
                'bg-gray-100 text-gray-500']">
                {{ statusLabel(modal.data.status) }}
              </span>
            </div>
          </div>

          <div>
            <div class="text-xs text-gray-400 mb-0.5">주소</div>
            <div class="text-sm text-gray-700">{{ modal.data.address }}</div>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div>
              <div class="text-xs text-gray-400 mb-0.5">전화번호</div>
              <div class="text-sm text-gray-700">{{ modal.data.phone || '-' }}</div>
            </div>
            <div>
              <div class="text-xs text-gray-400 mb-0.5">이메일</div>
              <div class="text-sm text-gray-700">{{ modal.data.email || '-' }}</div>
            </div>
            <div>
              <div class="text-xs text-gray-400 mb-0.5">웹사이트</div>
              <div class="text-sm text-blue-600 truncate">
                <a v-if="modal.data.website" :href="modal.data.website" target="_blank">{{ modal.data.website }}</a>
                <span v-else class="text-gray-400">-</span>
              </div>
            </div>
          </div>

          <div>
            <div class="text-xs text-gray-400 mb-0.5">영업시간</div>
            <div class="text-sm text-gray-700">{{ modal.data.hours || '-' }}</div>
          </div>

          <div>
            <div class="text-xs text-gray-400 mb-0.5">소개글 / 설명</div>
            <div class="text-sm text-gray-700 bg-gray-50 rounded-lg p-3">{{ modal.data.description || '-' }}</div>
          </div>

          <!-- 사진 갤러리 -->
          <div v-if="modal.data.images && modal.data.images.length">
            <div class="text-xs text-gray-400 mb-1">사진 갤러리</div>
            <div class="flex gap-2 overflow-x-auto pb-1">
              <img v-for="(img, i) in modal.data.images" :key="i" :src="img"
                class="w-24 h-24 object-cover rounded-lg border border-gray-200" />
            </div>
          </div>

          <!-- 등록자 정보 -->
          <div class="bg-gray-50 rounded-lg p-3">
            <div class="text-xs text-gray-400 mb-1">등록자 정보</div>
            <div class="text-sm text-gray-700">{{ modal.data.user?.name || '-' }} ({{ modal.data.user?.email || '-' }})</div>
            <div class="text-xs text-gray-400 mt-1">등록일: {{ modal.data.created_at }}</div>
          </div>

          <!-- 리뷰/평점 -->
          <div>
            <div class="text-xs text-gray-400 mb-1">리뷰 ({{ modal.data.reviews_count }}건, 평균 {{ modal.data.rating > 0 ? modal.data.rating.toFixed(1) : '-' }})</div>
            <div v-if="modal.data.reviews && modal.data.reviews.length" class="space-y-2">
              <div v-for="r in modal.data.reviews" :key="r.id" class="bg-gray-50 rounded-lg p-3">
                <div class="flex items-center gap-2 mb-1">
                  <span class="text-yellow-500 text-xs">&#9733;</span>
                  <span class="text-xs font-semibold text-gray-700">{{ r.rating }}</span>
                  <span class="text-xs text-gray-400">{{ r.user }}</span>
                  <span class="text-xs text-gray-300 ml-auto">{{ r.date }}</span>
                </div>
                <div class="text-xs text-gray-600">{{ r.content }}</div>
              </div>
            </div>
            <div v-else class="text-xs text-gray-400">리뷰가 없습니다.</div>
          </div>
        </div>

        <!-- 모달 본문: 수정 모드 -->
        <div v-if="modal.mode === 'edit'" class="px-6 py-5 space-y-4">
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label class="block text-xs text-gray-500 mb-1">업소명 *</label>
              <input v-model="modal.data.name" type="text"
                class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-400" />
            </div>
            <div>
              <label class="block text-xs text-gray-500 mb-1">영문명</label>
              <input v-model="modal.data.english_name" type="text"
                class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-400" />
            </div>
            <div>
              <label class="block text-xs text-gray-500 mb-1">카테고리</label>
              <select v-model="modal.data.category"
                class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-400">
                <option v-for="cat in categories" :key="cat" :value="cat">{{ cat }}</option>
              </select>
            </div>
            <div>
              <label class="block text-xs text-gray-500 mb-1">대표자명</label>
              <input v-model="modal.data.owner_name" type="text"
                class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-400" />
            </div>
            <div>
              <label class="block text-xs text-gray-500 mb-1">사업자등록번호</label>
              <input v-model="modal.data.business_number" type="text"
                class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-400" />
            </div>
            <div>
              <label class="block text-xs text-gray-500 mb-1">상태</label>
              <select v-model="modal.data.status"
                class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-400">
                <option value="active">활성</option>
                <option value="pending">승인대기</option>
                <option value="inactive">비활성</option>
              </select>
            </div>
          </div>

          <div>
            <label class="block text-xs text-gray-500 mb-1">주소 *</label>
            <input v-model="modal.data.address" type="text"
              class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-400" />
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div>
              <label class="block text-xs text-gray-500 mb-1">전화번호</label>
              <input v-model="modal.data.phone" type="text"
                class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-400" />
            </div>
            <div>
              <label class="block text-xs text-gray-500 mb-1">이메일</label>
              <input v-model="modal.data.email" type="text"
                class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-400" />
            </div>
            <div>
              <label class="block text-xs text-gray-500 mb-1">웹사이트</label>
              <input v-model="modal.data.website" type="text"
                class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-400" />
            </div>
          </div>

          <div>
            <label class="block text-xs text-gray-500 mb-1">영업시간</label>
            <input v-model="modal.data.hours" type="text" placeholder="예: 09:00-22:00"
              class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-400" />
          </div>

          <div>
            <label class="block text-xs text-gray-500 mb-1">소개글 / 설명</label>
            <textarea v-model="modal.data.description" rows="3"
              class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-400 resize-none"></textarea>
          </div>

          <div class="flex justify-end gap-2 pt-2">
            <button @click="closeModal"
              class="px-4 py-2 text-sm text-gray-600 bg-gray-100 hover:bg-gray-200 rounded-lg transition">
              취소
            </button>
            <button @click="saveBusiness" :disabled="saving"
              class="px-4 py-2 text-sm text-white bg-blue-500 hover:bg-blue-600 rounded-lg transition font-semibold disabled:opacity-50">
              {{ saving ? '저장 중...' : '저장' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 반려 모달 -->
    <div v-if="rejectModal.open" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40" @click.self="rejectModal.open = false">
      <div class="bg-white rounded-2xl shadow-xl w-full max-w-md m-4">
        <div class="px-6 py-4 border-b border-gray-100">
          <h3 class="text-lg font-bold text-gray-800">업소 등록 반려</h3>
        </div>
        <div class="px-6 py-5 space-y-3">
          <div class="text-sm text-gray-700">
            <span class="font-semibold">{{ rejectModal.business?.name }}</span> 업소의 등록을 반려합니다.
          </div>
          <div>
            <label class="block text-xs text-gray-500 mb-1">반려 사유 *</label>
            <textarea v-model="rejectModal.reason" rows="3" placeholder="반려 사유를 입력해주세요..."
              class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-red-400 resize-none"></textarea>
          </div>
        </div>
        <div class="px-6 py-4 border-t border-gray-100 flex justify-end gap-2">
          <button @click="rejectModal.open = false"
            class="px-4 py-2 text-sm text-gray-600 bg-gray-100 hover:bg-gray-200 rounded-lg transition">
            취소
          </button>
          <button @click="rejectBusiness" :disabled="!rejectModal.reason.trim()"
            class="px-4 py-2 text-sm text-white bg-red-500 hover:bg-red-600 rounded-lg transition font-semibold disabled:opacity-50">
            반려
          </button>
        </div>
      </div>
    </div>

    <!-- 승인 확인 모달 -->
    <div v-if="approveModal.open" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40" @click.self="approveModal.open = false">
      <div class="bg-white rounded-2xl shadow-xl w-full max-w-md m-4">
        <div class="px-6 py-4 border-b border-gray-100">
          <h3 class="text-lg font-bold text-gray-800">업소 승인 확인</h3>
        </div>
        <div class="px-6 py-5 space-y-3">
          <div class="text-sm text-gray-700">
            <span class="font-semibold">{{ approveModal.business?.name }}</span> 업소를 승인하시겠습니까?
          </div>
          <div>
            <label class="block text-xs text-gray-500 mb-1">메모 (선택)</label>
            <input v-model="approveModal.memo" type="text" placeholder="승인 메모..."
              class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-green-400" />
          </div>
        </div>
        <div class="px-6 py-4 border-t border-gray-100 flex justify-end gap-2">
          <button @click="approveModal.open = false"
            class="px-4 py-2 text-sm text-gray-600 bg-gray-100 hover:bg-gray-200 rounded-lg transition">
            취소
          </button>
          <button @click="confirmApprove"
            class="px-4 py-2 text-sm text-white bg-green-500 hover:bg-green-600 rounded-lg transition font-semibold">
            승인
          </button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import axios from 'axios'

// --- 카테고리 목록 ---
const categories = ['음식점', '뷰티', '자동차', '부동산', '법률', '의료', '교육', '쇼핑', '서비스', '기타']

// --- 더미 데이터 ---
const dummyBusinesses = [
  { id: 1, name: 'LA 한인마트', english_name: 'LA Korean Mart', category: '쇼핑', owner_name: '김영수', phone: '213-380-0100', email: 'lamart@example.com', website: 'https://lakoreanmart.com', address: '3500 W 6th St, Los Angeles, CA 90020', rating: 4.5, reviews_count: 28, status: 'active', description: 'LA 코리아타운 중심의 대형 한인 마트', hours: '09:00-22:00', business_number: '123-45-67890', images: [], reviews: [{ id: 1, user: '이수정', rating: 5, content: '품목이 다양하고 가격도 합리적입니다!', date: '2026-03-10' }, { id: 2, user: '박민수', rating: 4, content: '주차가 좀 불편하지만 물건은 좋아요.', date: '2026-02-28' }], user: { name: '김영수', email: 'youngsu@gmail.com' }, created_at: '2025-05-15' },
  { id: 2, name: '새롬 부동산', english_name: 'Saerom Realty', category: '부동산', owner_name: '이재현', phone: '213-555-0200', email: 'saerom@example.com', address: '3435 Wilshire Blvd, Los Angeles, CA 90010', rating: 4.2, reviews_count: 15, status: 'active', description: 'LA/OC 지역 전문 부동산', hours: '09:00-18:00', business_number: '234-56-78901', images: [], reviews: [{ id: 3, user: '김진호', rating: 4, content: '친절하고 전문적입니다.', date: '2026-01-15' }], user: { name: '이재현', email: 'jaehyun@gmail.com' }, created_at: '2025-08-20' },
  { id: 3, name: '미소 헤어살롱', english_name: 'Miso Hair Salon', category: '뷰티', owner_name: '박미소', phone: '213-555-0300', email: 'miso@example.com', address: '621 S Western Ave, Los Angeles, CA 90005', rating: 4.8, reviews_count: 42, status: 'active', description: '한국식 헤어 전문 살롱', hours: '10:00-20:00', business_number: '345-67-89012', images: [], reviews: [{ id: 4, user: '최은지', rating: 5, content: '항상 만족하는 결과를 받아요!', date: '2026-03-20' }, { id: 5, user: '정수현', rating: 5, content: '분위기도 좋고 실력도 최고', date: '2026-03-05' }], user: { name: '박미소', email: 'miso@gmail.com' }, created_at: '2025-06-10' },
  { id: 4, name: '새마을 식당', english_name: 'Saemaeul Restaurant', category: '음식점', owner_name: '정대한', phone: '213-555-0400', email: 'saemaeul@example.com', address: '856 S Vermont Ave, Los Angeles, CA 90005', rating: 0, reviews_count: 0, status: 'pending', description: '정통 한식 전문점 - 열탄불고기, 7분돼지김치찌개', hours: '11:00-22:00', business_number: '', images: [], reviews: [], user: { name: '정대한', email: 'daehan@gmail.com' }, created_at: '2026-03-25' },
  { id: 5, name: '한미 법률사무소', english_name: 'Han-Mi Law Office', category: '법률', owner_name: '송재원', phone: '213-555-0500', email: 'hanmi@example.com', address: '3460 Wilshire Blvd #400, LA, CA 90010', rating: 4.6, reviews_count: 19, status: 'active', description: '이민법, 부동산, 비즈니스법 전문', hours: '09:00-18:00', business_number: '567-89-01234', images: [], reviews: [{ id: 6, user: '한민석', rating: 5, content: '이민법 관련 정말 잘 도와주셨습니다.', date: '2026-02-10' }], user: { name: '송재원', email: 'jaewon@gmail.com' }, created_at: '2025-04-01' },
  { id: 6, name: '아리랑 한의원', english_name: 'Arirang Oriental Medicine', category: '의료', owner_name: '김한의', phone: '213-555-0600', email: 'arirang@example.com', address: '3200 W Olympic Blvd, LA, CA 90006', rating: 4.3, reviews_count: 31, status: 'active', description: '침, 한약, 추나요법 전문', hours: '09:00-18:00', business_number: '678-90-12345', images: [], reviews: [{ id: 7, user: '오정원', rating: 4, content: '한약 처방 받고 많이 좋아졌어요.', date: '2026-03-01' }], user: { name: '김한의', email: 'hanui@gmail.com' }, created_at: '2025-07-01' },
  { id: 7, name: '갈비왕', english_name: 'Galbi King', category: '음식점', owner_name: '최갈비', phone: '213-555-0700', email: '', address: '123 N Western Ave, LA, CA 90004', rating: 0, reviews_count: 0, status: 'pending', description: 'LA 최고의 갈비 전문점', hours: '11:30-22:00', business_number: '', images: [], reviews: [], user: { name: '최갈비', email: 'galbi@gmail.com' }, created_at: '2026-03-27' },
  { id: 8, name: '코리아 오토', english_name: 'Korea Auto', category: '자동차', owner_name: '한차수리', phone: '213-555-0800', email: '', address: '456 S Vermont Ave, LA, CA 90020', rating: 3.8, reviews_count: 8, status: 'inactive', description: '한인 전문 자동차 수리/정비', hours: '08:00-18:00', business_number: '890-12-34567', images: [], reviews: [{ id: 8, user: '강태호', rating: 4, content: '수리비가 합리적이에요.', date: '2025-12-15' }], user: { name: '한차', email: 'auto@gmail.com' }, created_at: '2025-03-15' },
]

// --- 상태 ---
const businesses = ref([...dummyBusinesses])
const loading = ref(false)
const saving = ref(false)
const search = ref('')
const filterStatus = ref('')
const filterCategory = ref('')
const sortBy = ref('latest')
const page = ref(1)
const perPage = 10

// --- 모달 상태 ---
const modal = reactive({ open: false, mode: 'view', data: {} })
const rejectModal = reactive({ open: false, business: null, reason: '' })
const approveModal = reactive({ open: false, business: null, memo: '' })

// --- 통계 ---
const stats = computed(() => {
  const all = businesses.value
  const now = new Date()
  const thisMonth = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`
  return {
    total: all.length,
    active: all.filter(b => b.status === 'active').length,
    pending: all.filter(b => b.status === 'pending').length,
    inactive: all.filter(b => b.status === 'inactive').length,
    newThisMonth: all.filter(b => b.created_at && b.created_at.startsWith(thisMonth)).length,
  }
})

// --- 필터링 + 정렬 ---
const filtered = computed(() => {
  let list = businesses.value

  if (search.value.trim()) {
    const q = search.value.trim().toLowerCase()
    list = list.filter(b =>
      (b.name && b.name.toLowerCase().includes(q)) ||
      (b.address && b.address.toLowerCase().includes(q)) ||
      (b.phone && b.phone.includes(q))
    )
  }
  if (filterStatus.value) {
    list = list.filter(b => b.status === filterStatus.value)
  }
  if (filterCategory.value) {
    list = list.filter(b => b.category === filterCategory.value)
  }

  if (sortBy.value === 'name') {
    list = [...list].sort((a, b) => (a.name || '').localeCompare(b.name || '', 'ko'))
  } else if (sortBy.value === 'reviews') {
    list = [...list].sort((a, b) => (b.reviews_count || 0) - (a.reviews_count || 0))
  } else {
    list = [...list].sort((a, b) => (b.created_at || '').localeCompare(a.created_at || ''))
  }

  return list
})

// --- 페이지네이션 ---
const totalPages = computed(() => Math.max(1, Math.ceil(filtered.value.length / perPage)))

const paginated = computed(() => {
  const start = (page.value - 1) * perPage
  return filtered.value.slice(start, start + perPage)
})

const pageNumbers = computed(() => {
  const total = totalPages.value
  const cur = page.value
  if (total <= 7) return Array.from({ length: total }, (_, i) => i + 1)
  const pages = []
  pages.push(1)
  if (cur > 3) pages.push('...')
  for (let i = Math.max(2, cur - 1); i <= Math.min(total - 1, cur + 1); i++) pages.push(i)
  if (cur < total - 2) pages.push('...')
  pages.push(total)
  return pages
})

// --- 유틸 ---
function statusLabel(s) {
  return s === 'active' ? '활성' : s === 'pending' ? '승인대기' : '비활성'
}

function categoryBadgeClass(cat) {
  const map = {
    '음식점': 'bg-orange-100 text-orange-700',
    '뷰티': 'bg-pink-100 text-pink-700',
    '자동차': 'bg-sky-100 text-sky-700',
    '부동산': 'bg-emerald-100 text-emerald-700',
    '법률': 'bg-violet-100 text-violet-700',
    '의료': 'bg-red-100 text-red-700',
    '교육': 'bg-blue-100 text-blue-700',
    '쇼핑': 'bg-amber-100 text-amber-700',
    '서비스': 'bg-teal-100 text-teal-700',
    '기타': 'bg-gray-100 text-gray-600',
  }
  return map[cat] || 'bg-gray-100 text-gray-600'
}

function loadFirst() {
  page.value = 1
}

// --- 데이터 로드 (API 연동 시 사용) ---
async function loadFromApi() {
  loading.value = true
  try {
    const res = await axios.get('/api/admin/businesses', {
      params: { page: page.value, search: search.value, status: filterStatus.value, category: filterCategory.value }
    })
    businesses.value = res.data.data ?? []
  } catch {
    // API 실패 시 더미 데이터 유지
  } finally {
    loading.value = false
  }
}

// --- 모달 열기/닫기 ---
function openDetail(b) {
  modal.data = JSON.parse(JSON.stringify(b))
  modal.mode = 'view'
  modal.open = true
}

function openEdit(b) {
  modal.data = JSON.parse(JSON.stringify(b))
  modal.mode = 'edit'
  modal.open = true
}

function closeModal() {
  modal.open = false
  modal.mode = 'view'
  modal.data = {}
}

// --- 저장 ---
async function saveBusiness() {
  saving.value = true
  try {
    await axios.put(`/api/admin/businesses/${modal.data.id}`, modal.data)
  } catch {
    // API 실패 시 로컬에서만 반영
  }
  const idx = businesses.value.findIndex(b => b.id === modal.data.id)
  if (idx !== -1) businesses.value[idx] = JSON.parse(JSON.stringify(modal.data))
  saving.value = false
  closeModal()
}

// --- 승인 ---
function approveBusiness(b) {
  approveModal.business = b
  approveModal.memo = ''
  approveModal.open = true
}

async function confirmApprove() {
  const b = approveModal.business
  try {
    await axios.post(`/api/admin/businesses/${b.id}/approve`, { memo: approveModal.memo })
  } catch {
    // API 실패 시 로컬에서만 반영
  }
  b.status = 'active'
  approveModal.open = false
}

// --- 반려 ---
function openRejectModal(b) {
  rejectModal.business = b
  rejectModal.reason = ''
  rejectModal.open = true
}

async function rejectBusiness() {
  const b = rejectModal.business
  try {
    await axios.post(`/api/admin/businesses/${b.id}/reject`, { reason: rejectModal.reason })
  } catch {
    // API 실패 시 로컬에서만 반영
  }
  b.status = 'inactive'
  rejectModal.open = false
}

// --- 상태 토글 ---
async function toggleStatus(b) {
  const newStatus = b.status === 'active' ? 'inactive' : 'active'
  try {
    await axios.put(`/api/admin/businesses/${b.id}`, { ...b, status: newStatus })
  } catch {
    // API 실패 시 로컬에서만 반영
  }
  b.status = newStatus
}

// --- 삭제 ---
async function deleteBusiness(b) {
  if (!confirm(`"${b.name}" 업소를 삭제하시겠습니까?`)) return
  try {
    await axios.delete(`/api/admin/businesses/${b.id}`)
  } catch {
    // API 실패 시 로컬에서만 반영
  }
  businesses.value = businesses.value.filter(x => x.id !== b.id)
}

// --- 초기화 ---
onMounted(() => {
  loadFromApi()
})
</script>
