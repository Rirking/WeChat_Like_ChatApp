<!--
  ChatList.vue —— 会话列表（好友列表）
  新增功能：搜索用户 → 添加好友 / 查看好友申请列表
-->
<template>
  <div class="chatlist-page">
    <!-- 顶部栏 -->
    <div class="chatlist-header">
      <span class="title">💬 聊天室</span>
      <div class="header-actions">
        <!-- 个人资料入口 -->
        <button class="header-btn" @click="router.push('/profile')">我的</button>
        <!-- 好友申请入口（带未读数） -->
        <button class="header-btn" @click="goToRequests">
          好友申请
          <span v-if="pendingCount > 0" class="badge">{{ pendingCount }}</span>
        </button>
        <button class="logout-btn" @click="handleLogout">退出</button>
      </div>
    </div>

    <!-- ===== 搜索区域 ===== -->
    <div class="search-area">
      <input
        v-model="searchQuery"
        type="text"
        placeholder="搜索用户名添加好友..."
        @keyup.enter="searchUser"
      />
      <button class="search-btn" @click="searchUser" :disabled="searching">
        {{ searching ? '搜索中...' : '搜索' }}
      </button>
    </div>

    <!-- 搜索结果 -->
    <div v-if="searchResult" class="search-result">
      <div class="search-item">
        <div class="avatar">
          <img v-if="searchResult.avatar" :src="searchResult.avatar" class="avatar-img" />
          <span v-else>{{ (searchResult.nickname || searchResult.username)[0] }}</span>
        </div>
        <div class="friend-info">
          <div class="name">{{ searchResult.nickname || searchResult.username }}</div>
          <div class="username">@{{ searchResult.username }}</div>
        </div>
        <button
          class="add-btn"
          @click="addFriend"
          :disabled="adding"
        >
          {{ adding ? '发送中...' : '添加好友' }}
        </button>
      </div>
      <div v-if="searchMsg" class="search-msg" :class="{ error: searchMsgIsError }">
        {{ searchMsg }}
      </div>
    </div>

    <!-- 加载中 -->
    <div v-if="loading" class="loading-text">加载中...</div>

    <!-- 好友列表 -->
    <div v-else-if="friends.length > 0">
      <div
        v-for="friend in friends"
        :key="friend.id"
        class="friend-item"
        @click="openChat(friend)"
      >
        <div class="avatar">
          <img v-if="friend.avatar" :src="friend.avatar" class="avatar-img" />
          <span v-else>{{ (friend.nickname || friend.username)[0] }}</span>
        </div>
        <div class="friend-info">
          <div class="name">{{ friend.nickname || friend.username }}</div>
          <div class="username">@{{ friend.username }}</div>
        </div>
      </div>
    </div>

    <!-- 暂无好友 -->
    <div v-else class="empty-state">
      <p>暂无好友</p>
      <p style="font-size:13px;margin-top:8px;">在上方搜索用户名添加好友</p>
    </div>
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

// 好友列表相关
const friends = ref([])
const loading = ref(true)

// 搜索相关
const searchQuery = ref('')      // 搜索输入框内容
const searchResult = ref(null)   // 搜索到的用户
const searchMsg = ref('')        // 搜索提示消息
const searchMsgIsError = ref(false)
const searching = ref(false)
const adding = ref(false)

// 好友申请未读数
const pendingCount = ref(0)

onMounted(() => {
  fetchFriends()
  fetchPendingCount()
})

/** 获取好友列表 */
async function fetchFriends() {
  loading.value = true
  try {
    const res = await axios.get(`${apiConfig.baseURL}/api/friends/list`, {
      headers: { Authorization: `Bearer ${userStore.token}` }
    })
    if (res.data && res.data.code === 200) {
      friends.value = res.data.data
    }
  } catch (error) {
    console.error('获取好友列表失败:', error)
    if (error.response?.status === 401) {
      userStore.logout()
      router.push('/login')
    }
  } finally {
    loading.value = false
  }
}

/**
 * 搜索用户：GET /api/users/search?username=xxx
 * 精确匹配用户名，返回用户信息
 */
async function searchUser() {
  const q = searchQuery.value.trim()
  if (!q) return

  searching.value = true
  searchResult.value = null
  searchMsg.value = ''

  try {
    const res = await axios.get(`${apiConfig.baseURL}/api/users/search`, {
      headers: { Authorization: `Bearer ${userStore.token}` },
      params: { username: q }
    })

    if (res.data && res.data.code === 200) {
      searchResult.value = res.data.data.userinfo
      searchMsgIsError.value = false
      searchMsg.value = ''
    } else {
      searchResult.value = null
      searchMsgIsError.value = true
      searchMsg.value = res.data.message || '查无此用户'
    }
  } catch (error) {
    searchResult.value = null
    searchMsgIsError.value = true
    searchMsg.value = '搜索失败：' + (error.response?.data?.detail || error.message)
  } finally {
    searching.value = false
  }
}

/**
 * 添加好友：POST /api/friends_request/add
 * receiver_id 取搜索结果里的 id
 */
async function addFriend() {
  if (!searchResult.value) return

  adding.value = true
  searchMsg.value = ''

  try {
    const res = await axios.post(
      `${apiConfig.baseURL}/api/friends_request/add`,
      { receiver_id: searchResult.value.id, message: '' },
      { headers: { Authorization: `Bearer ${userStore.token}` } }
    )

    if (res.data && res.data.code === 200) {
      searchMsgIsError.value = false
      searchMsg.value = '好友申请已发送！'
      // 延迟清空搜索结果
      setTimeout(() => {
        searchQuery.value = ''
        searchResult.value = null
        searchMsg.value = ''
      }, 2000)
    } else {
      searchMsgIsError.value = true
      searchMsg.value = res.data.message || '添加失败'
    }
  } catch (error) {
    searchMsgIsError.value = true
    searchMsg.value = error.response?.data?.detail || '添加好友失败'
  } finally {
    adding.value = false
  }
}

/**
 * 获取好友申请未读数
 * 调用 GET /api/friends_request/list 获取待处理申请的数量
 */
async function fetchPendingCount() {
  try {
    const res = await axios.get(`${apiConfig.baseURL}/api/friends_request/list`, {
      headers: { Authorization: `Bearer ${userStore.token}` }
    })
    if (res.data && res.data.code === 200 && Array.isArray(res.data.data)) {
      pendingCount.value = res.data.data.length
    }
  } catch (error) {
    // 忽略，没申请就不显示
  }
}

/** 跳转到好友申请页 */
function goToRequests() {
  router.push('/requests')
}

/** 进入聊天窗口 */
function openChat(friend) {
  router.push(`/chat/${friend.id}`)
}

/** 退出登录 */
function handleLogout() {
  userStore.logout()
  router.push('/login')
}
</script>
