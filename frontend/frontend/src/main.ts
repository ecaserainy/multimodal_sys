// src/main.ts
import { createApp } from 'vue'
import App from './App.vue'
import { router } from './router'
import './style.css' // Tailwind 基础样式

createApp(App).use(router).mount('#app')

