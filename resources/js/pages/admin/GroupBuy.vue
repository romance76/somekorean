<template>
<div>
  <AdminListView icon="🤝" title="공동구매 관리" api-url="/api/groupbuys"
    :extra-cols='[{"key":"status","label":"상태"},{"key":"city","label":"도시"}]'
    @open-user="u => { selectedUserId = u?.id; showUser = true }" />
  <AdminUserModal :show="showUser" :user-id="selectedUserId" @close="showUser=false" />
</div>
</template>
<script setup>
import { ref } from 'vue'
import AdminListView from '../../components/AdminListView.vue'
import AdminUserModal from '../../components/AdminUserModal.vue'
const showUser = ref(false)
const selectedUserId = ref(null)
</script>
