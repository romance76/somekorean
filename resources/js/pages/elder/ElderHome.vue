<template>
  <div class="min-h-screen bg-gray-50 pb-24">
    <div class="max-w-[800px] mx-auto px-4 pt-4">
    <!-- Header Banner -->
    <div class="bg-gradient-to-r from-blue-600 to-blue-800 text-white px-6 py-6 rounded-2xl shadow-lg">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-black flex items-center gap-2">안심서비스</h1>
          <p class="text-base opacity-80 mt-1">매일 체크인으로 보호자에게 안전 알림</p>
        </div>
        <button
          @click="showSettingsModal = true"
          class="bg-white bg-opacity-20 hover:bg-opacity-30 rounded-xl px-4 py-2 text-base font-bold transition"
        >
          설정
        </button>
      </div>
    </div>
    </div>

    <div class="max-w-[800px] mx-auto px-4 mt-6 space-y-5">
      <!-- Greeting + Date/Time -->
      <div class="bg-white rounded-2xl shadow-md p-6 text-center">
        <p class="text-3xl font-bold text-gray-800 mb-2">
          안녕하세요, {{ auth.user?.name || auth.user?.nickname || '회원' }}님
        </p>
        <p class="text-xl text-gray-500">{{ currentDateTime }}</p>
      </div>

      <!-- Card 1: Checkin -->
      <div class="bg-white rounded-2xl shadow-md p-6 text-center">
        <div v-if="todayCheckedIn" class="mb-3">
          <p class="text-green-600 font-bold text-xl mb-1">오늘 체크인 완료!</p>
          <p class="text-lg text-gray-500">{{ formatTime(settings.last_checkin_at) }}</p>
        </div>
        <router-link
          to="/elder/checkin"
          class="block w-full text-center font-bold text-xl py-5 rounded-2xl transition shadow-md"
          :class="todayCheckedIn
            ? 'bg-green-100 text-green-700 hover:bg-green-200'
            : 'bg-green-500 hover:bg-green-600 text-white'"
        >
          {{ todayCheckedIn ? '오늘도 안전합니다' : '체크인 하러 가기' }}
        </router-link>
        <p v-if="!todayCheckedIn" class="text-base text-gray-400 mt-3">매일 체크인하면 포인트 5점 적립</p>
        <p v-if="settings.last_checkin_at && !todayCheckedIn" class="text-base text-gray-400 mt-1">
          마지막 체크인: {{ formatTime(settings.last_checkin_at) }}
        </p>
      </div>

      <!-- Card 2: SOS Emergency -->
      <div class="bg-white rounded-2xl shadow-md p-6 text-center">
        <h2 class="text-xl font-bold text-red-600 mb-2">긴급 SOS</h2>
        <p class="text-lg text-gray-500 mb-4">3초 꾹 누르면 보호자에게 긴급 연락</p>

        <!-- SOS Button -->
        <div class="flex justify-center mb-4">
          <div class="relative">
            <!-- Progress ring -->
            <svg class="w-36 h-36 transform -rotate-90" viewBox="0 0 120 120">
              <circle cx="60" cy="60" r="54" fill="none" stroke="#fee2e2" stroke-width="8" />
              <circle
                cx="60" cy="60" r="54" fill="none"
                stroke="#ef4444" stroke-width="8"
                stroke-linecap="round"
                :stroke-dasharray="339.292"
                :stroke-dashoffset="339.292 - (339.292 * sosProgress / 100)"
                class="transition-all duration-100"
              />
            </svg>
            <button
              class="absolute inset-0 m-auto w-28 h-28 rounded-full bg-red-600 hover:bg-red-700 text-white font-bold text-3xl shadow-lg active:scale-95 transition select-none"
              @mousedown="startSOS"
              @mouseup="cancelSOS"
              @mouseleave="cancelSOS"
              @touchstart.prevent="startSOS"
              @touchend.prevent="cancelSOS"
              @touchcancel.prevent="cancelSOS"
            >
              SOS
            </button>
          </div>
        </div>

        <!-- SOS Active State -->
        <div v-if="sosActive" class="bg-red-50 border border-red-200 rounded-xl p-4 mt-3">
          <p class="text-red-700 font-bold text-xl">SOS 발동됨!</p>
          <p class="text-red-600 text-lg">보호자에게 알림이 전송되었습니다</p>
          <p v-if="sosLocation" class="text-gray-500 text-base mt-1">
            위치: {{ sosLocation.lat.toFixed(5) }}, {{ sosLocation.lng.toFixed(5) }}
          </p>
          <p class="text-gray-500 text-base">시간: {{ sosTime }}</p>
          <button
            v-if="sosCancelable"
            @click="cancelSOSAlert"
            class="mt-3 bg-gray-500 hover:bg-gray-600 text-white font-bold py-3 px-8 rounded-xl text-lg"
          >
            취소 ({{ sosCancelCountdown }}초)
          </button>
        </div>
      </div>

      <!-- Card 3: Health Record -->
      <div class="bg-white rounded-2xl shadow-md p-6">
        <h2 class="text-xl font-bold text-gray-800 mb-4">건강 기록</h2>
        <div class="grid grid-cols-2 gap-3 mb-4">
          <div>
            <label class="block text-lg text-gray-600 mb-1">혈압 (수축기)</label>
            <input
              v-model.number="healthForm.blood_pressure_systolic"
              type="number"
              placeholder="120"
              class="w-full border border-gray-300 rounded-xl px-4 py-3 text-lg focus:ring-2 focus:ring-blue-400 focus:border-blue-400"
            />
          </div>
          <div>
            <label class="block text-lg text-gray-600 mb-1">혈압 (이완기)</label>
            <input
              v-model.number="healthForm.blood_pressure_diastolic"
              type="number"
              placeholder="80"
              class="w-full border border-gray-300 rounded-xl px-4 py-3 text-lg focus:ring-2 focus:ring-blue-400 focus:border-blue-400"
            />
          </div>
          <div>
            <label class="block text-lg text-gray-600 mb-1">혈당 (mg/dL)</label>
            <input
              v-model.number="healthForm.blood_sugar"
              type="number"
              placeholder="100"
              class="w-full border border-gray-300 rounded-xl px-4 py-3 text-lg focus:ring-2 focus:ring-blue-400 focus:border-blue-400"
            />
          </div>
          <div>
            <label class="block text-lg text-gray-600 mb-1">체중 (kg)</label>
            <input
              v-model.number="healthForm.weight"
              type="number"
              step="0.1"
              placeholder="65"
              class="w-full border border-gray-300 rounded-xl px-4 py-3 text-lg focus:ring-2 focus:ring-blue-400 focus:border-blue-400"
            />
          </div>
        </div>
        <button
          @click="saveHealthRecord"
          :disabled="healthSaving"
          class="w-full bg-blue-500 hover:bg-blue-600 disabled:bg-blue-300 text-white font-bold text-lg py-4 rounded-xl transition"
        >
          {{ healthSaving ? '저장 중...' : '기록하기' }}
        </button>
        <p v-if="healthSaveMsg" class="text-center text-green-600 font-bold text-lg mt-2">{{ healthSaveMsg }}</p>

        <!-- Recent Health Records -->
        <div v-if="recentHealthRecords.length" class="mt-5 border-t pt-4">
          <h3 class="text-lg font-bold text-gray-700 mb-3">최근 기록</h3>
          <div class="space-y-2">
            <div
              v-for="record in recentHealthRecords.slice(0, 5)"
              :key="record.id"
              class="flex items-center justify-between bg-gray-50 rounded-xl px-4 py-3"
            >
              <span class="text-base text-gray-600">{{ formatDate(record.recorded_at) }}</span>
              <div class="flex gap-3 text-base">
                <span v-if="record.blood_pressure_systolic" class="text-red-600">
                  {{ record.blood_pressure_systolic }}/{{ record.blood_pressure_diastolic }}
                </span>
                <span v-if="record.blood_sugar" class="text-purple-600">
                  {{ record.blood_sugar }}mg
                </span>
                <span v-if="record.weight" class="text-blue-600">
                  {{ record.weight }}kg
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Card 4: Medication Reminders -->
      <div class="bg-white rounded-2xl shadow-md p-6">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-xl font-bold text-gray-800">복약 알림</h2>
          <button
            @click="showMedicationModal = true"
            class="bg-blue-100 hover:bg-blue-200 text-blue-700 font-bold text-base px-4 py-2 rounded-xl transition"
          >
            + 알림 추가
          </button>
        </div>

        <div v-if="medications.length === 0" class="text-center py-4 text-gray-400 text-lg">
          등록된 복약 알림이 없습니다
        </div>
        <div v-else class="space-y-3">
          <div
            v-for="med in medications"
            :key="med.id"
            class="flex items-center justify-between bg-gray-50 rounded-xl px-4 py-4"
          >
            <div class="flex items-center gap-3">
              <span class="text-2xl">{{ isMedicationTaken(med.id) ? '&#x2705;' : '&#x1F48A;' }}</span>
              <div>
                <p class="text-lg font-bold text-gray-800">{{ med.name }}</p>
                <p class="text-base text-gray-500">{{ med.time }} | {{ formatDays(med.days) }}</p>
              </div>
            </div>
            <div class="flex items-center gap-2">
              <button
                v-if="!isMedicationTaken(med.id)"
                @click="takeMedication(med.id)"
                class="bg-green-500 hover:bg-green-600 text-white font-bold text-base px-4 py-2 rounded-xl transition"
              >
                복용 완료
              </button>
              <span v-else class="text-green-600 font-bold text-base">복용함</span>
              <button
                @click="removeMedication(med.id)"
                class="text-red-400 hover:text-red-600 text-xl ml-2"
              >
                &times;
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Card 5: Guardian Settings -->
      <div class="bg-white rounded-2xl shadow-md p-6">
        <h2 class="text-xl font-bold text-gray-800 mb-3">보호자 설정</h2>
        <div v-if="settings.guardian_name" class="space-y-2">
          <div class="flex items-center gap-2">
            <span class="text-green-500 text-lg">&#x25CF;</span>
            <span class="text-lg text-gray-700">{{ settings.guardian_name }} ({{ settings.guardian_phone }})</span>
          </div>
          <div v-if="settings.guardian2_name" class="flex items-center gap-2">
            <span class="text-blue-500 text-lg">&#x25CF;</span>
            <span class="text-lg text-gray-700">{{ settings.guardian2_name }} ({{ settings.guardian2_phone }})</span>
          </div>
        </div>
        <div v-else class="text-gray-400 text-lg mb-3">
          보호자가 설정되지 않았습니다
        </div>
        <button
          @click="showSettingsModal = true"
          class="mt-3 w-full bg-blue-500 hover:bg-blue-600 text-white font-bold text-lg py-4 rounded-xl transition"
        >
          설정 변경
        </button>
      </div>

      <!-- Card 6: Guardian Dashboard Link -->
      <div class="bg-white rounded-2xl shadow-md p-6">
        <h2 class="text-xl font-bold text-gray-800 mb-2">보호자 대시보드</h2>
        <p class="text-lg text-gray-500 mb-4">가족의 안전 상태를 확인하세요</p>
        <router-link
          to="/elder/guardian"
          class="block w-full text-center bg-indigo-500 hover:bg-indigo-600 text-white font-bold text-lg py-4 rounded-xl transition"
        >
          보호자 화면 보기
        </router-link>
      </div>

      <!-- Card 7: Checkin Calendar (30 days) -->
      <div class="bg-white rounded-2xl shadow-md p-6">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-xl font-bold text-gray-800">체크인 달력</h2>
          <span v-if="streakDays > 0" class="text-orange-500 font-bold text-lg">
            연속 {{ streakDays }}일
          </span>
        </div>
        <div class="grid grid-cols-7 gap-1 text-center text-base mb-2">
          <span v-for="d in ['일','월','화','수','목','금','토']" :key="d" class="text-gray-400 font-medium py-1">{{ d }}</span>
        </div>
        <div class="grid grid-cols-7 gap-1 text-center">
          <!-- empty slots for alignment -->
          <span v-for="n in calendarStartOffset" :key="'e'+n"></span>
          <span
            v-for="day in calendarDays"
            :key="day.date"
            class="py-2 rounded-lg text-base"
            :class="{
              'bg-green-100 text-green-700': day.status === 'checked',
              'bg-red-100 text-red-600': day.status === 'missed',
              'bg-gray-50 text-gray-300': day.status === 'future',
            }"
            :title="day.date"
          >
            {{ day.day }}
          </span>
        </div>
      </div>

      <!-- Card 8: Senior Community Preview -->
      <div class="bg-white rounded-2xl shadow-md p-6">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-xl font-bold text-gray-800">시니어 커뮤니티</h2>
          <router-link to="/board/senior" class="text-blue-500 font-bold text-base hover:underline">
            더보기 &rarr;
          </router-link>
        </div>
        <div v-if="communityPosts.length === 0" class="text-center py-4 text-gray-400 text-lg">
          아직 글이 없습니다
        </div>
        <div v-else class="space-y-3">
          <router-link
            v-for="post in communityPosts.slice(0, 3)"
            :key="post.id"
            :to="`/board/senior/${post.id}`"
            class="block bg-gray-50 hover:bg-blue-50 rounded-xl px-4 py-3 transition"
          >
            <p class="text-lg font-medium text-gray-800 truncate">{{ post.title }}</p>
            <p class="text-base text-gray-400 mt-1">{{ formatDate(post.created_at) }}</p>
          </router-link>
        </div>
      </div>
    </div>

    <!-- Settings Modal -->
    <div v-if="showSettingsModal" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-end sm:items-center justify-center p-4">
      <div class="bg-white rounded-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <div class="sticky top-0 bg-white px-6 py-4 border-b flex items-center justify-between rounded-t-2xl">
          <h2 class="text-xl font-bold">설정</h2>
          <button @click="showSettingsModal = false" class="text-gray-400 hover:text-gray-600 text-2xl">&times;</button>
        </div>
        <div class="p-6 space-y-5">
          <!-- Guardian 1 -->
          <div>
            <h3 class="font-bold text-lg text-gray-800 mb-2">보호자 1 (필수)</h3>
            <div class="space-y-3">
              <div>
                <label class="block text-base text-gray-600 mb-1">이름</label>
                <input v-model="form.guardian_name" type="text" class="w-full border border-gray-300 rounded-xl px-4 py-3 text-lg focus:ring-2 focus:ring-blue-400 focus:border-blue-400" placeholder="보호자 이름" />
              </div>
              <div>
                <label class="block text-base text-gray-600 mb-1">전화번호</label>
                <input v-model="form.guardian_phone" type="tel" class="w-full border border-gray-300 rounded-xl px-4 py-3 text-lg focus:ring-2 focus:ring-blue-400 focus:border-blue-400" placeholder="010-0000-0000" />
              </div>
            </div>
          </div>

          <!-- Guardian 2 -->
          <div>
            <h3 class="font-bold text-lg text-gray-800 mb-2">보호자 2 (선택)</h3>
            <div class="space-y-3">
              <div>
                <label class="block text-base text-gray-600 mb-1">이름</label>
                <input v-model="form.guardian2_name" type="text" class="w-full border border-gray-300 rounded-xl px-4 py-3 text-lg focus:ring-2 focus:ring-blue-400 focus:border-blue-400" placeholder="2차 보호자 이름" />
              </div>
              <div>
                <label class="block text-base text-gray-600 mb-1">전화번호</label>
                <input v-model="form.guardian2_phone" type="tel" class="w-full border border-gray-300 rounded-xl px-4 py-3 text-lg focus:ring-2 focus:ring-blue-400 focus:border-blue-400" placeholder="010-0000-0000" />
              </div>
            </div>
          </div>

          <!-- Search member as guardian -->
          <div>
            <h3 class="font-bold text-lg text-gray-800 mb-2">사이트 회원 중 보호자 검색</h3>
            <div class="flex gap-2">
              <input
                v-model="guardianSearch"
                type="text"
                class="flex-1 border border-gray-300 rounded-xl px-4 py-3 text-lg focus:ring-2 focus:ring-blue-400 focus:border-blue-400"
                placeholder="이메일 또는 닉네임"
                @input="searchGuardian"
              />
            </div>
            <ul v-if="guardianResults.length" class="mt-2 border rounded-xl overflow-hidden">
              <li
                v-for="u in guardianResults"
                :key="u.id"
                class="flex items-center justify-between px-4 py-3 border-b last:border-b-0 hover:bg-blue-50 cursor-pointer"
                @click="selectGuardian(u)"
              >
                <span class="text-base">{{ u.name }} ({{ u.email }})</span>
                <button class="text-blue-500 font-bold text-sm">선택</button>
              </li>
            </ul>
          </div>

          <!-- Checkin time -->
          <div>
            <label class="block font-bold text-lg text-gray-800 mb-2">체크인 시간</label>
            <select v-model="form.checkin_time" class="w-full border border-gray-300 rounded-xl px-4 py-3 text-lg focus:ring-2 focus:ring-blue-400 focus:border-blue-400">
              <option v-for="h in checkinHours" :key="h.value" :value="h.value">{{ h.label }}</option>
            </select>
          </div>

          <!-- Timezone -->
          <div>
            <label class="block font-bold text-lg text-gray-800 mb-2">시간대</label>
            <select v-model="form.timezone" class="w-full border border-gray-300 rounded-xl px-4 py-3 text-lg focus:ring-2 focus:ring-blue-400 focus:border-blue-400">
              <option value="America/New_York">동부시간 (ET)</option>
              <option value="America/Chicago">중부시간 (CT)</option>
              <option value="America/Denver">산악시간 (MT)</option>
              <option value="America/Los_Angeles">태평양시간 (PT)</option>
              <option value="Pacific/Honolulu">하와이시간 (HT)</option>
              <option value="America/Anchorage">알래스카시간 (AKT)</option>
              <option value="Asia/Seoul">한국시간 (KST)</option>
            </select>
          </div>

          <!-- Toggles -->
          <div class="space-y-3">
            <label class="flex items-center justify-between">
              <span class="text-lg text-gray-700">체크인 알림</span>
              <button
                @click="form.checkin_enabled = !form.checkin_enabled"
                class="relative w-14 h-8 rounded-full transition"
                :class="form.checkin_enabled ? 'bg-blue-500' : 'bg-gray-300'"
              >
                <span
                  class="absolute top-1 left-1 w-6 h-6 bg-white rounded-full shadow transition-transform"
                  :class="form.checkin_enabled ? 'translate-x-6' : ''"
                ></span>
              </button>
            </label>
            <label class="flex items-center justify-between">
              <span class="text-lg text-gray-700">SOS 기능</span>
              <button
                @click="form.sos_enabled = !form.sos_enabled"
                class="relative w-14 h-8 rounded-full transition"
                :class="form.sos_enabled ? 'bg-red-500' : 'bg-gray-300'"
              >
                <span
                  class="absolute top-1 left-1 w-6 h-6 bg-white rounded-full shadow transition-transform"
                  :class="form.sos_enabled ? 'translate-x-6' : ''"
                ></span>
              </button>
            </label>
          </div>

          <!-- Save -->
          <button
            @click="saveSettings"
            :disabled="saving"
            class="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white font-bold text-lg py-4 rounded-xl transition"
          >
            {{ saving ? '저장 중...' : '설정 저장' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Medication Add Modal -->
    <div v-if="showMedicationModal" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-end sm:items-center justify-center p-4">
      <div class="bg-white rounded-2xl w-full max-w-md">
        <div class="px-6 py-4 border-b flex items-center justify-between rounded-t-2xl">
          <h2 class="text-xl font-bold">복약 알림 추가</h2>
          <button @click="showMedicationModal = false" class="text-gray-400 hover:text-gray-600 text-2xl">&times;</button>
        </div>
        <div class="p-6 space-y-4">
          <div>
            <label class="block text-lg text-gray-600 mb-1">약 이름</label>
            <input
              v-model="medForm.name"
              type="text"
              placeholder="예: 혈압약"
              class="w-full border border-gray-300 rounded-xl px-4 py-3 text-lg focus:ring-2 focus:ring-blue-400 focus:border-blue-400"
            />
          </div>
          <div>
            <label class="block text-lg text-gray-600 mb-1">복용 시간</label>
            <input
              v-model="medForm.time"
              type="time"
              class="w-full border border-gray-300 rounded-xl px-4 py-3 text-lg focus:ring-2 focus:ring-blue-400 focus:border-blue-400"
            />
          </div>
          <div>
            <label class="block text-lg text-gray-600 mb-2">복용 요일</label>
            <div class="flex gap-2 flex-wrap">
              <button
                v-for="day in allDays"
                :key="day.value"
                @click="toggleMedDay(day.value)"
                class="px-4 py-2 rounded-xl text-base font-bold border-2 transition"
                :class="medForm.days.includes(day.value) ? 'bg-blue-500 text-white border-blue-500' : 'bg-white text-gray-600 border-gray-300'"
              >
                {{ day.label }}
              </button>
            </div>
          </div>
          <button
            @click="saveMedication"
            :disabled="medSaving || !medForm.name || !medForm.time"
            class="w-full bg-green-500 hover:bg-green-600 disabled:bg-green-300 text-white font-bold text-lg py-4 rounded-xl transition"
          >
            {{ medSaving ? '저장 중...' : '알림 추가' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Call Message -->
    <div v-if="callMessage" class="fixed top-4 left-1/2 -translate-x-1/2 z-40 bg-blue-600 text-white px-6 py-3 rounded-xl shadow-lg text-lg font-bold">
      {{ callMessage }}
    </div>

    <!-- WebRTC Call Modal -->
    <CallModal
      :callState="callState"
      :callType="callType"
      :callDuration="callDuration"
      :localStream="localStream"
      :remoteStream="remoteStream"
      :remoteUser="remoteUser"
      :isMuted="isMuted"
      :isVideoOff="isVideoOff"
      :formatDuration="formatDuration"
      @answerCall="answerCall"
      @rejectCall="rejectCall"
      @endCall="endCall"
      @toggleMute="toggleMute"
      @toggleVideo="toggleVideo"
    />

    <!-- SOS Confirm Modal -->
    <div v-if="showSOSConfirm" class="fixed inset-0 bg-black bg-opacity-60 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-2xl w-full max-w-sm p-6 text-center">
        <p class="text-5xl mb-3">&#x1F6A8;</p>
        <h2 class="text-2xl font-bold text-red-600 mb-2">긴급상황인가요?</h2>
        <p class="text-lg text-gray-600 mb-6">보호자에게 긴급 알림이 전송됩니다</p>
        <div class="flex gap-3">
          <button
            @click="showSOSConfirm = false"
            class="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-700 font-bold text-lg py-4 rounded-xl"
          >
            아니요
          </button>
          <button
            @click="confirmSOS"
            class="flex-1 bg-red-600 hover:bg-red-700 text-white font-bold text-lg py-4 rounded-xl"
          >
            네, 긴급이에요!
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '../../stores/auth'
import axios from 'axios'
import { useSocket } from '../../composables/useSocket'
import { useWebRTC } from '../../composables/useWebRTC'
import CallModal from '../../components/CallModal.vue'
import { usePushNotification } from '../../composables/usePushNotification'

const auth = useAuthStore()
const { subscribe: pushSubscribe, requestPermission } = usePushNotification()
const token = localStorage.getItem('sk_token')
const headers = { Authorization: `Bearer ${token}` }

// State
const settings = reactive({
  elder_mode: false,
  guardian_name: '',
  guardian_phone: '',
  guardian2_name: '',
  guardian2_phone: '',
  checkin_time: '09:00',
  checkin_enabled: true,
  sos_enabled: true,
  last_checkin_at: null,
  missed_count: 0,
  recent_logs: [],
  timezone: 'America/New_York',
  medication_times: '[]',
})
const loading = ref(true)
const showSettingsModal = ref(false)
const saving = ref(false)

// Settings form
const form = reactive({
  guardian_name: '',
  guardian_phone: '',
  guardian2_name: '',
  guardian2_phone: '',
  checkin_time: '09:00',
  checkin_enabled: true,
  sos_enabled: true,
  timezone: 'America/New_York',
})

// Guardian search
const guardianSearch = ref('')
const guardianResults = ref([])
let searchTimeout = null

// SOS
const sosProgress = ref(0)
const sosActive = ref(false)
const sosLocation = ref(null)
const sosTime = ref('')
const showSOSConfirm = ref(false)
const sosCancelable = ref(false)
const sosCancelCountdown = ref(10)
let sosTimer = null
let sosProgressInterval = null
let sosCancelTimer = null
let sosCancelInterval = null

// Health Records
const healthForm = reactive({
  blood_pressure_systolic: null,
  blood_pressure_diastolic: null,
  blood_sugar: null,
  weight: null,
})
const healthSaving = ref(false)
const healthSaveMsg = ref('')
const recentHealthRecords = ref([])

// Medications
const medications = ref([])
const takenMedications = ref(new Set())
const showMedicationModal = ref(false)
const medForm = reactive({ name: '', time: '09:00', days: ['mon','tue','wed','thu','fri','sat','sun'] })
const medSaving = ref(false)
const allDays = [
  { value: 'mon', label: '월' },
  { value: 'tue', label: '화' },
  { value: 'wed', label: '수' },
  { value: 'thu', label: '목' },
  { value: 'fri', label: '금' },
  { value: 'sat', label: '토' },
  { value: 'sun', label: '일' },
]

// Community posts
const communityPosts = ref([])

// WebRTC & Socket
const { isConnected: socketConnected, connect: socketConnect, emit: socketEmit, on: socketOn, off: socketOff, socket: getSocket } = useSocket()
const {
  localStream, remoteStream, peerConnection,
  callState, callType, callDuration,
  isMuted, isVideoOff, remoteUser,
  setSocket, setupSocketListeners, removeSocketListeners,
  startCall, answerCall, rejectCall, endCall,
  toggleMute, toggleVideo, formatDuration,
} = useWebRTC()
const guardianOnline = ref(false)
const callMessage = ref('')

// Calendar
const checkinHistory = ref([])
const streakDays = ref(0)

// Current date/time
const currentDateTime = ref('')
let clockInterval = null

function updateClock() {
  const now = new Date()
  currentDateTime.value = now.toLocaleDateString('ko-KR', {
    year: 'numeric', month: 'long', day: 'numeric', weekday: 'long',
  }) + ' ' + now.toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' })
}

// Computed
const todayCheckedIn = computed(() => {
  if (!settings.last_checkin_at) return false
  const today = new Date().toISOString().slice(0, 10)
  const last = new Date(settings.last_checkin_at).toISOString().slice(0, 10)
  return today === last
})

const checkinHours = computed(() => {
  const hours = []
  for (let h = 6; h <= 22; h++) {
    const label = h < 12 ? `오전 ${h}시` : h === 12 ? '오후 12시' : `오후 ${h - 12}시`
    hours.push({ value: `${String(h).padStart(2, '0')}:00`, label })
  }
  return hours
})

const calendarDays = computed(() => {
  const days = []
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const checkedDates = new Set(
    checkinHistory.value.map(h => new Date(h.checked_at || h.created_at).toISOString().slice(0, 10))
  )
  for (let i = 29; i >= 0; i--) {
    const d = new Date(today)
    d.setDate(d.getDate() - i)
    const dateStr = d.toISOString().slice(0, 10)
    let status = 'future'
    if (d <= today) {
      status = checkedDates.has(dateStr) ? 'checked' : 'missed'
    }
    if (d.toDateString() === today.toDateString() && !checkedDates.has(dateStr)) {
      status = 'future' // today not yet missed
    }
    days.push({ date: dateStr, day: d.getDate(), status })
  }
  return days
})

const calendarStartOffset = computed(() => {
  if (!calendarDays.value.length) return 0
  const firstDate = new Date(calendarDays.value[0].date)
  return firstDate.getDay()
})

// Methods
function formatTime(dt) {
  if (!dt) return ''
  const d = new Date(dt)
  return d.toLocaleString('ko-KR', { month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

function formatDate(dt) {
  if (!dt) return ''
  const d = new Date(dt)
  return d.toLocaleDateString('ko-KR', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

function formatDays(days) {
  if (!days || !days.length) return '매일'
  const dayMap = { mon: '월', tue: '화', wed: '수', thu: '목', fri: '금', sat: '토', sun: '일' }
  if (days.length === 7) return '매일'
  return days.map(d => dayMap[d] || d).join(', ')
}

function isMedicationTaken(medId) {
  return takenMedications.value.has(medId)
}

async function loadSettings() {
  try {
    const { data } = await axios.get('/api/elder/settings', { headers })
    const s = data.settings || data
    Object.assign(settings, s)
    if (data.recent_logs) settings.recent_logs = data.recent_logs
    Object.assign(form, {
      guardian_name: s.guardian_name || '',
      guardian_phone: s.guardian_phone || '',
      guardian2_name: s.guardian2_name || '',
      guardian2_phone: s.guardian2_phone || '',
      checkin_time: s.checkin_time || '09:00',
      checkin_enabled: s.checkin_enabled ?? true,
      sos_enabled: s.sos_enabled ?? true,
      timezone: s.timezone || 'America/New_York',
    })
    // Load medications from settings
    try {
      const meds = JSON.parse(s.medication_times || '[]')
      medications.value = Array.isArray(meds) ? meds : []
    } catch (e) {
      medications.value = []
    }
  } catch (e) {
    console.error('Failed to load elder settings', e)
  } finally {
    loading.value = false
  }
}

async function loadCheckinHistory() {
  try {
    const { data } = await axios.get('/api/elder/checkin-history', { headers })
    checkinHistory.value = data.data || data.logs || data || []
    calculateStreak()
  } catch (e) {
    console.error('Failed to load checkin history', e)
  }
}

async function loadHealthRecords() {
  try {
    const { data } = await axios.get('/api/elder/health-records', { headers })
    recentHealthRecords.value = data.data || data || []
  } catch (e) {
    console.error('Failed to load health records', e)
  }
}

async function loadMedicationLogs() {
  try {
    const { data } = await axios.get('/api/elder/medications', { headers })
    const todayLogs = data.today_logs || []
    takenMedications.value = new Set(todayLogs.map(l => l.medication_id))
  } catch (e) {
    console.error('Failed to load medication logs', e)
  }
}

async function loadCommunityPosts() {
  try {
    const { data } = await axios.get('/api/posts', { headers, params: { board: 'senior', per_page: 3 } })
    communityPosts.value = data.data || data || []
  } catch (e) {
    // Silently fail - community posts are not critical
  }
}

function calculateStreak() {
  const checkedDates = new Set(
    checkinHistory.value.map(h => new Date(h.checked_at || h.created_at).toISOString().slice(0, 10))
  )
  let streak = 0
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  for (let i = 0; i < 365; i++) {
    const d = new Date(today)
    d.setDate(d.getDate() - i)
    const dateStr = d.toISOString().slice(0, 10)
    if (checkedDates.has(dateStr)) {
      streak++
    } else if (i > 0) {
      break
    }
  }
  streakDays.value = streak
}

async function saveSettings() {
  saving.value = true
  try {
    await axios.put('/api/elder/settings', { ...form }, { headers: { ...headers, 'Content-Type': 'application/json' } })
    Object.assign(settings, form)
    showSettingsModal.value = false
  } catch (e) {
    alert('설정 저장에 실패했습니다')
  } finally {
    saving.value = false
  }
}

async function searchGuardian() {
  clearTimeout(searchTimeout)
  if (guardianSearch.value.length < 2) {
    guardianResults.value = []
    return
  }
  searchTimeout = setTimeout(async () => {
    try {
      const { data } = await axios.get('/api/elder/guardian-search', {
        headers,
        params: { q: guardianSearch.value }
      })
      guardianResults.value = data.data || data || []
    } catch (e) {
      guardianResults.value = []
    }
  }, 300)
}

async function selectGuardian(user) {
  try {
    await axios.post('/api/elder/link-guardian', { guardian_user_id: user.id }, { headers })
    form.guardian_name = user.name
    form.guardian_phone = user.phone || ''
    guardianSearch.value = ''
    guardianResults.value = []
  } catch (e) {
    alert('보호자 연결에 실패했습니다')
  }
}

// Health Records
async function saveHealthRecord() {
  if (!healthForm.blood_pressure_systolic && !healthForm.blood_sugar && !healthForm.weight) {
    alert('최소 하나의 항목을 입력해주세요')
    return
  }
  healthSaving.value = true
  healthSaveMsg.value = ''
  try {
    await axios.post('/api/elder/health-record', { ...healthForm }, { headers })
    healthSaveMsg.value = '저장되었습니다!'
    setTimeout(() => { healthSaveMsg.value = '' }, 3000)
    // Reset form
    healthForm.blood_pressure_systolic = null
    healthForm.blood_pressure_diastolic = null
    healthForm.blood_sugar = null
    healthForm.weight = null
    // Reload records
    loadHealthRecords()
  } catch (e) {
    alert('건강 기록 저장에 실패했습니다')
  } finally {
    healthSaving.value = false
  }
}

// Medications
function toggleMedDay(day) {
  const idx = medForm.days.indexOf(day)
  if (idx >= 0) medForm.days.splice(idx, 1)
  else medForm.days.push(day)
}

async function saveMedication() {
  medSaving.value = true
  try {
    await axios.post('/api/elder/medications', {
      name: medForm.name,
      time: medForm.time,
      days: medForm.days,
    }, { headers })
    showMedicationModal.value = false
    medForm.name = ''
    medForm.time = '09:00'
    medForm.days = ['mon','tue','wed','thu','fri','sat','sun']
    // Reload settings to get updated medications
    await loadSettings()
  } catch (e) {
    alert('복약 알림 추가에 실패했습니다')
  } finally {
    medSaving.value = false
  }
}

async function takeMedication(medId) {
  try {
    await axios.post(`/api/elder/medications/${medId}/taken`, {}, { headers })
    takenMedications.value.add(medId)
    takenMedications.value = new Set(takenMedications.value)
  } catch (e) {
    alert('복약 완료 처리에 실패했습니다')
  }
}

async function removeMedication(medId) {
  if (!confirm('이 복약 알림을 삭제하시겠습니까?')) return
  try {
    await axios.delete(`/api/elder/medications/${medId}`, { headers })
    await loadSettings()
  } catch (e) {
    alert('삭제에 실패했습니다')
  }
}

// SOS Long Press
function startSOS() {
  sosProgress.value = 0
  const startTime = Date.now()
  sosProgressInterval = setInterval(() => {
    const elapsed = Date.now() - startTime
    sosProgress.value = Math.min((elapsed / 3000) * 100, 100)
    if (elapsed >= 3000) {
      clearInterval(sosProgressInterval)
      sosProgressInterval = null
      showSOSConfirm.value = true
    }
  }, 50)
}

function cancelSOS() {
  if (sosProgressInterval) {
    clearInterval(sosProgressInterval)
    sosProgressInterval = null
  }
  sosProgress.value = 0
}

async function confirmSOS() {
  showSOSConfirm.value = false
  sosProgress.value = 0

  let lat = null, lng = null, address = null
  try {
    const pos = await new Promise((resolve, reject) => {
      navigator.geolocation.getCurrentPosition(resolve, reject, { timeout: 5000 })
    })
    lat = pos.coords.latitude
    lng = pos.coords.longitude
  } catch (e) {
    // GPS unavailable - still send SOS
  }

  try {
    await axios.post('/api/elder/sos', { latitude: lat, longitude: lng, address }, { headers })
    sosActive.value = true
    sosLocation.value = lat ? { lat, lng } : null
    sosTime.value = new Date().toLocaleString('ko-KR')
    sosCancelable.value = true
    sosCancelCountdown.value = 10

    sosCancelInterval = setInterval(() => {
      sosCancelCountdown.value--
      if (sosCancelCountdown.value <= 0) {
        clearInterval(sosCancelInterval)
        sosCancelable.value = false
      }
    }, 1000)

    // Socket SOS + WebRTC call to guardian
    if (settings.guardian_user_id) {
      socketEmit('elder:sos', {
        guardianUserId: String(settings.guardian_user_id),
        elderName: auth.user?.name || '어르신',
        lat, lng,
      })

      try {
        const { data: onlineData } = await axios.get('/api/socket/online/' + settings.guardian_user_id)
        if (onlineData.online) {
          guardianOnline.value = true
          callMessage.value = ''
          startCall(
            { id: String(settings.guardian_user_id), name: settings.guardian_name || '보호자', _callerName: auth.user?.name || '어르신' },
            'audio'
          )
        } else {
          guardianOnline.value = false
          callMessage.value = '보호자에게 알림을 보냈습니다 (오프라인)'
          setTimeout(() => { callMessage.value = '' }, 5000)
        }
      } catch(e) {
        callMessage.value = '보호자에게 알림을 보냈습니다'
        setTimeout(() => { callMessage.value = '' }, 5000)
      }
    }
  } catch (e) {
    alert('SOS 전송에 실패했습니다. 직접 911에 연락해주세요.')
  }
}

function cancelSOSAlert() {
  sosActive.value = false
  sosCancelable.value = false
  if (sosCancelInterval) clearInterval(sosCancelInterval)
}

// Lifecycle
onMounted(() => {
  updateClock()
  clockInterval = setInterval(updateClock, 60000)

  loadSettings()
  loadCheckinHistory()
  loadHealthRecords()
  loadMedicationLogs()
  loadCommunityPosts()

  // Push notification subscription
  requestPermission().then(perm => {
    if (perm === 'granted' && auth.user?.id) {
      pushSubscribe(auth.user.id)
    }
  })

  // Socket connection + WebRTC setup
  socketConnect()
  const initWebRTCSocket = () => {
    const s = getSocket()
    if (s) {
      setSocket(s)
      setupSocketListeners()
    } else {
      setTimeout(initWebRTCSocket, 500)
    }
  }
  setTimeout(initWebRTCSocket, 500)
})

onUnmounted(() => {
  if (sosProgressInterval) clearInterval(sosProgressInterval)
  if (sosCancelInterval) clearInterval(sosCancelInterval)
  if (clockInterval) clearInterval(clockInterval)
  removeSocketListeners()
})
</script>
