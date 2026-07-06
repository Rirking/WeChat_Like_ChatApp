<!--
  ChatWindow.vue —— 聊天窗口
  顶部：好友名称 + 返回按钮 + WebSocket连接状态
  中间：消息列表（自己发的气泡靠右绿色，对方的气泡靠左白色）
  底部：输入框 + AI分析按钮 + 发送按钮

  路由参数：/chat/:id  →  :id 就是好友的 user_id
-->
<template>
  <div class="chat-window">
    <!-- ===== 顶部栏 ===== -->
    <div class="chat-header">
      <button class="back-btn" @click="goBack">← 返回</button>
      <span class="name">{{ friendName }}</span>
      <span class="ws-status" :class="wsConnected ? 'connected' : 'disconnected'">
        {{ wsConnected ? '● 在线' : '○ 连接中...'}}
      </span>
    </div>

    <!-- ===== 消息列表 ===== -->
    <div class="message-list" ref="msgListRef">
      <!-- 加载中 -->
      <div v-if="loading" class="loading-text">加载中...</div>

      <!-- 消息为空 -->
      <div v-else-if="messages.length === 0" class="empty-state">
        暂无消息，发送第一条吧
      </div>

      <!-- 消息列表 -->
      <div
        v-for="msg in messages"
        :key="msg.id"
        :class="['msg-row', msg.sender_id === myUserId ? 'self' : 'other']"
      >
        <div class="msg-bubble">
          <div>{{ msg.content }}</div>
          <div class="msg-time">
            {{ formatTime(msg.sent_at) }}
            <!-- 自己发的消息显示已读/未读状态 -->
            <span v-if="msg.sender_id === myUserId" class="read-status">
              {{ msg.is_read ? '已读' : '未读' }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- ===== 发送区 ===== -->
    <div class="chat-input-area">
      <input
        v-model="inputText"
        type="text"
        placeholder="输入消息..."
        @keyup.enter="sendMessage"
      />
      <!-- AI 分析入口 -->
      <button class="ai-btn" @click="goToAIAnalysis" title="AI分析">🤖</button>
      <button class="send-btn" @click="sendMessage">发送</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import { apiConfig } from '../config/api'
import { useUserStore } from '../store/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

// --- 基础数据 ---
const friendId = ref(Number(route.params.id))  // 好友 ID（从 URL 里取）
const friendName = ref('')                      // 好友昵称
const myUserId = ref(userStore.userInfo?.id)    // 当前登录用户的 ID

const messages = ref([])      // 消息列表
const inputText = ref('')     // 输入框内容
const loading = ref(true)     // 是否加载中

// 消息列表的 DOM 引用，用于自动滚到底部
const msgListRef = ref(null)

// --- WebSocket 相关 ---
let ws = null                  // WebSocket 实例
let reconnectTimer = null      // 重连定时器
let shouldReconnect = true     // 是否应该自动重连（组件卸载时设为 false）
const wsConnected = ref(false) // WebSocket 连接状态（控制顶部状态显示）

/**
 * 页面挂载 → 加载好友信息 + 聊天记录 + 标记已读 + 连接 WebSocket
 */
onMounted(async () => {
  await loadFriendInfo()
  await fetchMessages()
  await markAsRead()
  connectWebSocket()
})

/**
 * 组件卸载 → 关闭 WebSocket + 清除重连定时器
 */
onUnmounted(() => {
  shouldReconnect = false
  if (reconnectTimer) clearTimeout(reconnectTimer)
  if (ws) {
    ws.onclose = null  // 先清掉 onclose，防止触发重连
    ws.close()
  }
})


function connectWebSocket() {
  // 把 http:// 或 https:// 替换成 ws:// 或 wss://
  const wsBase = apiConfig.baseURL.replace(/^http/, 'ws')
  const wsUrl = `${wsBase}/api/messages/ws/${userStore.token}`

  ws = new WebSocket(wsUrl)

  // 连接成功
  ws.onopen = () => {
    wsConnected.value = true
    console.log('WebSocket 已连接')
  }

  // 收到消息
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data)

    if (data.type === 'new_message') {
      // 收到对方发来的新消息
      // 只有当前正在聊天的好友发来的消息才显示
      if (data.data.sender_id === friendId.value) {
        messages.value.push(data.data)
        nextTick(() => scrollToBottom())
        // 标记已读
        markAsRead()
      }
    }

    if (data.type === 'message_sent') {
      // 自己发的消息被服务器确认成功
      messages.value.push(data.data)
      nextTick(() => scrollToBottom())
    }
  }

  // 连接关闭
  ws.onclose = () => {
    wsConnected.value = false
    console.log('WebSocket 断开')
    // 自动重连（3秒后），但组件卸载后不再重连
    if (shouldReconnect) {
      reconnectTimer = setTimeout(connectWebSocket, 3000)
    }
  }

  // 连接出错
  ws.onerror = (error) => {
    console.error('WebSocket 错误:', error)
  }
}

