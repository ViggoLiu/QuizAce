<template>
  <div 
    class="ai-float-container" 
    ref="floatContainer"
    :style="{
      left: position.x + 'px',
      top: position.y + 'px'
    }"
  >
    <!-- 悬浮小球 -->
    <div 
      class="ai-ball" 
      :class="{ 'active': isChatOpen }"
      @mousedown="startDrag"
    >
      <i class="el-icon-robot"></i>
    </div>
    
    <!-- 聊天窗口 -->
    <div class="ai-chat-window" v-if="isChatOpen">
      <!-- 聊天头部 -->
      <div class="chat-header">
        <h3>AI助手</h3>
        <button class="close-btn" @click="toggleChat">
          <i class="el-icon-close"></i>
        </button>
      </div>
      
      <!-- 聊天内容 -->
      <div class="chat-content" ref="chatContent">
        <div 
          v-for="(message, index) in messages" 
          :key="index" 
          class="message" 
          :class="{ 'user': message.isUser, 'ai': !message.isUser }"
        >
          <div class="message-content" v-html="formatMarkdown(message.content)"></div>
        </div>
      </div>
      
      <!-- 输入区域 -->
      <div class="chat-input-area">
        <el-input
          v-model="inputMessage"
          placeholder="请输入您的问题..."
          @keyup.enter="sendMessage"
          clearable
        >
          <template #append>
            <el-button type="primary" @click="sendMessage">发送</el-button>
          </template>
        </el-input>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
