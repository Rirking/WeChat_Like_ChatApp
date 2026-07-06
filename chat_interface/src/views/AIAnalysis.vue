<!--
  AIAnalysis.vue —— AI 分析页
  功能：输入/粘贴消息内容，调用千问大模型进行 AI 分析，流式输出结果

  接口：
    POST /api/ai/analyze/stream  → 流式 SSE 返回，逐字推送分析结果

  注意：后端返回的是 text/event-stream（SSE 格式），不是普通 JSON
  所以不能用 axios，要用 fetch + ReadableStream 逐块读取
-->
<template>
  <div class="chatlist-page">
    <!-- 顶部栏 -->
    <div class="chatlist-header">
      <button class="back-btn" @click="goBack">&larr; 返回</button>
      <span class="title">AI 分析</span>
      <span style="width:50px;"></span>
    </div>

    <!-- 输入区 -->
    <div class="ai-input-area">
      <textarea
        v-model="inputContent"
        placeholder="粘贴或输入你想分析的消息内容..."
        rows="4"
      ></textarea>
      <button class="analyze-btn" @click="analyze" :disabled="analyzing">
        {{ analyzing ? '分析中...' : '开始分析' }}
      </button>
    </div>

    <!-- 分析结果（流式输出） -->
    <div v-if="result || analyzing" class="ai-result">
      <div class="result-title">分析结果：</div>
      <div class="result-content">
        {{ result }}
        <span v-if="analyzing" class="cursor-blink">|</span>
      </div>
    </div>

    <!-- 操作提示 -->
    <div v-if="toastMsg" class="toast-msg">{{ toastMsg }}</div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { apiConfig } from '../config/api'
import { useUserStore } from '../store/user'

const router = useRouter()
const userStore = useUserStore()

const inputContent = ref('')
const result = ref('')
const analyzing = ref(false)
const toastMsg = ref('')

/**
 * 开始分析：POST /api/ai/analyze/stream
 *
 * 后端返回 SSE 流（text/event-stream），格式：
 *   data: {"content": "你"}\n\n
 *   data: {"content": "好"}\n\n
 *   ...
 *
 * 用 fetch + ReadableStream 逐块读取，实时拼接到 result
 */
async function analyze() {
  const content = inputContent.value.trim()
  if (!content) return

  analyzing.value = true
  result.value = ''

  try {
    const response = await fetch(`${apiConfig.baseURL}/api/ai/analyze/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${userStore.token}`
      },
      body: JSON.stringify({ content })
    })

    if (!response.ok) {
      throw new Error(`服务器返回 ${response.status}`)
    }

    // 读取流式响应
    const reader = response.body.getReader()
    const decoder = new TextDecoder()

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      // 把二进制数据解码成文本
      const text = decoder.decode(value, { stream: true })

      // SSE 格式：每条消息以 "data: " 开头，以 "\n\n" 分隔
      // 可能一次读到多行，也可能一行被拆成两块，所以用 split 处理
      const lines = text.split('\n')
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const jsonStr = line.slice(6)  // 去掉 "data: " 前缀
          try {
            const data = JSON.parse(jsonStr)
            if (data.content) {
              result.value += data.content   // 逐字拼接
            }
          } catch (e) {
            // JSON 不完整（被截断了），跳过等下一块
            continue
          }
        }
      }
    }
  } catch (error) {
    showToast('分析失败：' + error.message)
  } finally {
    analyzing.value = false
  }
}

/** 显示提示，2秒后消失 */
function showToast(text) {
  toastMsg.value = text
  setTimeout(() => { toastMsg.value = '' }, 2000)
}

function goBack() {
  router.back()
}
</script>

<style scoped>
.cursor-blink {
  animation: blink 1s infinite;
  font-weight: bold;
  color: #07c160;
}

@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}
</style>
