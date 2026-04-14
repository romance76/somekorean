<template>
<div>
  <div class="flex items-center justify-between mb-4">
    <h2 class="text-lg font-bold">👥 동호회 관리</h2>
  </div>
  <AdminListView icon="👥" title="동호회" api-url="/api/clubs"
    :extra-cols='[{"key":"category","label":"카테고리"},{"key":"type","label":"유형"},{"key":"member_count","label":"회원수"}]'
    @open-user="u => { selectedUserId = u?.id; showUser = true }">
    <template #filters>
      <select v-model="catFilter" @change="$forceUpdate()" class="border rounded px-2 py-1 text-sm">
        <option value="">전체 카테고리</option>
        <option v-for="c in ['등산','골프','테니스','볼링','독서','요리','사진','음악','운동','영화','게임','여행','낚시','기타']" :key="c" :value="c">{{ c }}</option>
      </select>
    </template>
  </AdminListView>
  <AdminUserModal :show="showUser" :user-id="selectedUserId" @close="showUser=false" />
</div>
</template>
<script setup>
import { ref } from 'vue'
import AdminListView from '../../components/AdminListView.vue'
import AdminUserModal from '../../components/AdminUserModal.vue'
const showUser = ref(false)
const selectedUserId = ref(null)
const catFilter = ref('')
</script>
