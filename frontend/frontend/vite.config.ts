import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'url'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      // 把 "@/" 映射到 src 目录
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  // …如果你还有其他配置就放在这里
})
