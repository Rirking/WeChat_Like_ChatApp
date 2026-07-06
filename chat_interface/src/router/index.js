import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '../store/user'

/*
 * 路由表 —— 整个应用只有 3 个页面：
 *   1. /login       登录 / 注册
 *   2. /chat        好友列表（会话列表）
 *   3. /chat/:id    和某个好友的聊天窗口
 *
 * 路由守卫：未登录 → 强制跳转 /login
 */

const routes = [
  {
    // 访问根路径 → 直接去聊天列表（路由守卫会判断是否登录）
    path: '/',
    redirect: '/chat'
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { title: '聊天室 - 登录' }
  },
  {
    path: '/chat',
    name: 'ChatList',
    // 懒加载：只有访问这个路由时才去加载对应的 .vue 文件
    component: () => import('../views/ChatList.vue'),
    meta: { title: '聊天室', requiresAuth: true }
  },
  {
    // :id 是动态参数，比如 /chat/2 表示和 id=2 的好友聊天
    path: '/chat/:id',
    name: 'ChatWindow',
    component: () => import('../views/ChatWindow.vue'),
    meta: { title: '聊天中', requiresAuth: true }
  },
  {
    // 好友申请管理页
    path: '/requests',
    name: 'FriendRequests',
    component: () => import('../views/FriendRequests.vue'),
    meta: { title: '好友申请', requiresAuth: true }
  },
  {
    // 个人资料页
    path: '/profile',
    name: 'Profile',
    component: () => import('../views/Profile.vue'),
    meta: { title: '个人资料', requiresAuth: true }
  },
  {
    // AI 分析页
    path: '/ai-analysis',
    name: 'AIAnalysis',
    component: () => import('../views/AIAnalysis.vue'),
    meta: { title: 'AI分析', requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

/*
 * 全局前置守卫 —— 每次路由跳转前都会执行
 * 作用：检查用户是否登录，未登录就踢回登录页
 *
 * 注意：这里读 Pinia store 内存里的 token，而不是 localStorage。
 * 因为 Pinia persist 插件是异步写入 localStorage 的，
 * 登录成功后立刻跳转时，localStorage 可能还没写入完成。
 */
router.beforeEach((to, from, next) => {
  // 设置页面标题
  document.title = to.meta.title || '聊天室'

  // 如果目标页面不需要登录，直接放行（目前只有 /login 不需要）
  if (!to.meta.requiresAuth) {
    next()
    return
  }

  /*
   * 需要登录的页面 → 直接从 Pinia store 读 token（内存，即时生效）
   *
   * 同时兜底刷新场景：如果登录后刷新了页面，store 还没有从 localStorage 恢复，
   * 我们手动从 localStorage 读一次作为补充
   */
  const userStore = useUserStore()

  // 优先读内存里的 token（刚登录完有值）
  let token = userStore.token

  // 兜底：刷新页面后 store 还未来得及 hydrate，手动从 localStorage 读
  if (!token) {
    try {
      const raw = localStorage.getItem('user-store')
      if (raw) {
        const parsed = JSON.parse(raw)
        token = parsed.token || ''
      }
    } catch (e) {
      // localStorage 解析失败，忽略
    }
  }

  if (token) {
    next()
  } else {
    next('/login')
  }
})

export default router
