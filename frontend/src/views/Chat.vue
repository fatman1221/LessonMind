<template>
  <div class="chat-container">
    <el-card class="chat-card">
      <div class="chat-header">
        <h2>AI教学助手</h2>
        <p>我可以帮助您进行备课、解答教学问题、提供教学建议</p>
      </div>
      
      <div class="chat-messages" ref="messagesContainer">
        <div
          v-for="(msg, index) in messages"
          :key="index"
          :class="['message-item', msg.role === 'user' ? 'user-message' : 'ai-message']"
        >
          <div class="message-avatar">
            <el-icon v-if="msg.role === 'user'"><User /></el-icon>
            <el-icon v-else><ChatLineRound /></el-icon>
          </div>
          <div class="message-content">
            <div class="message-text">{{ msg.content }}</div>
            <div class="message-time">{{ formatTime(msg.time) }}</div>
          </div>
        </div>
        <div v-if="loading" class="message-item ai-message">
          <div class="message-avatar">
            <el-icon><ChatLineRound /></el-icon>
          </div>
          <div class="message-content">
            <div class="message-text">
              <el-icon class="is-loading"><Loading /></el-icon>
              正在思考...
            </div>
          </div>
        </div>
      </div>

      <div class="chat-input">
        <el-input
          v-model="inputMessage"
          type="textarea"
          :rows="3"
          placeholder="请输入您的问题..."
          @keyup.ctrl.enter="sendMessage"
          :disabled="loading"
        />
        <div class="input-actions">
          <el-button
            type="primary"
            :loading="loading"
            @click="sendMessage"
            :disabled="!inputMessage.trim()"
          >
            发送 (Ctrl+Enter)
          </el-button>
          <el-button @click="clearMessages">清空</el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { User, ChatLineRound, Loading } from '@element-plus/icons-vue'
import { chatApi } from '@/api/chat'

const messages = ref([])
const inputMessage = ref('')
const loading = ref(false)
const messagesContainer = ref(null)

const formatTime = (time) => {
  if (!time) return ''
  const date = new Date(time)
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

const sendMessage = async () => {
  if (!inputMessage.value.trim() || loading.value) return

  const userMessage = {
    role: 'user',
    content: inputMessage.value,
    time: new Date()
  }
  messages.value.push(userMessage)
  const currentInput = inputMessage.value
  inputMessage.value = ''
  loading.value = true
  scrollToBottom()

  try {
    const res = await chatApi.sendMessage(currentInput)
    messages.value.push({
      role: 'ai',
      content: res.response,
      time: new Date()
    })
  } catch (error) {
    ElMessage.error('发送消息失败：' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
    scrollToBottom()
  }
}

const clearMessages = () => {
  messages.value = []
}

const loadHistory = async () => {
  try {
    const history = await chatApi.getHistory(20)
    messages.value = history.reverse().map(item => ({
      role: 'user',
      content: item.message,
      time: item.created_at
    })).concat(history.map(item => ({
      role: 'ai',
      content: item.response,
      time: item.created_at
    }))).sort((a, b) => new Date(a.time) - new Date(b.time))
  } catch (error) {
    console.error('加载历史记录失败', error)
  }
}

onMounted(() => {
  loadHistory()
})
</script>

<style scoped>
.chat-container {
  height: calc(100vh - 140px);
  display: flex;
  flex-direction: column;
}

.chat-card {
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: #ffffff;
  border: none;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.chat-header {
  padding: 20px;
  border-bottom: 1px solid #e4e7ed;
  text-align: center;
}

.chat-header h2 {
  font-size: 20px;
  color: #333333;
  margin-bottom: 8px;
}

.chat-header p {
  font-size: 14px;
  color: #909399;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background-color: #fafafa;
}

.message-item {
  display: flex;
  margin-bottom: 20px;
  animation: fadeIn 0.3s;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.user-message {
  flex-direction: row-reverse;
}

.user-message .message-content {
  background-color: #409EFF;
  color: #ffffff;
  margin-right: 10px;
}

.ai-message .message-content {
  background-color: #ffffff;
  color: #333333;
  margin-left: 10px;
  border: 1px solid #e4e7ed;
}

.message-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f0f2f5;
  flex-shrink: 0;
}

.user-message .message-avatar {
  background-color: #409EFF;
  color: #ffffff;
}

.ai-message .message-avatar {
  background-color: #e4e7ed;
  color: #409EFF;
}

.message-content {
  max-width: 70%;
  padding: 12px 16px;
  border-radius: 8px;
  word-wrap: break-word;
}

.message-text {
  font-size: 14px;
  line-height: 1.6;
  white-space: pre-wrap;
}

.message-time {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
  margin-top: 4px;
}

.ai-message .message-time {
  color: #909399;
}

.chat-input {
  padding: 20px;
  border-top: 1px solid #e4e7ed;
  background-color: #ffffff;
}

.input-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 10px;
}

:deep(.el-textarea__inner) {
  border-radius: 8px;
  font-size: 14px;
}
</style>

