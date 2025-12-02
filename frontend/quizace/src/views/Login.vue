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
          <el-form ref="loginRef" :model="loginForm" :rules="loginRules" :validate-on-rule-change="false" class="login-form">
            <div class="form-logo">
              <img src="@/assets/logo.png" alt="QuizAce Logo" />
            </div>
            <div class="form-header">
              <p>请登录您的账号继续学习</p>
            </div>
      
            <el-form-item prop="username" >
              <el-input
                v-model="loginForm.username"
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
            <el-form-item prop="password" >
              <el-input
                v-model="loginForm.password"
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
      
            <div class="form-options">
              <el-checkbox v-model="loginForm.rememberMe">记住密码</el-checkbox>
              <el-button type="text" class="forgot-password">忘记密码？</el-button>
            </div>

            <el-form-item style="width:100%;">
              <el-button
                  size="large"
                  type="primary"
                  style="width:100%;"
                  @click.prevent="handLogin"
                  :loading="loading"
              >
                <span>{{ loading ? '登录中...' : '登 录' }}</span>
              </el-button>
            </el-form-item>

            <div class="form-footer">
              <span>还没有账号？</span>
              <router-link to="/register">立即注册</router-link>
            </div>
          </el-form>
        </el-card>
      </div>
    </div>
  </div>
  </template>
  
  <script setup>
import request from '@/util/request'
import { ref, onMounted } from 'vue'
import qs from 'qs'
import { ElMessage } from 'element-plus'
import Cookies from "js-cookie";
import { encrypt, decrypt } from "@/util/jsencrypt";
import router from '@/router'
import { useRoute } from 'vue-router'
import { useStore } from 'vuex'
  
const store = useStore()
const route = useRoute()

    const loginForm=ref({
        username:'',
        password:'',
        rememberMe:false
    })

    const loginRef=ref(null)
    const loading=ref(false)

    const loginRules={
        username:[{required:true,trigger:['blur'],message:"请输入您的账号"}],
        password:[{required:true,trigger:['blur'],message:"请输入您的密码"}]
    }

    const handLogin=()=>{
        loginRef.value.validate(async (valid)=>{
            if(valid){
                loading.value = true
                try {
                    let result = await request.post('user/login?'+qs.stringify(loginForm.value))
                    console.log(result)
                    let data=result.data
                    if(data.code==200){
                        ElMessage.success(data.info)
                        
                        // 使用 Vuex 保存用户信息和令牌
                        store.dispatch('loginSuccess', {
                            token: data.token,
                            user: data.user
                        })
                        
                        // 勾选了需要记住密码设置在 cookie 中设置记住用户名和密码
                        if (loginForm.value.rememberMe) {
                            Cookies.set("username", loginForm.value.username, { expires: 30 });
                            Cookies.set("password", encrypt(loginForm.value.password), { expires: 30 });
                            Cookies.set("rememberMe", loginForm.value.rememberMe, { expires: 30 });
                        } else {
                            // 否则移除
                            Cookies.remove("username");
                            Cookies.remove("password");
                            Cookies.remove("rememberMe");
                        }
                        router.replace("/")
                    }else{
                        ElMessage.error(data.info)
                    }
                } catch (error) {
                    ElMessage.error('登录失败，请重试')
                    console.error('登录失败:', error)
                } finally {
                    loading.value = false
                }
            }else{
                console.log("验证失败")
            }
        }) 
    }

    function getCookie() {
        const username = Cookies.get("username");
        const password = Cookies.get("password");
        const rememberMe = Cookies.get("rememberMe");
        loginForm.value = {
        username: username === undefined ? loginForm.value.username : username,
        password: password === undefined ? loginForm.value.password : decrypt(password),
        rememberMe: rememberMe === undefined ? false : Boolean(rememberMe)
        };
    }

  getCookie();
  
  // 组件挂载后检查URL参数，如果有username则自动填充
  onMounted(() => {
    if (route.query.username) {
      loginForm.value.username = route.query.username;
    }
  });
  
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

.form-options {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 25px;
    
    .el-checkbox {
        color: #606266;
        font-size: 14px;
    }
}

.forgot-password {
    color: #409eff;
    font-size: 14px;
    
    &:hover {
        color: #66b1ff;
    }
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
  