/**
 * 通过 WebSocket 发送消息
 * 发送格式：{"receiver_id": 2, "content": "你好"}
 * 后端收到后存入数据库，再回传 message_sent 确认
 */
function sendMessage() {
  const text = inputText.value.trim()
  if (!text) return

  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({
      receiver_id: friendId.value,
      content: text
    }))
    inputText.value = ''
  } else {
    console.warn('WebSocket 未连接，无法发送')
  }
}

/**
 * 根据 friendId 加载好友的昵称
 * 调用 GET /api/friends/list，从好友列表里找到对应的人
 */
async function loadFriendInfo() {
  try {
    const res = await axios.get(`${apiConfig.baseURL}/api/friends/list`, {
      headers: { Authorization: `Bearer ${userStore.token}` }
    })
    if (res.data && res.data.code === 200) {
      const friend = res.data.data.find(f => f.id === friendId.value)
      if (friend) {
        friendName.value = friend.nickname || friend.username
      }
    }
  } catch (error) {
    console.error('加载好友信息失败:', error)
  }
}

/**
 * 拉取聊天记录（仅页面加载时调用一次，后续靠 WebSocket 实时推送）
 * 调用 GET /api/messages/messageslist/{friend_id}?offset=0&limit=50
 */
async function fetchMessages() {
  try {
    const res = await axios.get(
      `${apiConfig.baseURL}/api/messages/messageslist/${friendId.value}`,
      {
        headers: { Authorization: `Bearer ${userStore.token}` },
        params: { offset: 0, limit: 50 }
      }
    )

    if (res.data && res.data.code === 200) {
      messages.value = res.data.data
      // 自动滚到最底部
      await nextTick()
      scrollToBottom()
    }
  } catch (error) {
    console.error('获取消息失败:', error)
    if (error.response?.status === 401) {
      userStore.logout()
      router.push('/login')
    }
  } finally {
    loading.value = false
  }
}

/**
 * 标记好友发来的消息为已读
 * 调用 PUT /api/messages/remark/{friend_id}
 * 后端会将 receiver_id=自己 且 sender_id=好友 且 is_read=False 的消息全部改为 True
 */
async function markAsRead() {
  try {
    await axios.put(
      `${apiConfig.baseURL}/api/messages/remark/${friendId.value}`,
      {},
      { headers: { Authorization: `Bearer ${userStore.token}` } }
    )
  } catch (error) {
    console.error('标记已读失败:', error)
  }
}

/**
 * 跳转到 AI 分析页
 */
function goToAIAnalysis() {
  router.push('/ai-analysis')
}

/**
 * 返回好友列表
 */
function goBack() {
  router.push('/chat')
}

/**
 * 消息列表滚动到最底部
 */
function scrollToBottom() {
  if (msgListRef.value) {
    msgListRef.value.scrollTop = msgListRef.value.scrollHeight
  }
}

/**
 * 格式化时间：去掉秒后面的毫秒部分
 * @param {string} isoString  ISO 格式的时间字符串
 * @returns {string}  例如 "07-01 21:06"
 */
function formatTime(isoString) {
  if (!isoString) return ''
  const date = new Date(isoString)
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  return `${month}-${day} ${hours}:${minutes}`
}
</script>
