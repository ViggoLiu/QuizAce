<template>
  <div class="login-wrapper">
    <div class="login-content">
      <div class="login-banner">
        <div class="banner-text">
          <h1>🎓 QuizAce</h1>
          <p>高校课程考试在线出题、答题与智能批阅平台</p>
          <div class="banner-features">
            <div class="feature-item">
              <i class="el-icon-edit-outline"></i>
              <span>智能出题</span>
            </div>
            <div class="feature-item">
              <i class="el-icon-trophy"></i>
              <span>在线考试</span>
            </div>
            <div class="feature-item">
              <i class="el-icon-check"></i>
              <span>自动批阅</span>
            </div>
            <div class="feature-item">
              <i class="el-icon-s-data"></i>
              <span>数据分析</span>
            </div>
          </div>
        </div>
      </div>
      <div class="login-container">
        <el-card class="login-card" shadow="hover">
          <el-form ref="registerRef" :model="registerForm" :rules="registerRules" :validate-on-rule-change="false" class="login-form">
            <div class="form-logo">
              <img src="@/assets/logo.png" alt="QuizAce Logo" />
            </div>
            <div class="form-header">
              <p>请注册您的账号开始学习之旅</p>
            </div>
      
            <el-form-item prop="username">
              <el-input
                v-model="registerForm.username"
                type="text"
                size="large"
                auto-complete="off"
                placeholder="账号"
              >
                <template #prefix>
                  <i class="el-icon-user"></i>
                </template>
              </el-input>
            </el-form-item>

            <el-form-item prop="email">
              <el-input
                v-model="registerForm.email"
                type="email"
                size="large"
                auto-complete="off"
                placeholder="邮箱"
              >
                <template #prefix>
                  <i class="el-icon-message"></i>
                </template>
              </el-input>
            </el-form-item>

            <el-form-item prop="password">
              <el-input
                v-model="registerForm.password"
                type="password"
                size="large"
                auto-complete="off"
                placeholder="密码"
                show-password
              >
                <template #prefix>
                  <i class="el-icon-lock"></i>
                </template>
              </el-input>
            </el-form-item>

            <el-form-item prop="confirmPassword">
              <el-input
                v-model="registerForm.confirmPassword"
                type="password"
                size="large"
                auto-complete="off"
                placeholder="确认密码"
                show-password
              >
                <template #prefix>
                  <i class="el-icon-lock"></i>
                </template>
              </el-input>
            </el-form-item>

            <el-form-item style="width:100%;">
              <el-button
                size="large"
                type="primary"
                style="width:100%;"
                @click.prevent="handleRegister"
                :loading="loading"
              >
                <span>{{ loading ? '注册中...' : '注 册' }}</span>
              </el-button>
            </el-form-item>

            <div class="form-footer">
              <span>已有账号？</span>
              <router-link to="/login">立即登录</router-link>
            </div>
          </el-form>
        </el-card>
      </div>
    </div>
  </div>
</template>
  
<script setup>
import request from '@/util/request'
import { ref } from 'vue'
import qs from 'qs'
import { ElMessage } from 'element-plus'
import router from '@/router'
import { useStore } from 'vuex'

const store = useStore()

const registerForm = ref({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
}) 

const registerRef = ref(null)
const loading = ref(false)

const validateConfirmPassword = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请再次输入密码'))
  } else if (value !== registerForm.value.password) {
    callback(new Error('两次输入密码不一致'))
  } else {
    callback()
  }
}

const validateEmail = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请输入邮箱地址'))
  } else {
    const emailReg = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$/
    if (!emailReg.test(value)) {
      callback(new Error('请输入正确的邮箱地址'))
    } else {
      callback()
    }
  }
}

const registerRules = {
  username: [
    { required: true, trigger: [], message: "请输入您的账号" },
    { min: 3, max: 20, trigger: [], message: "账号长度应在3-20个字符之间" }
  ],
  email: [
    { required: true, trigger: [], validator: validateEmail }
  ],
  password: [
    { required: true, trigger: [], message: "请输入您的密码" },
    { min: 6, max: 20, trigger: [], message: "密码长度应在6-20个字符之间" }
  ],
  confirmPassword: [
    { required: true, trigger: [], validator: validateConfirmPassword }
  ]
}

