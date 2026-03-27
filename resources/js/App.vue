<template>
  <div id="somekorean-app">
    <NavBar v-if="!isAuthPage" />
    <main class="min-h-screen bg-gray-50">
      <router-view />
    </main>
    <BottomNav v-if="!isAuthPage && isMobile" />
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import NavBar from './components/NavBar.vue';
import BottomNav from './components/BottomNav.vue';

const route = useRoute();
const isAuthPage = computed(() => route.path.startsWith('/auth'));
const isMobile = computed(() => window.innerWidth < 768);
</script>
