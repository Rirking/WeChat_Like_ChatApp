import { defineStore } from 'pinia'
import axios from 'axios'
import { apiConfig } from '../config/api'

/*
 * 用户状态管理 —— 管理登录、注册、用户信息
 *
 * 持久化到 localStorage，key = "user-store"
 * 刷新页面后 token 和用户信息不会丢失
 */
export const useUserStore = defineStore('user', {
  // --- 状态（数据） ---
  state: () => ({
    token: '',          // JWT token，每次请求都要带在 Authorization 头里
    userInfo: null,     // 当前登录用户的信息 { id, username, nickname, ... }
    isLogin: false      // 是否已登录
  }),

  // --- 计算属性（方便获取状态） ---
  getters: {
    getToken: (state) => state.token,
    getUserInfo: (state) => state.userInfo,
    getLoginStatus: (state) => state.isLogin
  },

  // --- 动作（修改状态 + 调接口） ---
  actions: {
    /**
     * 登录
     * @param {string} username  用户名
     * @param {string} password  密码
     * @returns {object} { success, message }
     */
    async login(username, password) {
      try {
        // POST /api/users/login
        const res = await axios.post(`${apiConfig.baseURL}/api/users/login`, {
          username,
          password
        })

        if (res.data && res.data.code === 200) {
          // 登录成功 → 保存 token 和用户信息
          this.token = res.data.data.token
          this.userInfo = res.data.data.userinfo
          this.isLogin = true
          return { success: true, message: '登录成功' }
        } else {
          return { success: false, message: res.data.message || '登录失败' }
        }
      } catch (error) {
        // 网络错误或服务器返回了非 200
        const msg = error.response?.data?.detail || '登录请求失败'
        return { success: false, message: msg }
      }
    },

    /**
     * 注册
     * @param {string} username  用户名
     * @param {string} password  密码
     * @param {string} nickname  昵称
     * @returns {object} { success, message }
     */
    async register(username, password, nickname) {
      try {
        // POST /api/users/register
        const res = await axios.post(`${apiConfig.baseURL}/api/users/register`, {
          username,
          password,
          nickname
        })

        if (res.data && res.data.code === 200) {
          // 注册成功 → 后端不会自动返回 token，
          // 所以注册成功后自动调一次登录获取 token
          const loginRes = await this.login(username, password)
          return loginRes
        } else {
          return { success: false, message: res.data.message || '注册失败' }
        }
      } catch (error) {
        const msg = error.response?.data?.detail || '注册请求失败'
        return { success: false, message: msg }
      }
    },

    /**
     * 退出登录
     * 清空 token 和用户信息
     */
    logout() {
      this.token = ''
      this.userInfo = null
      this.isLogin = false
    }
  },

  // --- 持久化配置 ---
  persist: {
    enabled: true,
    strategies: [
      {
        key: 'user-store',     // localStorage 的 key 名
        storage: localStorage   // 存储位置
      }
    ]
  }
})
