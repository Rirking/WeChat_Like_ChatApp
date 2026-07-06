import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import pinia from './store'

// 导入全局样式
import './style.css'

const app = createApp(App)

// 注册路由和状态管理
app.use(router)
app.use(pinia)

// 挂载到 #app
app.mount('#app')
