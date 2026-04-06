<template>
<div>
  <AdminListView icon="🛍️" title="쇼핑 관리" api-url="/api/shopping"
    :extra-cols='[{"key": "store.name", "label": "매장"}]'
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
