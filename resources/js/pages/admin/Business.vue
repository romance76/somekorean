<template>
<div>
  <AdminListView icon="🏪" title="업소록 관리" api-url="/api/businesses"
    :extra-cols='[{"key":"category","label":"업종"},{"key":"city","label":"도시"},{"key":"rating","label":"평점"}]'
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
