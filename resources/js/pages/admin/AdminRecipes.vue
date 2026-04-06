<template>
<div>
  <AdminListView icon="🍳" title="레시피 관리" api-url="/api/recipes"
    :extra-cols='[{"key": "category.name", "label": "카테고리"}]'
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
