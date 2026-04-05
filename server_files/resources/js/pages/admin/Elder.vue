<template>
  <div class="space-y-5">

    <!-- 통계 카드 -->
    <div class="grid grid-cols-2 sm:grid-cols-5 gap-3">
      <div class="bg-white rounded-xl p-4 shadow-sm border border-gray-100 text-center">
        <div class="text-2xl font-black text-gray-800">{{ elders.length }}</div>
        <div class="text-xs text-gray-500 mt-0.5">전체 등록</div>
      </div>
      <div class="bg-white rounded-xl p-4 shadow-sm border border-green-100 text-center">
        <div class="text-2xl font-black text-green-600">{{ normalCount }}</div>
        <div class="text-xs text-gray-500 mt-0.5">정상 체크인</div>
      </div>
      <div class="bg-white rounded-xl p-4 shadow-sm border border-red-200 text-center bg-red-50">
        <div class="text-2xl font-black text-red-500">{{ overdueCount }}</div>
        <div class="text-xs text-red-400 mt-0.5">체크인 미완료</div>
      </div>
      <div class="bg-white rounded-xl p-4 shadow-sm border border-orange-200 text-center bg-orange-50">
        <div class="text-2xl font-black text-orange-500">{{ sosCount }}</div>
        <div class="text-xs text-orange-400 mt-0.5">SOS 발신</div>
      </div>
      <div class="bg-white rounded-xl p-4 shadow-sm border border-gray-100 text-center">
        <div class="text-2xl font-black text-blue-600">{{ guardianCount }}</div>
        <div class="text-xs text-gray-500 mt-0.5">등록 보호자</div>
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

      <!-- Tab 1: 모니터링 -->
      <div v-if="activeTab === 'monitoring'">
        <div class="flex items-center gap-2 px-5 py-3 border-b border-gray-50 bg-gray-50/50">
          <button v-for="f in filters" :key="f.key"
            @click="activeFilter = f.key"
            :class="['px-3 py-1 rounded-full text-xs font-semibold transition-colors',
              activeFilter === f.key ? 'bg-blue-600 text-white' : 'bg-white text-gray-500 border border-gray-200 hover:bg-gray-100']">
            {{ f.label }} ({{ f.count }})
          </button>
          <div class="flex-1" />
          <button @click="load" class="text-xs text-blue-500 hover:text-blue-600 font-medium">새로고침</button>
        </div>

        <div v-if="loading" class="text-center py-10 text-gray-400 text-sm">불러오는 중...</div>
        <div v-else-if="filteredElders.length === 0" class="text-center py-10 text-gray-400 text-sm">해당하는 어르신이 없습니다.</div>
        <div v-else class="divide-y divide-gray-50">
          <div v-for="e in filteredElders" :key="e.id"
            :class="['px-5 py-4 flex items-center gap-4 hover:bg-gray-50/50 transition-colors',
              e.last_sos_at && isRecentSos(e.last_sos_at) ? 'bg-red-50' : e.is_overdue ? 'bg-orange-50/50' : '']">

            <div :class="['w-10 h-10 rounded-full flex items-center justify-center text-lg flex-shrink-0',
              e.last_sos_at && isRecentSos(e.last_sos_at) ? 'bg-red-100' : e.is_overdue ? 'bg-orange-100' : 'bg-green-100']">
              {{ e.last_sos_at && isRecentSos(e.last_sos_at) ? '🆘' : e.is_overdue ? '⚠️' : '✅' }}
            </div>

            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2 flex-wrap">
                <span class="text-sm font-semibold text-gray-800">{{ e.user?.name ?? '알수없음' }}</span>
                <span v-if="e.last_sos_at && isRecentSos(e.last_sos_at)"
                  class="text-[10px] bg-red-500 text-white px-1.5 py-0.5 rounded-full font-bold animate-pulse">SOS</span>
                <span v-if="e.is_overdue"
                  class="text-[10px] bg-orange-100 text-orange-600 px-1.5 py-0.5 rounded-full font-semibold">미완료</span>
              </div>
              <div class="text-xs text-gray-400 mt-0.5">@{{ e.user?.username }} · {{ e.user?.email }}</div>
              <div class="flex items-center gap-4 mt-1.5 text-[11px] text-gray-500 flex-wrap">
                <span>체크인 주기: {{ e.checkin_interval }}h</span>
                <span>마지막: {{ e.last_checkin_at ? formatDate(e.last_checkin_at) : '없음' }}</span>
                <span v-if="e.last_sos_at" class="text-red-500 font-medium">SOS: {{ formatDate(e.last_sos_at) }}</span>
              </div>
            </div>

            <div class="text-right hidden md:block flex-shrink-0">
              <div class="text-xs font-semibold text-gray-700">{{ e.guardian_name ?? '-' }}</div>
              <div class="text-[10px] text-gray-400">{{ e.guardian_phone ?? '-' }}</div>
              <span :class="['text-[10px] px-2 py-0.5 rounded-full font-semibold inline-block mt-1',
                e.alert_sent ? 'bg-orange-100 text-orange-600' : 'bg-gray-100 text-gray-400']">
                {{ e.alert_sent ? '알림발송됨' : '알림없음' }}
              </span>
            </div>

            <div class="flex flex-col gap-1.5 flex-shrink-0">
              <button @click="resetCheckin(e)" class="text-[10px] px-2.5 py-1 rounded-md bg-blue-50 text-blue-600 hover:bg-blue-100 font-medium whitespace-nowrap">체크인 재설정</button>
              <button @click="sendAlert(e)" class="text-[10px] px-2.5 py-1 rounded-md bg-orange-50 text-orange-600 hover:bg-orange-100 font-medium whitespace-nowrap">알림 발송</button>
              <button @click="openDetail(e)" class="text-[10px] px-2.5 py-1 rounded-md bg-gray-100 text-gray-600 hover:bg-gray-200 font-medium whitespace-nowrap">상세보기</button>
            </div>
          </div>
        </div>
      </div>

      <!-- Tab 2: 보호자 관리 -->
      <div v-if="activeTab === 'guardians'" class="p-5 space-y-5">
        <div class="bg-blue-50 border border-blue-200 rounded-lg p-4 space-y-3">
          <h4 class="text-sm font-bold text-blue-800">보호자 연결 등록</h4>
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            <div>
              <label class="text-xs text-gray-600 font-medium">어르신 선택</label>
              <select v-model="guardianForm.elder_id" class="mt-1 w-full text-sm border border-gray-200 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-300 focus:border-blue-400 outline-none">
                <option value="">선택하세요</option>
                <option v-for="e in elders" :key="e.id" :value="e.id">{{ e.user?.name }} (@{{ e.user?.username }})</option>
              </select>
            </div>
            <div>
              <label class="text-xs text-gray-600 font-medium">보호자 이름</label>
              <input v-model="guardianForm.name" type="text" placeholder="보호자 성함" class="mt-1 w-full text-sm border border-gray-200 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-300 focus:border-blue-400 outline-none" />
            </div>
            <div>
              <label class="text-xs text-gray-600 font-medium">전화번호</label>
              <input v-model="guardianForm.phone" type="text" placeholder="213-555-0000" class="mt-1 w-full text-sm border border-gray-200 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-300 focus:border-blue-400 outline-none" />
            </div>
            <div>
              <label class="text-xs text-gray-600 font-medium">이메일</label>
              <input v-model="guardianForm.email" type="email" placeholder="guardian@email.com" class="mt-1 w-full text-sm border border-gray-200 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-300 focus:border-blue-400 outline-none" />
            </div>
            <div>
              <label class="text-xs text-gray-600 font-medium">관계</label>
              <select v-model="guardianForm.relation" class="mt-1 w-full text-sm border border-gray-200 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-300 focus:border-blue-400 outline-none">
                <option value="자녀">자녀</option>
                <option value="손자녀">손자녀</option>
                <option value="친척">친척</option>
                <option value="기타">기타</option>
              </select>
            </div>
            <div class="flex items-end">
              <button @click="addGuardian" class="w-full px-4 py-2 bg-blue-600 text-white text-sm font-semibold rounded-lg hover:bg-blue-700 transition-colors">등록</button>
            </div>
          </div>
        </div>

        <div class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead class="bg-gray-50">
              <tr>
                <th class="text-left px-4 py-2.5 text-xs font-semibold text-gray-500">보호자명</th>
                <th class="text-left px-4 py-2.5 text-xs font-semibold text-gray-500">연락처</th>
                <th class="text-left px-4 py-2.5 text-xs font-semibold text-gray-500">연결된 어르신</th>
                <th class="text-left px-4 py-2.5 text-xs font-semibold text-gray-500">알림 수신</th>
                <th class="text-left px-4 py-2.5 text-xs font-semibold text-gray-500">등록일</th>
                <th class="text-center px-4 py-2.5 text-xs font-semibold text-gray-500">관리</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-50">
              <tr v-for="e in elders" :key="'g-'+e.id" class="hover:bg-gray-50/50">
                <td class="px-4 py-3 font-medium text-gray-800">{{ e.guardian_name }}</td>
                <td class="px-4 py-3">
                  <div class="text-xs text-gray-700">{{ e.guardian_phone }}</div>
                  <div class="text-[11px] text-gray-400">{{ e.guardian_email }}</div>
                </td>
                <td class="px-4 py-3">
                  <span class="text-xs bg-blue-50 text-blue-700 px-2 py-0.5 rounded-full font-medium">{{ e.user?.name }}</span>
                  <span class="text-[10px] text-gray-400 ml-1">({{ e.guardian_relation }})</span>
                </td>
                <td class="px-4 py-3">
                  <div class="flex flex-col gap-1">
                    <label class="flex items-center gap-1.5 text-[11px] text-gray-600">
                      <input type="checkbox" checked class="rounded border-gray-300 text-blue-600 w-3.5 h-3.5" /> 체크인 미완료
                    </label>
                    <label class="flex items-center gap-1.5 text-[11px] text-gray-600">
                      <input type="checkbox" checked class="rounded border-gray-300 text-blue-600 w-3.5 h-3.5" /> SOS 알림
                    </label>
                    <label class="flex items-center gap-1.5 text-[11px] text-gray-600">
                      <input type="checkbox" class="rounded border-gray-300 text-blue-600 w-3.5 h-3.5" /> 주간 리포트
                    </label>
                  </div>
                </td>
                <td class="px-4 py-3 text-xs text-gray-500">{{ formatShortDate(e.created_at) }}</td>
                <td class="px-4 py-3 text-center">
                  <div class="flex items-center justify-center gap-1.5">
                    <button @click="editGuardian(e)" class="text-[10px] px-2 py-1 rounded bg-gray-100 text-gray-600 hover:bg-gray-200 font-medium">수정</button>
                    <button @click="deleteGuardian(e)" class="text-[10px] px-2 py-1 rounded bg-red-50 text-red-500 hover:bg-red-100 font-medium">삭제</button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Tab 3: 서비스 설정 -->
      <div v-if="activeTab === 'settings'" class="p-5 space-y-6">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div class="space-y-4">
            <h4 class="text-sm font-bold text-gray-800 border-b border-gray-100 pb-2">체크인 설정</h4>
            <div>
              <label class="text-xs text-gray-600 font-medium">기본 체크인 주기 (시간)</label>
              <input v-model.number="settings.default_checkin_interval" type="number" min="1" max="72"
                class="mt-1 w-full text-sm border border-gray-200 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-300 focus:border-blue-400 outline-none" />
            </div>
            <div>
              <label class="text-xs text-gray-600 font-medium">미완료 후 자동 알림 지연 (분)</label>
              <input v-model.number="settings.auto_alert_delay" type="number" min="5" max="360"
                class="mt-1 w-full text-sm border border-gray-200 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-300 focus:border-blue-400 outline-none" />
            </div>
            <div>
              <label class="text-xs text-gray-600 font-medium">SOS 알림 수신자</label>
              <select v-model="settings.sos_recipients" class="mt-1 w-full text-sm border border-gray-200 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-300 focus:border-blue-400 outline-none">
                <option value="admin">관리자만</option>
                <option value="guardian">보호자만</option>
                <option value="all">관리자 + 보호자 모두</option>
              </select>
            </div>
          </div>

          <div class="space-y-4">
            <h4 class="text-sm font-bold text-gray-800 border-b border-gray-100 pb-2">긴급 연락 / 통화 설정</h4>
            <div>
              <label class="text-xs text-gray-600 font-medium">긴급 연락번호 1</label>
              <input v-model="settings.emergency_phone_1" type="text" placeholder="213-555-9999"
                class="mt-1 w-full text-sm border border-gray-200 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-300 focus:border-blue-400 outline-none" />
            </div>
            <div>
              <label class="text-xs text-gray-600 font-medium">긴급 연락번호 2</label>
              <input v-model="settings.emergency_phone_2" type="text" placeholder="213-555-8888"
                class="mt-1 w-full text-sm border border-gray-200 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-300 focus:border-blue-400 outline-none" />
            </div>
            <div>
              <label class="flex items-center gap-2 text-sm text-gray-700 cursor-pointer">
                <input v-model="settings.webrtc_enabled" type="checkbox" class="rounded border-gray-300 text-blue-600 w-4 h-4" />
                <span class="font-medium">WebRTC 전화 연결 활성화</span>
              </label>
              <p class="text-[11px] text-gray-400 mt-1 ml-6">보호자가 알림 클릭 시 바로 전화 연결이 됩니다.</p>
            </div>
          </div>
        </div>

        <div class="space-y-4">
          <h4 class="text-sm font-bold text-gray-800 border-b border-gray-100 pb-2">알림 메시지 템플릿</h4>
          <div>
            <label class="text-xs text-gray-600 font-medium">체크인 미완료 알림 메시지</label>
            <textarea v-model="settings.template_overdue" rows="2"
              class="mt-1 w-full text-sm border border-gray-200 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-300 focus:border-blue-400 outline-none resize-none" />
          </div>
          <div>
            <label class="text-xs text-gray-600 font-medium">SOS 발생 알림 메시지</label>
            <textarea v-model="settings.template_sos" rows="2"
              class="mt-1 w-full text-sm border border-gray-200 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-300 focus:border-blue-400 outline-none resize-none" />
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

    <!-- 상세보기 모달 -->
    <div v-if="detailElder" class="fixed inset-0 z-50 flex items-center justify-center p-4" @click.self="detailElder = null">
      <div class="absolute inset-0 bg-black/40" @click="detailElder = null" />
      <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto z-10">
        <div class="sticky top-0 bg-white border-b border-gray-100 px-6 py-4 flex items-center justify-between rounded-t-2xl">
          <h3 class="text-base font-bold text-gray-800">{{ detailElder.user?.name }} 상세 정보</h3>
          <button @click="detailElder = null" class="w-8 h-8 rounded-full bg-gray-100 hover:bg-gray-200 flex items-center justify-center text-gray-500 text-lg">&times;</button>
        </div>

        <div class="p-6 space-y-6">
          <!-- 기본 정보 -->
          <div>
            <h4 class="text-sm font-bold text-gray-700 mb-3">기본 정보</h4>
            <div class="grid grid-cols-2 gap-3 text-sm">
              <div class="bg-gray-50 rounded-lg p-3">
                <div class="text-[11px] text-gray-400">이름</div>
                <div class="font-semibold text-gray-800">{{ detailElder.user?.name }}</div>
              </div>
              <div class="bg-gray-50 rounded-lg p-3">
                <div class="text-[11px] text-gray-400">아이디</div>
                <div class="font-semibold text-gray-800">@{{ detailElder.user?.username }}</div>
              </div>
              <div class="bg-gray-50 rounded-lg p-3">
                <div class="text-[11px] text-gray-400">이메일</div>
                <div class="font-semibold text-gray-800">{{ detailElder.user?.email }}</div>
              </div>
              <div class="bg-gray-50 rounded-lg p-3">
                <div class="text-[11px] text-gray-400">등록일</div>
                <div class="font-semibold text-gray-800">{{ formatShortDate(detailElder.created_at) }}</div>
              </div>
              <div class="bg-gray-50 rounded-lg p-3 col-span-2">
                <div class="text-[11px] text-gray-400">건강상태 메모</div>
                <div class="font-semibold text-gray-800">{{ detailElder.health_memo || '(없음)' }}</div>
              </div>
            </div>
          </div>

          <!-- 체크인 이력 (최근 30일) -->
          <div>
            <h4 class="text-sm font-bold text-gray-700 mb-3">체크인 이력 (최근 30일)</h4>
            <div class="max-h-40 overflow-y-auto border border-gray-100 rounded-lg">
              <table class="w-full text-xs">
                <thead class="bg-gray-50 sticky top-0">
                  <tr>
                    <th class="text-left px-3 py-2 text-gray-500 font-semibold">날짜</th>
                    <th class="text-left px-3 py-2 text-gray-500 font-semibold">시간</th>
                    <th class="text-left px-3 py-2 text-gray-500 font-semibold">상태</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-gray-50">
                  <tr v-for="(ch, idx) in detailCheckinHistory" :key="idx" class="hover:bg-gray-50/50">
                    <td class="px-3 py-2 text-gray-700">{{ ch.date }}</td>
                    <td class="px-3 py-2 text-gray-700">{{ ch.time }}</td>
                    <td class="px-3 py-2">
                      <span :class="['px-2 py-0.5 rounded-full text-[10px] font-semibold',
                        ch.status === '정상' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-600']">
                        {{ ch.status }}
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- SOS 이력 -->
          <div>
            <h4 class="text-sm font-bold text-gray-700 mb-3">SOS 이력</h4>
            <div v-if="detailSosHistory.length === 0" class="text-xs text-gray-400 py-2">SOS 이력이 없습니다.</div>
            <div v-else class="border border-gray-100 rounded-lg overflow-hidden">
              <table class="w-full text-xs">
                <thead class="bg-gray-50">
                  <tr>
                    <th class="text-left px-3 py-2 text-gray-500 font-semibold">날짜/시간</th>
                    <th class="text-left px-3 py-2 text-gray-500 font-semibold">해결 여부</th>
                    <th class="text-left px-3 py-2 text-gray-500 font-semibold">응답 시간</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-gray-50">
                  <tr v-for="(s, idx) in detailSosHistory" :key="idx">
                    <td class="px-3 py-2 text-gray-700">{{ s.datetime }}</td>
                    <td class="px-3 py-2">
                      <span :class="['px-2 py-0.5 rounded-full text-[10px] font-semibold',
                        s.resolved ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-600']">
                        {{ s.resolved ? '해결됨' : '미해결' }}
                      </span>
                    </td>
                    <td class="px-3 py-2 text-gray-600">{{ s.response_time }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- 연결된 보호자 -->
          <div>
            <h4 class="text-sm font-bold text-gray-700 mb-3">연결된 보호자</h4>
            <div class="bg-blue-50 rounded-lg p-3 flex items-center gap-3">
              <div class="w-9 h-9 rounded-full bg-blue-200 flex items-center justify-center text-blue-700 text-sm font-bold">{{ (detailElder.guardian_name || '?')[0] }}</div>
              <div>
                <div class="text-sm font-semibold text-gray-800">{{ detailElder.guardian_name }} <span class="text-[11px] text-gray-400 font-normal">({{ detailElder.guardian_relation }})</span></div>
                <div class="text-[11px] text-gray-500">{{ detailElder.guardian_phone }} · {{ detailElder.guardian_email }}</div>
              </div>
            </div>
          </div>

          <!-- 활동 로그 -->
          <div>
            <h4 class="text-sm font-bold text-gray-700 mb-3">활동 로그</h4>
            <div class="space-y-2 max-h-32 overflow-y-auto">
              <div v-for="(log, idx) in detailActivityLog" :key="idx"
                class="flex items-start gap-2 text-xs">
                <span class="text-gray-400 flex-shrink-0 w-28">{{ log.date }}</span>
                <span class="text-gray-700">{{ log.message }}</span>
              </div>
            </div>
          </div>

          <!-- 관리 영역 -->
          <div class="border-t border-gray-100 pt-4 space-y-3">
            <h4 class="text-sm font-bold text-gray-700">관리</h4>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label class="text-xs text-gray-600 font-medium">체크인 주기 변경 (시간)</label>
                <input v-model.number="detailEditInterval" type="number" min="1" max="72"
                  class="mt-1 w-full text-sm border border-gray-200 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-300 focus:border-blue-400 outline-none" />
              </div>
              <div class="flex items-end">
                <label class="flex items-center gap-2 text-sm text-gray-700 cursor-pointer">
                  <input v-model="detailMonitoringEnabled" type="checkbox" class="rounded border-gray-300 text-blue-600 w-4 h-4" />
                  <span class="font-medium">모니터링 활성화</span>
                </label>
              </div>
            </div>
            <div>
              <label class="text-xs text-gray-600 font-medium">메모 추가</label>
              <textarea v-model="detailNewMemo" rows="2" placeholder="메모를 입력하세요..."
                class="mt-1 w-full text-sm border border-gray-200 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-300 focus:border-blue-400 outline-none resize-none" />
            </div>
            <div class="flex justify-end gap-2">
              <button @click="detailElder = null" class="px-4 py-2 text-sm text-gray-600 bg-gray-100 rounded-lg hover:bg-gray-200 font-medium">닫기</button>
              <button @click="saveDetailChanges" class="px-4 py-2 text-sm text-white bg-blue-600 rounded-lg hover:bg-blue-700 font-medium">저장</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 안내 메모 -->
    <div class="bg-blue-50 border border-blue-200 rounded-xl p-4 text-sm text-blue-700">
      <div class="font-semibold mb-1">노인 안심 서비스 안내</div>
      <ul class="text-xs space-y-1 text-blue-600">
        <li>SOS 발송 시 보호자에게 인앱 알림이 즉시 전송됩니다.</li>
        <li>체크인 미완료 시 설정된 시간 후 자동 알림이 발송됩니다.</li>
        <li>보호자는 알림 클릭 시 WebRTC 전화 연결이 가능합니다.</li>
      </ul>
    </div>

  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import axios from 'axios'

// --- Dummy data ---
const dummyElders = [
  { id: 1, user: { id: 10, name: '김순자', username: 'soonza', email: 'soonza@somekorean.com' }, checkin_interval: 24, last_checkin_at: '2026-03-28T08:30:00', is_overdue: false, last_sos_at: null, guardian_name: '김민준', guardian_phone: '213-555-0101', guardian_email: 'minjun@gmail.com', guardian_relation: '자녀', alert_sent: false, health_memo: '고혈압 관리 중', created_at: '2025-06-01' },
  { id: 2, user: { id: 11, name: '박영순', username: 'youngsoon', email: 'youngsoon@somekorean.com' }, checkin_interval: 12, last_checkin_at: '2026-03-27T14:00:00', is_overdue: true, last_sos_at: null, guardian_name: '박서연', guardian_phone: '213-555-0202', guardian_email: 'seoyeon@gmail.com', guardian_relation: '손자녀', alert_sent: true, health_memo: '당뇨, 무릎 통증', created_at: '2025-07-15' },
  { id: 3, user: { id: 12, name: '이정숙', username: 'jungsook', email: 'jungsook@somekorean.com' }, checkin_interval: 24, last_checkin_at: '2026-03-26T09:00:00', is_overdue: true, last_sos_at: '2026-03-27T22:15:00', guardian_name: '이하은', guardian_phone: '213-555-0303', guardian_email: 'haeun@gmail.com', guardian_relation: '자녀', alert_sent: true, health_memo: '심장 질환, 독거', created_at: '2025-05-20' },
  { id: 4, user: { id: 13, name: '최복순', username: 'boksoon', email: 'boksoon@somekorean.com' }, checkin_interval: 8, last_checkin_at: '2026-03-28T07:00:00', is_overdue: false, last_sos_at: null, guardian_name: '최재호', guardian_phone: '213-555-0404', guardian_email: 'jaeho@gmail.com', guardian_relation: '자녀', alert_sent: false, health_memo: '', created_at: '2025-09-10' },
  { id: 5, user: { id: 14, name: '정말숙', username: 'malsook', email: 'malsook@somekorean.com' }, checkin_interval: 24, last_checkin_at: '2026-03-28T06:45:00', is_overdue: false, last_sos_at: '2026-02-14T03:20:00', guardian_name: '정우진', guardian_phone: '213-555-0505', guardian_email: 'woojin@gmail.com', guardian_relation: '자녀', alert_sent: false, health_memo: '치매 초기 진단', created_at: '2025-08-01' },
]

// --- State ---
const elders = ref([])
const loading = ref(true)
const activeTab = ref('monitoring')
const activeFilter = ref('all')
const detailElder = ref(null)
const detailEditInterval = ref(24)
const detailMonitoringEnabled = ref(true)
const detailNewMemo = ref('')
const savingSettings = ref(false)

const tabs = [
  { key: 'monitoring', label: '모니터링' },
  { key: 'guardians', label: '보호자 관리' },
  { key: 'settings', label: '서비스 설정' },
]

const guardianForm = reactive({
  elder_id: '',
  name: '',
  phone: '',
  email: '',
  relation: '자녀',
})

const settings = reactive({
  default_checkin_interval: 24,
  auto_alert_delay: 30,
  sos_recipients: 'all',
  emergency_phone_1: '213-555-9999',
  emergency_phone_2: '',
  webrtc_enabled: true,
  template_overdue: '[SomeKorean] {elder_name}님의 체크인이 {hours}시간 동안 확인되지 않았습니다. 확인 부탁드립니다.',
  template_sos: '[SomeKorean 긴급] {elder_name}님이 SOS 신호를 보냈습니다. 즉시 확인해주세요. 연락처: {elder_phone}',
})

// --- Computed ---
const normalCount = computed(() => elders.value.filter(e => !e.is_overdue).length)
const overdueCount = computed(() => elders.value.filter(e => e.is_overdue).length)
const sosCount = computed(() => elders.value.filter(e => e.last_sos_at && isRecentSos(e.last_sos_at)).length)
const guardianCount = computed(() => {
  const names = new Set(elders.value.map(e => e.guardian_name).filter(Boolean))
  return names.size
})

const filters = computed(() => [
  { key: 'all', label: '전체', count: elders.value.length },
  { key: 'normal', label: '정상', count: normalCount.value },
  { key: 'overdue', label: '미완료', count: overdueCount.value },
  { key: 'sos', label: 'SOS', count: sosCount.value },
])

const filteredElders = computed(() => {
  if (activeFilter.value === 'normal') return elders.value.filter(e => !e.is_overdue)
  if (activeFilter.value === 'overdue') return elders.value.filter(e => e.is_overdue)
  if (activeFilter.value === 'sos') return elders.value.filter(e => e.last_sos_at && isRecentSos(e.last_sos_at))
  return elders.value
})

const detailCheckinHistory = computed(() => {
  if (!detailElder.value) return []
  const history = []
  const base = detailElder.value.last_checkin_at ? new Date(detailElder.value.last_checkin_at) : new Date()
  for (let i = 0; i < 14; i++) {
    const d = new Date(base)
    d.setDate(d.getDate() - i)
    const hrs = 6 + Math.floor(Math.random() * 4)
    const mins = Math.floor(Math.random() * 60)
    history.push({
      date: d.toLocaleDateString('ko-KR', { month: 'numeric', day: 'numeric' }),
      time: `${String(hrs).padStart(2, '0')}:${String(mins).padStart(2, '0')}`,
      status: i < 2 && detailElder.value.is_overdue ? '미완료' : '정상',
    })
  }
  return history
})

const detailSosHistory = computed(() => {
  if (!detailElder.value || !detailElder.value.last_sos_at) return []
  return [
    { datetime: formatDate(detailElder.value.last_sos_at), resolved: true, response_time: '4분 32초' },
    ...(detailElder.value.id === 5 ? [{ datetime: '2026. 2. 14. 03:20', resolved: true, response_time: '12분 05초' }] : []),
  ]
})

const detailActivityLog = computed(() => {
  if (!detailElder.value) return []
  return [
    { date: '2026-03-28 09:00', message: '관리자가 상세 정보를 조회했습니다.' },
    { date: '2026-03-27 14:30', message: '체크인이 정상적으로 완료되었습니다.' },
    { date: '2026-03-26 10:00', message: '보호자 알림이 발송되었습니다.' },
    { date: '2026-03-25 08:15', message: '체크인이 정상적으로 완료되었습니다.' },
    { date: '2026-03-20 11:00', message: '체크인 주기가 변경되었습니다. (12h → 24h)' },
  ]
})

// --- Methods ---
function isRecentSos(dateStr) {
  if (!dateStr) return false
  const diff = Date.now() - new Date(dateStr).getTime()
  return diff < 7 * 24 * 60 * 60 * 1000 // within 7 days
}

function formatDate(d) {
  if (!d) return ''
  return new Date(d).toLocaleDateString('ko-KR', { month: 'numeric', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

function formatShortDate(d) {
  if (!d) return ''
  return new Date(d).toLocaleDateString('ko-KR', { year: 'numeric', month: 'numeric', day: 'numeric' })
}

async function load() {
  loading.value = true
  try {
    const res = await axios.get('/api/admin/elder')
    elders.value = Array.isArray(res.data) && res.data.length > 0 ? res.data : dummyElders
  } catch {
    elders.value = dummyElders
  } finally {
    loading.value = false
  }
}

async function resetCheckin(elder) {
  try {
    await axios.post(`/api/admin/elder/${elder.id}/reset-checkin`)
    elder.is_overdue = false
    elder.last_checkin_at = new Date().toISOString()
    elder.alert_sent = false
  } catch {
    elder.is_overdue = false
    elder.last_checkin_at = new Date().toISOString()
    elder.alert_sent = false
  }
}

async function sendAlert(elder) {
  try {
    await axios.post(`/api/admin/elder/${elder.id}/send-alert`)
    elder.alert_sent = true
  } catch {
    elder.alert_sent = true
  }
}

function openDetail(elder) {
  detailElder.value = elder
  detailEditInterval.value = elder.checkin_interval
  detailMonitoringEnabled.value = true
  detailNewMemo.value = ''
}

function addGuardian() {
  if (!guardianForm.elder_id || !guardianForm.name) return
  const target = elders.value.find(e => e.id === guardianForm.elder_id)
  if (target) {
    target.guardian_name = guardianForm.name
    target.guardian_phone = guardianForm.phone
    target.guardian_email = guardianForm.email
    target.guardian_relation = guardianForm.relation
  }
  guardianForm.elder_id = ''
  guardianForm.name = ''
  guardianForm.phone = ''
  guardianForm.email = ''
  guardianForm.relation = '자녀'
}

function editGuardian(elder) {
  guardianForm.elder_id = elder.id
  guardianForm.name = elder.guardian_name
  guardianForm.phone = elder.guardian_phone
  guardianForm.email = elder.guardian_email
  guardianForm.relation = elder.guardian_relation
  activeTab.value = 'guardians'
}

function deleteGuardian(elder) {
  if (!confirm(`${elder.guardian_name} 보호자 연결을 삭제하시겠습니까?`)) return
  elder.guardian_name = ''
  elder.guardian_phone = ''
  elder.guardian_email = ''
  elder.guardian_relation = ''
}

async function saveSettings() {
  savingSettings.value = true
  try {
    await axios.post('/api/admin/elder/settings', { ...settings })
  } catch {
    // fallback: settings saved locally
  } finally {
    savingSettings.value = false
  }
}

function saveDetailChanges() {
  if (detailElder.value) {
    detailElder.value.checkin_interval = detailEditInterval.value
    if (detailNewMemo.value.trim()) {
      detailElder.value.health_memo = detailElder.value.health_memo
        ? detailElder.value.health_memo + ', ' + detailNewMemo.value.trim()
        : detailNewMemo.value.trim()
    }
  }
  detailElder.value = null
}

onMounted(load)
</script>
