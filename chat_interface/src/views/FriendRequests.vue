<!--
  FriendRequests.vue —— 好友申请管理页
  功能：查看待处理的申请（同意/拒绝）/ 已处理的申请（删除）
  接口：
    GET  /api/friends/list      → 获取申请列表
    PUT  /api/friends/status    → 同意/拒绝申请 body: { request_id, action }
    PUT  /api/friends/delete    → 删除申请记录 body: { request_id }
-->
<template>
  <div class="chatlist-page">
    <!-- 顶部栏 -->
    <div class="chatlist-header">
      <button class="back-btn" @click="goBack">← 返回</button>
      <span class="title">好友申请</span>
      <span style="width:50px;"></span>
    </div>

    <!-- Tab 切换：待处理 / 已处理 -->
    <div class="tab-bar">
      <span
        :class="['tab-item', { active: tab === 'pending' }]"
        @click="tab = 'pending'"
      >
        待处理
        <span v-if="pendingList.length > 0" class="badge">{{ pendingList.length }}</span>
      </span>
      <span
        :class="['tab-item', { active: tab === 'history' }]"
        @click="tab = 'history'"
      >
        已处理
      </span>
    </div>

    <!-- ===== 待处理 ===== -->
    <template v-if="tab === 'pending'">
      <div v-if="loading" class="loading-text">加载中...</div>

      <div v-else-if="pendingList.length === 0" class="empty-state">
        暂无待处理的好友申请
      </div>

      <div v-else>
        <div v-for="item in pendingList" :key="item.id" class="request-item">
          <div class="avatar">{{ (item.sender_nickname || item.sender_username || '?')[0] }}</div>
          <div class="request-info">
            <div class="name">{{ item.sender_nickname || item.sender_username }}</div>
            <div class="msg" v-if="item.message">验证消息：{{ item.message }}</div>
          </div>
          <div class="request-actions">
            <button class="accept-btn" @click="handleRequest(item.id, 'accept')">同意</button>
            <button class="reject-btn" @click="handleRequest(item.id, 'reject')">拒绝</button>
          </div>
        </div>
      </div>
    </template>

    <!-- ===== 已处理 ===== -->
    <template v-if="tab === 'history'">
      <div v-if="loading" class="loading-text">加载中...</div>

      <div v-else-if="historyList.length === 0" class="empty-state">
        暂无已处理的申请
      </div>

      <div v-else>
        <div v-for="item in historyList" :key="item.id" class="request-item">
          <div class="avatar">{{ (item.sender_nickname || item.sender_username || '?')[0] }}</div>
          <div class="request-info">
            <div class="name">{{ item.sender_nickname || item.sender_username }}</div>
            <div class="status-tag" :class="item.status">
              {{ item.status === 'accepted' ? '已同意' : '已拒绝' }}
            </div>
          </div>
          <button class="delete-btn" @click="deleteRequest(item.id)">删除</button>
        </div>
      </div>
    </template>

    <!-- 操作提示 -->
    <div v-if="msg" class="toast-msg">{{ msg }}</div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { apiConfig } from '../config/api'
import { useUserStore } from '../store/user'

const router = useRouter()
const userStore = useUserStore()

const tab = ref('pending')         // pending / history
const loading = ref(true)
const pendingList = ref([])        // 待处理的申请
const historyList = ref([])        // 已处理的申请
const msg = ref('')                // 操作提示

onMounted(() => {
  fetchRequests()
})

/**
 * 获取好友申请列表
 * 后端返回所有收到的申请（包括 pending/accepted/rejected）
 * 前端按 status 分两组展示
 */
async function fetchRequests() {
  loading.value = true
  try {
    const res = await axios.get(`${apiConfig.baseURL}/api/friends_request/list`, {
      headers: { Authorization: `Bearer ${userStore.token}` }
    })
    if (res.data && res.data.code === 200) {
      const list = res.data.data || []
      pendingList.value = list.filter(r => r.status === 'pending')
      historyList.value = list.filter(r => r.status !== 'pending')
    }
  } catch (error) {
    console.error('获取申请列表失败:', error)
    if (error.response?.status === 401) {
      userStore.logout()
      router.push('/login')
    }
  } finally {
    loading.value = false
  }
}

/**
 * 处理好友申请：同意 / 拒绝
 * PUT /api/friends_request/status  body: { request_id, action }
 */
async function handleRequest(requestId, action) {
  try {
    const res = await axios.put(
      `${apiConfig.baseURL}/api/friends_request/status`,
      { request_id: requestId, action },
      { headers: { Authorization: `Bearer ${userStore.token}` } }
    )
    if (res.data && res.data.code === 200) {
      showMsg(res.data.message || '操作成功')
      await fetchRequests()  // 刷新列表
    }
  } catch (error) {
    showMsg(error.response?.data?.detail || '操作失败', true)
  }
}

/**
 * 删除申请记录
 * PUT /api/friends_request/delete  body: { request_id }
 */
async function deleteRequest(requestId) {
  try {
    const res = await axios.put(
      `${apiConfig.baseURL}/api/friends_request/delete`,
      { request_id: requestId, action: 'reject' },
      { headers: { Authorization: `Bearer ${userStore.token}` } }
    )
    if (res.data && res.data.code === 200) {
      showMsg('删除成功')
      await fetchRequests()
    }
  } catch (error) {
    showMsg(error.response?.data?.detail || '删除失败', true)
  }
}

/** 显示操作提示，2秒后消失 */
function showMsg(text, isError = false) {
  msg.value = text
  setTimeout(() => { msg.value = '' }, 2000)
}

/** 返回好友列表 */
function goBack() {
  router.push('/chat')
}
</script>