export default {
  name: 'AIFloatBall',
  data() {
    return {
      isChatOpen: false,
      messages: [
        {
          content: '您好！我是您的AI助手，有什么可以帮助您了解系统使用的问题吗？',
          isUser: false
        }
      ],
      inputMessage: '',
      isLoading: false,
      position: {
        x: window.innerWidth - 100,
        y: window.innerHeight - 100
      },
      isDragging: false,
      dragStart: {
        x: 0,
        y: 0
      },
      // 添加点击起始位置，用于判断是点击还是拖拽
      clickStart: {
        x: 0,
        y: 0
      },
      // 拖拽阈值，超过则认为是拖拽
      dragThreshold: 5
    }
  },
  mounted() {
    // 添加鼠标事件监听器
    document.addEventListener('mousemove', this.onDrag)
    document.addEventListener('mouseup', this.stopDrag)
  },
  beforeUnmount() {
    // 移除鼠标事件监听器
    document.removeEventListener('mousemove', this.onDrag)
    document.removeEventListener('mouseup', this.stopDrag)
  },
  methods: {
    toggleChat() {
      this.isChatOpen = !this.isChatOpen
    },
    startDrag(event) {
      // 只有左键点击才能拖动
      if (event.button !== 0) return
      
      // 记录点击起始位置，用于判断是点击还是拖拽
      this.clickStart.x = event.clientX
      this.clickStart.y = event.clientY
      
      this.isDragging = true
      this.dragStart.x = event.clientX - this.position.x
      this.dragStart.y = event.clientY - this.position.y
      
      // 阻止默认行为，避免文本选择
      event.preventDefault()
    },
    onDrag(event) {
      if (!this.isDragging) return
      
      const newX = event.clientX - this.dragStart.x
      const newY = event.clientY - this.dragStart.y
      
      // 限制悬浮球在窗口内
      const containerWidth = 60 // 悬浮球宽度
      const containerHeight = 60 // 悬浮球高度
      
      this.position.x = Math.max(0, Math.min(newX, window.innerWidth - containerWidth))
      this.position.y = Math.max(0, Math.min(newY, window.innerHeight - containerHeight))
    },
    stopDrag(event) {
      // 计算拖拽距离
      const dragDistance = Math.sqrt(
        Math.pow(event.clientX - this.clickStart.x, 2) + 
        Math.pow(event.clientY - this.clickStart.y, 2)
      )
      
      // 如果拖拽距离小于阈值，则认为是点击
      if (dragDistance < this.dragThreshold) {
        this.toggleChat()
      }
      
      this.isDragging = false
    },
    sendMessage() {
      if (!this.inputMessage.trim() || this.isLoading) return
      
      // 添加用户消息
      const userMessage = this.inputMessage.trim()
      this.messages.push({
        content: userMessage,
        isUser: true
      })
      this.inputMessage = ''
      
      // 滚动到底部
      this.$nextTick(() => {
        this.scrollToBottom()
      })
      
      // 调用AI接口获取回复
      this.isLoading = true
      this.callAIAPI(userMessage)
    },
    async callAIAPI(message) {
      try {
        // ZenMux OpenAI兼容API调用
        console.log('开始调用ZenMux API...')
        
        // 准备请求数据 - 参考Python示例使用正确的ZenMux参数，精简系统提示
        const requestData = {
          model: 'z-ai/glm-4.6v-flash',
          messages: [
            { 
              role: 'system', 
              content: `你是一个系统使用教程助手，帮助用户了解和使用QuizAce系统。请根据以下核心信息回答用户问题：

# QuizAce 系统核心说明

## 1. 系统概述
QuizAce是面向教育场景的智能考试练习系统，支持学生练习、教师出题阅卷、管理员系统管理。

## 2. 身份角色
- 学生：在线练习、参加考试、查看成绩和学习分析
- 教师：管理题库、发布考试、批改试卷、查看教学分析
- 管理员：管理用户、审核资源、管理论坛内容

## 3. 核心功能
### 学生端
- 考试中心：参加教师发布的正式考试
- 模拟练习：自主练习，设置科目、题型、时长和题量
- 错题本：收集管理错题，支持重新练习和移除
- 学习分析：查看学习进度、成绩趋势和错题分布

### 教师端
- 题目管理：创建、编辑、批量导入题目
- 考试发布：创建和发布考试任务
- 阅卷管理：批改学生主观题试卷
- 教学分析：查看班级学习情况和考试结果

### 管理员端
- 用户管理：添加、编辑、禁用用户
- 资源审核：审核用户上传的学习资源
- 论坛管理：管理论坛帖子和评论

## 4. 常见问题
- 忘记密码：点击登录页面的"忘记密码"链接重置
- 考试注意：不要刷新页面，系统自动保存进度，时间到自动提交
- 题目要求：客观题至少2个选项，分值合理设置
- 阅卷规则：主观题批改后成绩立即更新，批改后不可修改

## 5. 技术支持
- 系统管理员：1446035863@qq.com
- 技术支持：499783408@qq.com

请用简洁明了的语言回答用户关于QuizAce系统使用的问题，重点突出核心操作流程和注意事项。` 
            },
            { role: 'user', content: message }
          ],
          temperature: 0.7
        }
        
        console.log('请求数据:', requestData)
        
        // 发送请求
        const response = await axios.post(
          'https://zenmux.ai/api/v1/chat/completions',
          requestData,
          {
            headers: {
              'Authorization': 'Bearer sk-ai-v1-79ae60b8c0b8d84bb11cf8b6b6ec61d85c6f2d2899616c812717494abcd210ca',
              'Content-Type': 'application/json',
              'Accept': 'application/json'
            },
            // 增加超时设置
            timeout: 10000
          }
        )
        
        console.log('API调用成功，响应数据:', response.data)
        
        // 处理响应
        if (response.data && response.data.choices && response.data.choices.length > 0) {
          this.messages.push({
            content: response.data.choices[0].message.content,
            isUser: false
          })
        } else {
          throw new Error('API返回了无效的响应格式')
        }
      } catch (error) {
        console.error('AI API调用失败:', error)
        
        // 详细记录错误信息
        if (error.response) {
          // 服务器返回了错误状态码
          console.error('错误状态码:', error.response.status)
          console.error('错误数据:', error.response.data)
          console.error('错误头信息:', error.response.headers)
        } else if (error.request) {
          // 请求已发送但没有收到响应
          console.error('请求已发送但未收到响应:', error.request)
        } else {
          // 请求配置有误
          console.error('请求配置错误:', error.message)
        }
        
        // 构建用户友好的错误信息
        let errorMsg = '抱歉，暂时无法连接到AI服务，请稍后再试。'
        
        if (error.response) {
          const errorData = error.response.data
          if (errorData.error) {
            errorMsg = `AI服务错误: ${errorData.error.message || error.response.statusText}`
          } else {
            errorMsg = `AI服务错误: ${error.response.status} ${error.response.statusText}`
          }
        } else if (error.request) {
          errorMsg = '无法连接到AI服务，请检查网络连接或稍后重试。'
        } else {
          errorMsg = `请求错误: ${error.message}`
        }
        
        this.messages.push({
          content: errorMsg,
          isUser: false
        })
      } finally {
        this.isLoading = false
        // 滚动到底部
        this.$nextTick(() => {
          this.scrollToBottom()
        })
      }
    },
    scrollToBottom() {
      const chatContent = this.$refs.chatContent
      if (chatContent) {
        chatContent.scrollTop = chatContent.scrollHeight
      }
    },
    // 格式化Markdown文本，转换为HTML
    formatMarkdown(text) {
      if (!text) return ''
      
      let formattedText = text
      
      // 处理加粗：**文本** -> <strong>文本</strong>
      formattedText = formattedText.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      
      // 处理斜体：*文本* -> <em>文本</em>
      formattedText = formattedText.replace(/\*(.*?)\*/g, '<em>$1</em>')
      
      // 处理标题：# 标题 -> <h1>标题</h1>
      formattedText = formattedText.replace(/^# (.*$)/gm, '<h1>$1</h1>')
      formattedText = formattedText.replace(/^## (.*$)/gm, '<h2>$1</h2>')
      formattedText = formattedText.replace(/^### (.*$)/gm, '<h3>$1</h3>')
      
      // 处理无序列表：- 项 -> <li>项</li>
      formattedText = formattedText.replace(/^- (.*$)/gm, '<li>$1</li>')
      // 将连续的<li>标签包裹在<ul>中
      formattedText = formattedText.replace(/(<li>.*?<\/li>)(?=<li>|$)/gs, '<ul>$&</ul>')
      
      // 处理换行：\n -> <br>
      formattedText = formattedText.replace(/\n/g, '<br>')
      
      return formattedText
    }
  }
}
</script>

<style scoped>
.ai-float-container {
  position: fixed;
  z-index: 1000;
  cursor: move;
}

.ai-ball {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transition: all 0.3s ease;
  font-size: 24px;
  color: white;
}

.ai-ball:hover {
  transform: scale(1.1);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
}

.ai-ball.active {
  transform: scale(1.1);
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.ai-chat-window {
  position: absolute;
  bottom: 80px;
  right: 0;
  width: 350px;
  height: 450px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from {
    transform: translateY(20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.chat-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 12px 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chat-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

.close-btn {
  background: transparent;
  border: none;
  color: white;
  font-size: 18px;
  cursor: pointer;
  padding: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: background 0.2s;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

.chat-content {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
  background: #f5f7fa;
}

.message {
  margin-bottom: 12px;
  display: flex;
  align-items: flex-start;
}

.message.user {
  justify-content: flex-end;
}

.message.ai {
  justify-content: flex-start;
}

.message-content {
  max-width: 80%;
  padding: 8px 12px;
  border-radius: 8px;
  word-wrap: break-word;
  line-height: 1.4;
}

.message.user .message-content {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-bottom-right-radius: 4px;
}

.message.ai .message-content {
  background: white;
  color: #333;
  border: 1px solid #e4e7ed;
  border-bottom-left-radius: 4px;
}

.chat-input-area {
  padding: 12px 16px;
  background: white;
  border-top: 1px solid #e4e7ed;
}
</style>