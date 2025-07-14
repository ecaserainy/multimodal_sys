<template>
  <div class="min-h-screen bg-gray-50 text-gray-800">
    <Header />
    <div class="flex">
      <Sidebar />
      <router-view class="flex-1 p-6" />
    </div>
  </div>
</template>

<script setup lang="ts">
import Header from './components/Header.vue'
import Sidebar from './components/Sidebar.vue'
</script>

