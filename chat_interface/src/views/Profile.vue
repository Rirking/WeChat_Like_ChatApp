<!--
  Profile.vue —— 个人资料页
  功能：查看/修改昵称、性别、手机号，上传头像

  接口：
    GET  /api/users/info          → 获取当前用户信息
    PUT  /api/users/update        → 更新昵称/性别/手机号/头像URL
    POST /api/users/upload_avatar → 上传头像文件，返回 URL

  流程：
    上传头像：选文件 → POST /upload_avatar → 拿到 URL → 存到本地 userInfo.avatar
    保存资料：点保存 → PUT /update（nickname + avatar + gender + phone 一起发）
-->
<template>
  <div class="chatlist-page">
    <!-- 顶部栏 -->
    <div class="chatlist-header">
      <button class="back-btn" @click="goBack">&larr; 返回</button>
      <span class="title">个人资料</span>
      <span style="width:50px;"></span>
    </div>

    <div class="profile-content">
      <!-- 头像区：有图显图，无图显首字，点击上传 -->
      <div class="profile-avatar" @click="uploadAvatar">
        <img v-if="userInfo.avatar" :src="userInfo.avatar" class="profile-avatar-img" />
        <div v-else class="profile-avatar-placeholder">
          {{ (userInfo.nickname || userInfo.username || '?')[0] }}
        </div>
        <div class="avatar-tip">点击修改头像</div>
      </div>

      <!-- 资料表单 -->
      <div class="profile-form">
        <label>用户名</label>
        <input :value="userInfo.username" disabled />

        <label>昵称</label>
        <input v-model="form.nickname" placeholder="设置昵称" />

        <label>性别</label>
        <select v-model="form.gender">
          <option value="unknown">保密</option>
          <option value="male">男</option>
          <option value="female">女</option>
        </select>

        <label>手机号</label>
        <input v-model="form.phone" placeholder="设置手机号" />

        <button class="save-btn" @click="saveProfile" :disabled="saving">
          {{ saving ? '保存中...' : '保存' }}
        </button>
      </div>
    </div>

    <!-- 操作提示 -->
    <div v-if="toastMsg" class="toast-msg">{{ toastMsg }}</div>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { apiConfig } from '../config/api'
import { useUserStore } from '../store/user'

const router = useRouter()
const userStore = useUserStore()

const userInfo = ref({})
const form = reactive({ nickname: '', gender: 'unknown', phone: '' })
const saving = ref(false)
const toastMsg = ref('')

onMounted(async () => {
  // 获取当前用户信息
  try {
    const res = await axios.get(`${apiConfig.baseURL}/api/users/info`, {
      headers: { Authorization: `Bearer ${userStore.token}` }
    })
    if (res.data && res.data.code === 200) {
      userInfo.value = res.data.data.userinfo
      form.nickname = userInfo.value.nickname || ''
      form.gender = userInfo.value.gender || 'unknown'
      form.phone = userInfo.value.phone || ''
    }
  } catch (error) {
    console.error('获取用户信息失败:', error)
    if (error.response?.status === 401) {
      userStore.logout()
      router.push('/login')
    }
  }
})

/**
 * 保存：把所有字段（含 avatar）一起通过 PUT /api/users/update 提交
 */
async function saveProfile() {
  saving.value = true
  try {
    const res = await axios.put(
      `${apiConfig.baseURL}/api/users/update`,
      {
        nickname: form.nickname,
        avatar: userInfo.value.avatar,    // 当前头像 URL（可能刚上传过）
        gender: form.gender,
        phone: form.phone
      },
      { headers: { Authorization: `Bearer ${userStore.token}` } }
    )
    if (res.data && res.data.code === 200) {
      userInfo.value = res.data.data.userinfo
      // 同步更新 store 里的用户信息
      userStore.userInfo = res.data.data.userinfo
      showToast('保存成功')
    }
  } catch (error) {
    showToast('保存失败：' + (error.response?.data?.detail || error.message))
  } finally {
    saving.value = false
  }
}

/**
 * 上传头像：选文件 → POST /api/users/upload_avatar → 拿到 URL
 * 拿到 URL 后直接赋值给 userInfo.avatar，等用户点"保存"才写入数据库
 */
async function uploadAvatar() {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = 'image/*'
  input.onchange = async (e) => {
    const file = e.target.files[0]
    if (!file) return

    const formData = new FormData()
    formData.append('file', file)

    try {
      const res = await axios.post(
        `${apiConfig.baseURL}/api/users/upload_avatar`,
        formData,
        { headers: { Authorization: `Bearer ${userStore.token}` } }
      )
      if (res.data && res.data.code === 200) {
        userInfo.value.avatar = res.data.data.avatar   // 只更新本地显示
        showToast('头像上传成功，记得点保存')
      }
    } catch (error) {
      showToast('头像上传失败')
    }
  }
  input.click()
}

/** 显示提示，2秒后消失 */
function showToast(text) {
  toastMsg.value = text
  setTimeout(() => { toastMsg.value = '' }, 2000)
}

function goBack() {
  router.push('/chat')
}
</script>
