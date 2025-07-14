// src/router/index.ts
import { createRouter, createWebHistory } from 'vue-router'
import Home from '@/pages/Home.vue'
import Chat from '@/pages/Chat.vue'

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: Home },
    { path: '/chat', component: Chat },
  ],
})
// import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
// import Home from '@/pages/Home.vue'
// import Chat from '@/pages/Chat.vue'
//
// const routes: RouteRecordRaw[] = [
//   { path: '/', name: 'Home', component: Home },
//   { path: '/chat', name: 'Chat', component: Chat },
// ]
//
// export const router = createRouter({
//   history: createWebHistory(),
//   routes,
// })
