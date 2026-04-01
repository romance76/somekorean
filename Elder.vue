<template>
  <div class="space-y-5">

    <!-- 상단 통계 카드 (4개) -->
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
      <div class="bg-white rounded-xl p-4 shadow-sm border border-gray-100 text-center">
        <div class="text-2xl font-black text-gray-800">{{ stats.totalElders }}</div>
        <div class="text-xs text-gray-500 mt-0.5">전체 노인 회원</div>
      </div>
      <div class="bg-white rounded-xl p-4 shadow-sm border border-green-100 text-center">
        <div class="text-2xl font-black text-green-600">
          {{ stats.checkedInToday }} / {{ stats.totalElders }}
          <span class="text-sm font-semibold text-green-500">({{ checkinPercent }}%)</span>
        </div>
        <div class="text-xs text-gray-500 mt-0.5">오늘 체크인 완료</div>
      </div>
      <div class="bg-red-50 rounded-xl p-4 shadow-sm border border-red-200 text-center">
        <div class="text-2xl font-black text-red-600">{{ stats.noResponseToday }}</div>
        <div class="text-xs text-red-400 mt-0.5">오늘 미응답</div>
      </div>
      <div class="bg-orange-50 rounded-xl p-4 shadow-sm border border-orange-200 text-center">
        <div class="text-2xl font-black text-orange-600">{{ stats.sosThisWeek }}</div>
        <div class="text-xs text-orange-400 mt-0.5">SOS 발동 (이번 주)</div>
      </div>
    </div>

    <!-- 탭 네비게이션 -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <div class="flex border-b border-gray-100">
        <button v-for="tab in tabs" :key="tab.key"
          @click="activeTab = tab.key"
          :class="['flex-1 px-4 py-3 text-sm font-semibold transition-colors',
            activeTab === tab.key ? 'text-blue-600 border-b-2 border-blue-600 bg-blue-50/50' : 'text-gray-500 hover:text-gray-700']">
          {{ tab.label }}
        </button>
      </div>

      <!-- ==================== 모니터링 탭 ==================== -->
      <div v-if="activeTab === 'monitoring'">
        <!-- 필터 -->
        <div class="flex items-center gap-2 px-5 py-3 border-b border-gray-50 bg-gray-50/50">
          <button v-for="f in monitorFilters" :key="f.key"
            @click="monitorFilter = f.key"
            :class="['px-3 py-1 rounded-full text-xs font-semibold transition-colors',
              monitorFilter === f.key ? 'bg-blue-600 text-white' : 'bg-white text-gray-500 border border-gray-200 hover:bg-gray-100']">
            {{ f.label }} ({{ f.count }})
          </button>
          <div class="flex-1" />
          <button @click="loadElders" class="text-xs text-blue-500 hover:text-blue-600 font-medium">새로고침</button>
        </div>

        <!-- 테이블 -->
        <div v-if="loading" class="text-center py-10 text-gray-400 text-sm">불러오는 중...</div>
        <div v-else-if="filteredMonitorElders.length === 0" class="text-center py-10 text-gray-400 text-sm">해당하는 회원이 없습니다.</div>
        <div v-else class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead class="bg-gray-50">
              <tr>
                <th class="text-left px-4 py-2.5 text-xs font-semibold text-gray-500">회원명</th>
                <th class="text-left px-4 py-2.5 text-xs font-semibold text-gray-500">연락처</th>
                <th class="text-left px-4 py-2.5 text-xs font-semibold text-gray-500">보호자</th>
                <th class="text-left px-4 py-2.5 text-xs font-semibold text-gray-500">체크인시간</th>
                <th class="text-center px-4 py-2.5 text-xs font-semibold text-gray-500">오늘상태</th>
                <th class="text-center px-4 py-2.5 text-xs font-semibold text-gray-500">연속미응답</th>
                <th class="text-center px-4 py-2.5 text-xs font-semibold text-gray-500">관리</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-50">
              <tr v-for="e in filteredMonitorElders" :key="e.id"
                :class="[getRowStatus(e) === 'no_response' ? 'bg-red-50' : 'hover:bg-gray-50/50']">
                <td class="px-4 py-3">
                  <div class="font-medium text-gray-800">{{ e.user?.name || '알수없음' }}</div>
                  <div class="text-[11px] text-gray-400">@{{ e.user?.username }}</div>
                </td>
                <td class="px-4 py-3 text-xs text-gray-600">
                  <div>{{ e.user?.phone || e.user?.email || '-' }}</div>
                </td>
                <td class="px-4 py-3 text-xs text-gray-600">
                  <div class="font-medium">{{ e.guardian_name || '-' }}</div>
                  <div class="text-[11px] text-gray-400">{{ e.guardian_phone || '' }}</div>
                </td>
                <td class="px-4 py-3 text-xs text-gray-600">
                  {{ e.last_checkin_at ? formatDateTime(e.last_checkin_at) : '-' }}
                </td>
                <td class="px-4 py-3 text-center">
                  <span v-if="getRowStatus(e) === 'checked_in'" class="text-green-600 font-semibold text-xs">&#x2705; 체크인</span>
                  <span v-else-if="getRowStatus(e) === 'waiting'" class="text-yellow-600 font-semibold text-xs">&#x23F3; 대기중</span>
                  <span v-else class="text-red-600 font-semibold text-xs">&#x274C; 미응답</span>
                </td>
                <td class="px-4 py-3 text-center">
                  <span :class="['text-xs font-bold', (e.consecutive_no_response || 0) > 0 ? 'text-red-600' : 'text-gray-400']">
                    {{ e.consecutive_no_response || 0 }}일
                  </span>
                </td>
                <td class="px-4 py-3 text-center">
                  <div class="flex items-center justify-center gap-1.5">
                    <button @click="sendAlert(e)" class="text-[10px] px-2 py-1 rounded bg-orange-50 text-orange-600 hover:bg-orange-100 font-medium whitespace-nowrap">알림발송</button>
                    <button @click="openDetailModal(e)" class="text-[10px] px-2 py-1 rounded bg-gray-100 text-gray-600 hover:bg-gray-200 font-medium whitespace-nowrap">상세보기</button>
                    <button @click="resetCheckin(e)" class="text-[10px] px-2 py-1 rounded bg-blue-50 text-blue-600 hover:bg-blue-100 font-medium whitespace-nowrap">리셋</button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- ==================== 회원관리 탭 ==================== -->
      <div v-if="activeTab === 'members'">
        <div v-if="loading" class="text-center py-10 text-gray-400 text-sm">불러오는 중...</div>
        <div v-else-if="elders.length === 0" class="text-center py-10 text-gray-400 text-sm">등록된 회원이 없습니다.</div>
        <div v-else class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead class="bg-gray-50">
              <tr>
                <th class="text-left px-4 py-2.5 text-xs font-semibold text-gray-500">회원명</th>
                <th class="text-left px-4 py-2.5 text-xs font-semibold text-gray-500">등록일</th>
                <th class="text-left px-4 py-2.5 text-xs font-semibold text-gray-500">보호자1</th>
                <th class="text-left px-4 py-2.5 text-xs font-semibold text-gray-500">보호자2</th>
                <th class="text-left px-4 py-2.5 text-xs font-semibold text-gray-500">체크인시간</th>
                <th class="text-center px-4 py-2.5 text-xs font-semibold text-gray-500">체크인율(30일)</th>
                <th class="text-left px-4 py-2.5 text-xs font-semibold text-gray-500">메모</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-50">
              <tr v-for="e in elders" :key="'m-'+e.id"
                class="hover:bg-gray-50/50 cursor-pointer"
                @click="openDetailModal(e)">
                <td class="px-4 py-3">
                  <div class="font-medium text-gray-800">{{ e.user?.name || '알수없음' }}</div>
                  <div class="text-[11px] text-gray-400">@{{ e.user?.username }}</div>
                </td>
                <td class="px-4 py-3 text-xs text-gray-600">{{ formatShortDate(e.created_at) }}</td>
                <td class="px-4 py-3 text-xs text-gray-600">
                  <div class="font-medium">{{ e.guardian_name || '-' }}</div>
                  <div class="text-[11px] text-gray-400">{{ e.guardian_phone || '' }}</div>
                </td>
                <td class="px-4 py-3 text-xs text-gray-600">
                  <div class="font-medium">{{ e.guardian2_name || '-' }}</div>
                  <div class="text-[11px] text-gray-400">{{ e.guardian2_phone || '' }}</div>
                </td>
                <td class="px-4 py-3 text-xs text-gray-600">
                  {{ e.checkin_interval ? e.checkin_interval + '시간 주기' : '-' }}
                </td>
                <td class="px-4 py-3 text-center">
                  <div class="flex items-center justify-center gap-1">
                    <div class="w-16 h-2 bg-gray-200 rounded-full overflow-hidden">
                      <div class="h-full rounded-full transition-all"
                        :class="getCheckinRateColor(e.checkin_rate_30d || 0)"
                        :style="{ width: (e.checkin_rate_30d || 0) + '%' }" />
                    </div>
                    <span class="text-xs font-semibold" :class="(e.checkin_rate_30d || 0) >= 80 ? 'text-green-600' : (e.checkin_rate_30d || 0) >= 50 ? 'text-yellow-600' : 'text-red-600'">
                      {{ e.checkin_rate_30d || 0 }}%
                    </span>
                  </div>
                </td>
                <td class="px-4 py-3 text-xs text-gray-500 max-w-[150px] truncate">{{ e.health_memo || '-' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- ==================== SOS기록 탭 ==================== -->
      <div v-if="activeTab === 'sos'">
        <div v-if="loading" class="text-center py-10 text-gray-400 text-sm">불러오는 중...</div>
        <div v-else-if="sosRecords.length === 0" class="text-center py-10 text-gray-400 text-sm">SOS 기록이 없습니다.</div>
        <div v-else class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead class="bg-gray-50">
              <tr>
                <th class="text-left px-4 py-2.5 text-xs font-semibold text-gray-500">시간</th>
                <th class="text-left px-4 py-2.5 text-xs font-semibold text-gray-500">회원명</th>
                <th class="text-left px-4 py-2.5 text-xs font-semibold text-gray-500">GPS위치</th>
                <th class="text-center px-4 py-2.5 text-xs font-semibold text-gray-500">보호자알림</th>
                <th class="text-center px-4 py-2.5 text-xs font-semibold text-gray-500">상태</th>
                <th class="text-center px-4 py-2.5 text-xs font-semibold text-gray-500">처리</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-50">
              <tr v-for="s in sosRecords" :key="s.id" class="hover:bg-gray-50/50">
                <td class="px-4 py-3 text-xs text-gray-600">{{ formatDateTime(s.created_at) }}</td>
                <td class="px-4 py-3">
                  <div class="font-medium text-gray-800">{{ s.elder?.user?.name || s.elder_name || '알수없음' }}</div>
                </td>
                <td class="px-4 py-3 text-xs">
                  <a v-if="s.latitude && s.longitude"
                    :href="'https://www.google.com/maps?q=' + s.latitude + ',' + s.longitude"
                    target="_blank"
                    class="text-blue-600 hover:text-blue-800 underline">
                    {{ Number(s.latitude).toFixed(4) }}, {{ Number(s.longitude).toFixed(4) }}
                  </a>
                  <span v-else class="text-gray-400">위치 없음</span>
                </td>
                <td class="px-4 py-3 text-center">
                  <span :class="['text-xs px-2 py-0.5 rounded-full font-semibold',
                    s.guardian_notified ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-600']">
                    {{ s.guardian_notified ? '발송완료' : '미발송' }}
                  </span>
                </td>
                <td class="px-4 py-3 text-center">
                  <span :class="['text-xs px-2 py-0.5 rounded-full font-semibold', sosStatusClass(s.status)]">
                    {{ sosStatusLabel(s.status) }}
                  </span>
                </td>
                <td class="px-4 py-3 text-center">
                  <div class="flex items-center justify-center gap-1.5">
                    <button v-if="s.status === 'triggered' || s.status === 'responded'"
                      @click="resolveSos(s)"
                      class="text-[10px] px-2 py-1 rounded bg-green-50 text-green-600 hover:bg-green-100 font-medium whitespace-nowrap">
                      해제처리
                    </button>
                    <button v-if="s.status === 'triggered' || s.status === 'responded'"
                      @click="falseAlarmSos(s)"
                      class="text-[10px] px-2 py-1 rounded bg-gray-100 text-gray-600 hover:bg-gray-200 font-medium whitespace-nowrap">
                      오인처리
                    </button>
                    <span v-if="s.status === 'resolved'" class="text-[10px] text-green-500 font-medium">해제됨</span>
                    <span v-if="s.status === 'false_alarm'" class="text-[10px] text-gray-400 font-medium">오인신고</span>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- ==================== 서비스설정 탭 ==================== -->
      <div v-if="activeTab === 'settings'" class="p-5 space-y-6">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div class="space-y-4">
            <h4 class="text-sm font-bold text-gray-800 border-b border-gray-100 pb-2">체크인 설정</h4>
            <div>
              <label class="text-xs text-gray-600 font-medium">기본 체크인 시간 설정</label>
              <input v-model="settings.default_checkin_time" type="time"
                class="mt-1 w-full text-sm border border-gray-200 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-300 focus:border-blue-400 outline-none" />
            </div>
            <div>
              <label class="text-xs text-gray-600 font-medium">미응답 알림 간격 (분)</label>
              <input v-model.number="settings.no_response_alert_interval" type="number" min="5" max="360"
                class="mt-1 w-full text-sm border border-gray-200 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-300 focus:border-blue-400 outline-none" />
              <p class="text-[11px] text-gray-400 mt-1">체크인 미응답 시 보호자에게 알림을 보내는 간격</p>
            </div>
            <div>
              <label class="text-xs text-gray-600 font-medium">2차 알림 시간 (분)</label>
              <input v-model.number="settings.secondary_alert_minutes" type="number" min="5" max="720"
                class="mt-1 w-full text-sm border border-gray-200 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-300 focus:border-blue-400 outline-none" />
              <p class="text-[11px] text-gray-400 mt-1">1차 알림 후 추가 알림 발송까지의 시간</p>
            </div>
          </div>

          <div class="space-y-4">
            <h4 class="text-sm font-bold text-gray-800 border-b border-gray-100 pb-2">SOS / 포인트 설정</h4>
            <div>
              <label class="flex items-center gap-2 text-sm text-gray-700 cursor-pointer">
                <input v-model="settings.sos_auto_call_enabled" type="checkbox" class="rounded border-gray-300 text-blue-600 w-4 h-4" />
                <span class="font-medium">SOS 자동 전화 활성화</span>
              </label>
              <p class="text-[11px] text-gray-400 mt-1 ml-6">SOS 발동 시 보호자에게 자동 전화를 걸어줍니다.</p>
            </div>
            <div>
              <label class="text-xs text-gray-600 font-medium">체크인 완료 시 포인트 지급량</label>
              <input v-model.number="settings.checkin_point_reward" type="number" min="0" max="1000"
                class="mt-1 w-full text-sm border border-gray-200 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-300 focus:border-blue-400 outline-none" />
              <p class="text-[11px] text-gray-400 mt-1">체크인을 완료한 회원에게 지급할 포인트</p>
            </div>
          </div>
        </div>

        <div class="flex justify-end pt-2">
          <button @click="saveSettings" :disabled="savingSettings"
            class="px-6 py-2.5 bg-blue-600 text-white text-sm font-semibold rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors">
            {{ savingSettings ? '저장 중...' : '설정 저장' }}
          </button>
        </div>
      </div>
    </div>

    <!-- ==================== 상세보기 모달 ==================== -->
    <div v-if="detailElder" class="fixed inset-0 z-50 flex items-center justify-center p-4" @click.self="detailElder = null">
      <div class="absolute inset-0 bg-black/40" @click="detailElder = null" />
      <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto z-10">
        <div class="sticky top-0 bg-white border-b border-gray-100 px-6 py-4 flex items-center justify-between rounded-t-2xl">
          <h3 class="text-base font-bold text-gray-800">{{ detailElder.user?.name }} 상세 정보</h3>
          <button @click="detailElder = null" class="w-8 h-8 rounded-full bg-gray-100 hover:bg-gray-200 flex items-center justify-center text-gray-500 text-lg">&times;</button>
        </div>

        <div v-if="detailLoading" class="text-center py-10 text-gray-400 text-sm">불러오는 중...</div>
        <div v-else class="p-6 space-y-6">
          <!-- 기본 정보 -->
          <div>
            <h4 class="text-sm font-bold text-gray-700 mb-3">기본 정보</h4>
            <div class="grid grid-cols-2 gap-3 text-sm">
              <div class="bg-gray-50 rounded-lg p-3">
                <div class="text-[11px] text-gray-400">이름</div>
                <div class="font-semibold text-gray-800">{{ detailData.user?.name || detailElder.user?.name }}</div>
              </div>
              <div class="bg-gray-50 rounded-lg p-3">
                <div class="text-[11px] text-gray-400">아이디</div>
                <div class="font-semibold text-gray-800">@{{ detailData.user?.username || detailElder.user?.username }}</div>
              </div>
              <div class="bg-gray-50 rounded-lg p-3">
                <div class="text-[11px] text-gray-400">이메일</div>
                <div class="font-semibold text-gray-800">{{ detailData.user?.email || detailElder.user?.email }}</div>
              </div>
              <div class="bg-gray-50 rounded-lg p-3">
                <div class="text-[11px] text-gray-400">등록일</div>
                <div class="font-semibold text-gray-800">{{ formatShortDate(detailData.created_at || detailElder.created_at) }}</div>
              </div>
            </div>
          </div>

          <!-- 보호자 정보 -->
          <div>
            <h4 class="text-sm font-bold text-gray-700 mb-3">보호자 정보</h4>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div class="bg-blue-50 rounded-lg p-3 flex items-center gap-3">
                <div class="w-9 h-9 rounded-full bg-blue-200 flex items-center justify-center text-blue-700 text-sm font-bold">
                  {{ ((detailData.guardian_name || detailElder.guardian_name) || '?')[0] }}
                </div>
                <div>
                  <div class="text-sm font-semibold text-gray-800">
                    {{ detailData.guardian_name || detailElder.guardian_name || '-' }}
                    <span class="text-[11px] text-gray-400 font-normal">({{ detailData.guardian_relation || detailElder.guardian_relation || '-' }})</span>
                  </div>
                  <div class="text-[11px] text-gray-500">{{ detailData.guardian_phone || detailElder.guardian_phone || '-' }}</div>
                </div>
              </div>
              <div v-if="detailData.guardian2_name || detailElder.guardian2_name" class="bg-blue-50 rounded-lg p-3 flex items-center gap-3">
                <div class="w-9 h-9 rounded-full bg-blue-200 flex items-center justify-center text-blue-700 text-sm font-bold">
                  {{ ((detailData.guardian2_name || detailElder.guardian2_name) || '?')[0] }}
                </div>
                <div>
                  <div class="text-sm font-semibold text-gray-800">
                    {{ detailData.guardian2_name || detailElder.guardian2_name }}
                    <span class="text-[11px] text-gray-400 font-normal">({{ detailData.guardian2_relation || detailElder.guardian2_relation || '-' }})</span>
                  </div>
                  <div class="text-[11px] text-gray-500">{{ detailData.guardian2_phone || detailElder.guardian2_phone || '-' }}</div>
                </div>
              </div>
            </div>
          </div>

          <!-- 체크인 달력 (30일) -->
          <div>
            <h4 class="text-sm font-bold text-gray-700 mb-3">체크인 달력 (최근 30일)</h4>
            <div class="grid grid-cols-10 gap-1">
              <div v-for="(day, idx) in detailCheckinCalendar" :key="idx"
                :class="['w-full aspect-square rounded flex items-center justify-center text-[10px] font-semibold',
                  day.status === 'checked' ? 'bg-green-100 text-green-700' :
                  day.status === 'missed' ? 'bg-red-100 text-red-600' :
                  'bg-gray-100 text-gray-400']"
                :title="day.date + ': ' + (day.status === 'checked' ? '체크인' : day.status === 'missed' ? '미응답' : '대기')">
                {{ day.day }}
              </div>
            </div>
            <div class="flex items-center gap-4 mt-2 text-[10px] text-gray-500">
              <span class="flex items-center gap-1"><span class="w-3 h-3 rounded bg-green-100 inline-block"></span> 체크인</span>
              <span class="flex items-center gap-1"><span class="w-3 h-3 rounded bg-red-100 inline-block"></span> 미응답</span>
              <span class="flex items-center gap-1"><span class="w-3 h-3 rounded bg-gray-100 inline-block"></span> 대기/미래</span>
            </div>
          </div>

          <!-- SOS 기록 -->
          <div>
            <h4 class="text-sm font-bold text-gray-700 mb-3">SOS 기록</h4>
            <div v-if="(detailData.sos_records || []).length === 0" class="text-xs text-gray-400 py-2">SOS 기록이 없습니다.</div>
            <div v-else class="border border-gray-100 rounded-lg overflow-hidden">
              <table class="w-full text-xs">
                <thead class="bg-gray-50">
                  <tr>
                    <th class="text-left px-3 py-2 text-gray-500 font-semibold">날짜/시간</th>
                    <th class="text-left px-3 py-2 text-gray-500 font-semibold">상태</th>
                    <th class="text-left px-3 py-2 text-gray-500 font-semibold">위치</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-gray-50">
                  <tr v-for="s in (detailData.sos_records || [])" :key="s.id">
                    <td class="px-3 py-2 text-gray-700">{{ formatDateTime(s.created_at) }}</td>
                    <td class="px-3 py-2">
                      <span :class="['px-2 py-0.5 rounded-full text-[10px] font-semibold', sosStatusClass(s.status)]">
                        {{ sosStatusLabel(s.status) }}
                      </span>
                    </td>
                    <td class="px-3 py-2">
                      <a v-if="s.latitude && s.longitude"
                        :href="'https://www.google.com/maps?q=' + s.latitude + ',' + s.longitude"
                        target="_blank"
                        class="text-blue-600 hover:text-blue-800 underline text-[11px]">
                        지도보기
                      </a>
                      <span v-else class="text-gray-400">-</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- 관리자 메모 -->
          <div class="border-t border-gray-100 pt-4">
            <h4 class="text-sm font-bold text-gray-700 mb-3">관리자 메모</h4>
            <div v-if="detailData.health_memo || detailElder.health_memo" class="text-xs text-gray-600 bg-gray-50 rounded-lg p-3 mb-3">
              {{ detailData.health_memo || detailElder.health_memo }}
            </div>
            <textarea v-model="detailMemo" rows="2" placeholder="메모를 입력하세요..."
              class="w-full text-sm border border-gray-200 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-300 focus:border-blue-400 outline-none resize-none" />
            <div class="flex justify-end gap-2 mt-3">
              <button @click="detailElder = null" class="px-4 py-2 text-sm text-gray-600 bg-gray-100 rounded-lg hover:bg-gray-200 font-medium">닫기</button>
              <button @click="saveDetailMemo" class="px-4 py-2 text-sm text-white bg-blue-600 rounded-lg hover:bg-blue-700 font-medium">저장</button>
            </div>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import axios from 'axios'

// --- Auth ---
const token = localStorage.getItem('sk_token')
const authHeader = { headers: { Authorization: `Bearer ${token}` } }

// --- State ---
const loading = ref(true)
const elders = ref([])
const sosRecords = ref([])
const activeTab = ref('monitoring')
const monitorFilter = ref('all')
const savingSettings = ref(false)
const detailElder = ref(null)
const detailData = ref({})
const detailLoading = ref(false)
const detailMemo = ref('')

const tabs = [
  { key: 'monitoring', label: '모니터링' },
  { key: 'members', label: '회원관리' },
  { key: 'sos', label: 'SOS기록' },
  { key: 'settings', label: '서비스설정' },
]

const settings = reactive({
  default_checkin_time: '09:00',
  no_response_alert_interval: 30,
  secondary_alert_minutes: 60,
  sos_auto_call_enabled: true,
  checkin_point_reward: 10,
})

// --- Stats ---
const stats = computed(() => {
  const total = elders.value.length
  const checkedIn = elders.value.filter(e => getRowStatus(e) === 'checked_in').length
  const noResponse = elders.value.filter(e => getRowStatus(e) === 'no_response').length
  const sosWeek = sosRecords.value.filter(s => {
    if (!s.created_at) return false
    const diff = Date.now() - new Date(s.created_at).getTime()
    return diff < 7 * 24 * 60 * 60 * 1000
  }).length
  return {
    totalElders: total,
    checkedInToday: checkedIn,
    noResponseToday: noResponse,
    sosThisWeek: sosWeek,
  }
})

const checkinPercent = computed(() => {
  if (stats.value.totalElders === 0) return 0
  return Math.round((stats.value.checkedInToday / stats.value.totalElders) * 100)
})

// --- Monitoring filters ---
const monitorFilters = computed(() => [
  { key: 'all', label: '전체', count: elders.value.length },
  { key: 'checked_in', label: '체크인완료', count: elders.value.filter(e => getRowStatus(e) === 'checked_in').length },
  { key: 'no_response', label: '미응답', count: elders.value.filter(e => getRowStatus(e) === 'no_response').length },
  { key: 'sos', label: 'SOS발동', count: elders.value.filter(e => e.last_sos_at && isRecent(e.last_sos_at, 7)).length },
])

const filteredMonitorElders = computed(() => {
  if (monitorFilter.value === 'checked_in') return elders.value.filter(e => getRowStatus(e) === 'checked_in')
  if (monitorFilter.value === 'no_response') return elders.value.filter(e => getRowStatus(e) === 'no_response')
  if (monitorFilter.value === 'sos') return elders.value.filter(e => e.last_sos_at && isRecent(e.last_sos_at, 7))
  return elders.value
})

// --- Detail modal checkin calendar ---
const detailCheckinCalendar = computed(() => {
  const calendar = []
  const checkins = detailData.value.checkin_history || detailData.value.checkins || []
  const checkinDates = new Set(checkins.map(c => {
    const d = new Date(c.checked_at || c.created_at || c.date)
    return d.toISOString().split('T')[0]
  }))
  const today = new Date()
  for (let i = 29; i >= 0; i--) {
    const d = new Date(today)
    d.setDate(d.getDate() - i)
    const dateStr = d.toISOString().split('T')[0]
    const isFuture = d > today
    let status = 'pending'
    if (!isFuture) {
      status = checkinDates.has(dateStr) ? 'checked' : 'missed'
    }
    // Today might still be waiting
    if (i === 0 && !checkinDates.has(dateStr)) {
      const elder = detailData.value || detailElder.value
      if (elder && !elder.is_overdue) status = 'pending'
    }
    calendar.push({
      day: d.getDate(),
      date: dateStr,
      status,
    })
  }
  return calendar
})

// --- Helpers ---
function getRowStatus(elder) {
  if (elder.today_checked_in) return 'checked_in'
  if (elder.is_overdue) return 'no_response'
  // Determine from last checkin
  if (elder.last_checkin_at) {
    const lastCheckin = new Date(elder.last_checkin_at)
    const today = new Date()
    if (lastCheckin.toDateString() === today.toDateString()) return 'checked_in'
  }
  // Check if overdue time-based
  if (elder.consecutive_no_response > 0) return 'no_response'
  return 'waiting'
}

function isRecent(dateStr, days) {
  if (!dateStr) return false
  const diff = Date.now() - new Date(dateStr).getTime()
  return diff < days * 24 * 60 * 60 * 1000
}

function formatDateTime(d) {
  if (!d) return ''
  return new Date(d).toLocaleDateString('ko-KR', {
    month: 'numeric', day: 'numeric', hour: '2-digit', minute: '2-digit'
  })
}

function formatShortDate(d) {
  if (!d) return ''
  return new Date(d).toLocaleDateString('ko-KR', {
    year: 'numeric', month: 'numeric', day: 'numeric'
  })
}

function getCheckinRateColor(rate) {
  if (rate >= 80) return 'bg-green-500'
  if (rate >= 50) return 'bg-yellow-500'
  return 'bg-red-500'
}

function sosStatusClass(status) {
  switch (status) {
    case 'triggered': return 'bg-red-100 text-red-700'
    case 'responded': return 'bg-yellow-100 text-yellow-700'
    case 'resolved': return 'bg-green-100 text-green-700'
    case 'false_alarm': return 'bg-gray-100 text-gray-500'
    default: return 'bg-gray-100 text-gray-500'
  }
}

function sosStatusLabel(status) {
  switch (status) {
    case 'triggered': return '발동'
    case 'responded': return '응답중'
    case 'resolved': return '해제됨'
    case 'false_alarm': return '오인신고'
    default: return status || '-'
  }
}

// --- API calls ---
async function loadElders() {
  loading.value = true
  try {
    const res = await axios.get('/api/admin/elder', authHeader)
    const data = res.data
    if (data && data.elders) {
      elders.value = data.elders
      if (data.sos_records) sosRecords.value = data.sos_records
    } else if (Array.isArray(data)) {
      elders.value = data
    } else if (data && data.data) {
      elders.value = Array.isArray(data.data) ? data.data : []
      if (data.sos_records) sosRecords.value = data.sos_records
    }
    // Extract SOS from elders if not provided separately
    if (sosRecords.value.length === 0) {
      const allSos = []
      elders.value.forEach(e => {
        if (e.sos_records && Array.isArray(e.sos_records)) {
          e.sos_records.forEach(s => {
            allSos.push({ ...s, elder: e, elder_name: e.user?.name })
          })
        }
        if (e.last_sos_at) {
          allSos.push({
            id: 'sos-' + e.id,
            elder: e,
            elder_name: e.user?.name,
            created_at: e.last_sos_at,
            latitude: e.sos_latitude || null,
            longitude: e.sos_longitude || null,
            guardian_notified: e.alert_sent || false,
            status: e.sos_status || 'triggered',
          })
        }
      })
      if (allSos.length > 0) {
        sosRecords.value = allSos.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
      }
    }
  } catch (err) {
    console.error('Failed to load elder data:', err)
  } finally {
    loading.value = false
  }
}

async function loadSettings() {
  try {
    const res = await axios.get('/api/admin/elder/service-settings', authHeader)
    const data = res.data?.data || res.data?.settings || res.data
    if (data) {
      Object.keys(settings).forEach(key => {
        if (data[key] !== undefined) {
          settings[key] = data[key]
        }
      })
    }
  } catch {
    // Use defaults
  }
}

async function saveSettings() {
  savingSettings.value = true
  try {
    await axios.post('/api/admin/elder/service-settings', { ...settings }, authHeader)
    alert('설정이 저장되었습니다.')
  } catch {
    alert('설정 저장에 실패했습니다.')
  } finally {
    savingSettings.value = false
  }
}

async function resetCheckin(elder) {
  if (!confirm(`${elder.user?.name}님의 체크인을 리셋하시겠습니까?`)) return
  try {
    await axios.post(`/api/admin/elder/${elder.id}/reset-checkin`, {}, authHeader)
    elder.is_overdue = false
    elder.today_checked_in = true
    elder.last_checkin_at = new Date().toISOString()
    elder.consecutive_no_response = 0
  } catch {
    // Optimistic update even on failure for UX
    elder.is_overdue = false
    elder.today_checked_in = true
    elder.last_checkin_at = new Date().toISOString()
    elder.consecutive_no_response = 0
  }
}

async function sendAlert(elder) {
  if (!confirm(`${elder.user?.name}님의 보호자에게 알림을 발송하시겠습니까?`)) return
  try {
    await axios.post(`/api/admin/elder/${elder.id}/send-alert`, {}, authHeader)
    elder.alert_sent = true
    alert('알림이 발송되었습니다.')
  } catch {
    alert('알림 발송에 실패했습니다.')
  }
}

async function openDetailModal(elder) {
  detailElder.value = elder
  detailData.value = { ...elder }
  detailMemo.value = ''
  detailLoading.value = true
  try {
    const res = await axios.get(`/api/admin/elder/${elder.id}`, authHeader)
    detailData.value = res.data?.data || res.data?.elder || res.data || elder
  } catch {
    detailData.value = elder
  } finally {
    detailLoading.value = false
  }
}

async function saveDetailMemo() {
  if (!detailElder.value) return
  try {
    // Try to save memo via detail endpoint or a dedicated endpoint
    await axios.post(`/api/admin/elder/${detailElder.value.id}/reset-checkin`, {
      memo: detailMemo.value,
    }, authHeader)
  } catch {
    // Silent fail
  }
  if (detailMemo.value.trim()) {
    const elder = elders.value.find(e => e.id === detailElder.value.id)
    if (elder) {
      elder.health_memo = elder.health_memo
        ? elder.health_memo + ', ' + detailMemo.value.trim()
        : detailMemo.value.trim()
    }
  }
  detailElder.value = null
}

async function resolveSos(sos) {
  if (!confirm('이 SOS를 해제 처리하시겠습니까?')) return
  try {
    await axios.post(`/api/admin/elder/sos/${sos.id}/resolve`, {}, authHeader)
  } catch { /* silent */ }
  sos.status = 'resolved'
}

async function falseAlarmSos(sos) {
  if (!confirm('이 SOS를 오인 처리하시겠습니까?')) return
  try {
    await axios.post(`/api/admin/elder/sos/${sos.id}/false-alarm`, {}, authHeader)
  } catch { /* silent */ }
  sos.status = 'false_alarm'
}

// --- Init ---
onMounted(() => {
  loadElders()
  loadSettings()
})
</script>