const handleRegister = () => {
  registerRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        const { confirmPassword, ...submitData } = registerForm.value
        let result = await request.post('user/register?' + qs.stringify(submitData))
        console.log(result)
        let data = result.data
        if (data.code == 200) {
          ElMessage.success(data.info)
          // 注册成功后跳转到登录页，并通过URL参数传递用户名
          router.replace({ path: '/login', query: { username: submitData.username } })
        } else {
          ElMessage.error(data.info)
        }
      } catch (error) {
        ElMessage.error('注册失败，请重试')
        console.error('注册失败:', error)
      } finally {
        loading.value = false
      }
    } else {
      console.log("验证失败")
    }
  }) 
}

</script>
  
<style lang="scss" scoped>

.login-wrapper {
    min-height: 100vh;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 20px;
    font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', Arial, sans-serif;
}

.login-content {
    display: flex;
    width: 100%;
    max-width: 1200px;
    height: 600px;
    border-radius: 20px;
    overflow: hidden;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
    animation: fadeIn 0.6s ease-out;
}

.login-banner {
    flex: 1;
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%);
    backdrop-filter: blur(10px);
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 60px;
    color: #ffffff;
}

.banner-text {
    text-align: center;
}

.banner-text h1 {
    font-size: 48px;
    font-weight: 700;
    margin-bottom: 20px;
    text-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.banner-text p {
    font-size: 18px;
    margin-bottom: 40px;
    opacity: 0.9;
    line-height: 1.6;
}

.banner-features {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 20px;
    margin-top: 40px;
}

.feature-item {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    padding: 15px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    font-size: 14px;
    transition: all 0.3s ease;
    
    &:hover {
        background: rgba(255, 255, 255, 0.15);
        transform: translateY(-3px);
    }
    
    i {
        font-size: 20px;
    }
}

.login-container {
    flex: 1;
    background: #ffffff;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 40px;
}

.login-card {
    width: 100%;
    max-width: 400px;
    border-radius: 16px;
    box-shadow: none;
    animation: slideIn 0.8s ease-out;
}

.login-form {
    width: 100%;
}

.form-logo {
    text-align: center;
    margin-top: 20px;
    img {
        width: 200px;
        height: auto;
    }
}

.form-header {
    text-align: center;
    margin-bottom: 40px;
}
 
.form-header h2 {
    color: #2c3e50;
    font-size: 32px;
    margin-bottom: 10px;
    font-weight: 700;
}
 
.form-header p {
    color: #95a5a6;
    font-size: 16px;
}

.el-form-item {
    margin-bottom: 24px;
    
    .el-input {
        height: 50px;
        
        .el-input__wrapper {
            height: 100%;
            border-radius: 12px;
            
            input {
                height: 100%;
                font-size: 16px;
            }
        }
    }
}

.el-button {
    height: 50px;
    font-size: 18px;
    border-radius: 12px;
    font-weight: 600;
    transition: all 0.3s ease;
    
    &:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(64, 158, 255, 0.3);
    }
}

.form-footer {
    text-align: center;
    margin-top: 30px;
    color: #95a5a6;
    font-size: 14px;
}
 
.form-footer a {
    color: #409eff;
    text-decoration: none;
    margin-left: 5px;
    font-weight: 600;
    transition: color 0.3s ease;
}
 
.form-footer a:hover {
    color: #66b1ff;
}

@keyframes fadeIn {
    from {
        opacity: 0;
        transform: scale(0.95);
    }
    to {
        opacity: 1;
        transform: scale(1);
    }
}

@keyframes slideIn {
    from {
        opacity: 0;
        transform: translateX(30px);
    }
    to {
        opacity: 1;
        transform: translateX(0);
    }
}

/* 响应式设计 */
@media (max-width: 768px) {
    .login-content {
        flex-direction: column;
        height: auto;
    }
    
    .login-banner {
        display: none;
    }
    
    .login-container {
        padding: 20px;
    }
    
    .form-header h2 {
        font-size: 28px;
    }
}

</style>

