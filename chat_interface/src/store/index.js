import { createPinia } from 'pinia'
import { createPersistedState } from 'pinia-plugin-persistedstate'

// 创建 Pinia 实例
const pinia = createPinia()

/*
 * 持久化插件：
 *   把 store 里的数据自动存到 localStorage，
 *   刷新页面后数据还在（比如 token、用户信息）
 */
pinia.use(createPersistedState({
  storage: localStorage
}))

export default pinia
