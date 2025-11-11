<template>
  <div class="login-container">
    <h2>登录页面</h2>
    <el-button @click="testApi">测试接口</el-button>
    <div v-if="message" class="response-message">
      <el-alert
        :title="message"
        type="success"
        show-icon
      />
    </div>
    <div v-if="error" class="response-error">
      <el-alert
        :title="error"
        type="error"
        show-icon
      />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'

// 响应消息状态
const message = ref('')
const error = ref('')

const testApi = async () => {
  try {
    // 清空之前的消息
    message.value = ''
    error.value = ''
    
    // 调用后端API
    const res = await axios.get('/api/user/test/')
    console.log('API响应:', res.data)  // 控制台输出
    
    // 在页面上显示响应消息
    message.value = res.data.message || JSON.stringify(res.data)
  } catch (err) {
    console.error('API调用错误:', err)
    error.value = `接口调用失败: ${err.message || '未知错误'}`
  }
}
</script>

<style scoped>
.login-container {
  max-width: 400px;
  margin: 100px auto;
  padding: 20px;
  text-align: center;
}

h2 {
  margin-bottom: 20px;
}

.response-message,
.response-error {
  margin-top: 20px;
}
</style>