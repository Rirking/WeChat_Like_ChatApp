<!--
  Login.vue —— 登录 / 注册页
  通过 isRegister 变量切换登录和注册模式
  登录用两个字段（用户名、密码），注册多一个昵称
-->
<template>
  <div class="login-page">
    <!-- 标题 -->
    <div class="login-title">💬 聊天室</div>

    <div class="login-card">
      <!-- 错误提示 -->
      <div v-if="errorMsg" class="error-msg">{{ errorMsg }}</div>

      <!-- 用户名 -->
      <label>用户名</label>
      <input
        v-model="username"
        type="text"
        placeholder="请输入用户名"
        @keyup.enter="handleSubmit"
      />

      <!-- 密码 -->
      <label>密码</label>
      <input
        v-model="password"
        type="password"
        placeholder="请输入密码"
        @keyup.enter="handleSubmit"
      />

      <!-- 注册模式下多一个昵称输入框 -->
      <template v-if="isRegister">
        <label>昵称</label>
        <input
          v-model="nickname"
          type="text"
          placeholder="给自己取个名字"
          @keyup.enter="handleSubmit"
        />
      </template>

      <!-- 主按钮：登录 / 注册 -->
      <button class="btn btn-primary" @click="handleSubmit" :disabled="loading">
        {{ loading ? '请稍候...' : (isRegister ? '注册' : '登录') }}
      </button>

      <!-- 切换登录 / 注册 -->
      <div class="tip">
        <span v-if="!isRegister">
          还没有账号？<a @click="toggleMode">去注册</a>
        </span>
        <span v-else>
          已有账号？<a @click="toggleMode">去登录</a>
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../store/user'

const router = useRouter()
const userStore = useUserStore()

// --- 表单数据 ---
const username = ref('')
const password = ref('')
const nickname = ref('')
const isRegister = ref(false)   // true = 注册模式，false = 登录模式
const errorMsg = ref('')        // 错误提示文本
const loading = ref(false)      // 防止重复提交

/**
 * 切换登录 / 注册模式
 */
function toggleMode() {
  isRegister.value = !isRegister.value
  errorMsg.value = ''   // 切换时清空错误提示
}

/**
 * 提交表单：登录 或 注册
 */
async function handleSubmit() {
  // 简单校验
  if (!username.value.trim() || !password.value.trim()) {
    errorMsg.value = '用户名和密码不能为空'
    return
  }
  if (isRegister.value && !nickname.value.trim()) {
    errorMsg.value = '昵称不能为空'
    return
  }

  loading.value = true
  errorMsg.value = ''

  let result
  if (isRegister.value) {
    // 注册
    result = await userStore.register(
      username.value.trim(),
      password.value,
      nickname.value.trim()
    )
  } else {
    // 登录
    result = await userStore.login(username.value.trim(), password.value)
  }

  loading.value = false

  if (result.success) {
    // 登录 / 注册成功 → 跳转到聊天列表
    router.push('/chat')
  } else {
    // 失败 → 显示错误
    errorMsg.value = result.message
  }
}
</script>
