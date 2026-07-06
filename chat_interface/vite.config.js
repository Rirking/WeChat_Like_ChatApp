import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  base: '/property_manager/',
  server: {
    port: 8002,           // 前端开发服务器端口，避开后端 8000 和其他项目
    host: '127.0.0.1'     // 只允许本地访问
  }
})
