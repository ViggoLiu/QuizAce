<template>
  <div class="welcome-container">
    <!-- 背景装饰 -->
    <div class="background-decoration">
      <div class="circle circle-1"></div>
      <div class="circle circle-2"></div>
      <div class="circle circle-3"></div>
      <div class="circle circle-4"></div>
    </div>
    
    <el-card class="welcome-card" shadow="hover">
      <template #header>
        <div class="welcome-header">
          <div class="header-content">
            <div class="header-icon">
              <i class="el-icon-s-home"></i>
            </div>
            <div class="header-text">
              <h2>👋 欢迎回来，{{ userName }}！</h2>
              <p class="current-time">{{ currentTime }}</p>
            </div>
          </div>
        </div>
      </template>
      <div class="welcome-content">
        <div class="welcome-message">
          <p class="greeting">很高兴再次见到您！</p>
          <p v-if="userRole === 'student'" class="role-message">祝您学习进步，考试顺利！</p>
          <p v-else-if="userRole === 'teacher'" class="role-message">祝您工作顺利，教学愉快！</p>
          <p v-else-if="userRole === 'admin'" class="role-message">祝您管理工作愉快！</p>
        </div>
        <div class="welcome-stats">
          <el-row :gutter="25">
            <el-col :xs="24" :sm="12" :md="8">
              <div class="stat-card">
                <div class="stat-icon exam">
                  <i class="el-icon-trophy"></i>
                </div>
                <div class="stat-info">
                  <div class="stat-number">0</div>
                  <div class="stat-label">进行中的考试</div>
                </div>
              </div>
            </el-col>
            <el-col :xs="24" :sm="12" :md="8">
              <div class="stat-card">
                <div class="stat-icon questions">
                  <i class="el-icon-edit-outline"></i>
                </div>
                <div class="stat-info">
                  <div class="stat-number">0</div>
                  <div class="stat-label">已完成练习</div>
                </div>
              </div>
            </el-col>
            <el-col :xs="24" :sm="12" :md="8">
              <div class="stat-card">
                <div class="stat-icon progress">
                  <i class="el-icon-s-data"></i>
                </div>
                <div class="stat-info">
                  <div class="stat-number">0%</div>
                  <div class="stat-label">学习进度</div>
                </div>
              </div>
            </el-col>
          </el-row>
        </div>
        <div class="welcome-quick-links">
          <h3 class="section-title">
            <i class="el-icon-star-on"></i> 快速开始
          </h3>
          <el-row :gutter="15">
            <el-col :xs="24" :sm="12" :md="6" v-for="(link, index) in quickLinks" :key="index">
              <el-button 
                :type="link.type" 
                :icon="link.icon" 
                @click="$router.push(link.path)"
                class="quick-link-btn"
              >
                {{ link.text }}
              </el-button>
            </el-col>
          </el-row>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script>
export default {
  name: "Welcome",
  data() {
    return {
      currentTime: ''
    };
  },
  computed: {
    getUser() {
      return this.$store.state.user;
    },
    getUserRole() {
      return this.$store.getters.getUserRole;
    },
    userName() {
      return this.getUser ? this.getUser.username : '用户';
    },
    userRole() {
      return this.getUserRole;
    },
    quickLinks() {
      // 根据用户角色返回不同的快速链接
      if (this.userRole === 'student') {
        return [
          { text: '考试中心', path: '/student/exam', icon: 'el-icon-trophy', type: 'primary' },
          { text: '模拟练习', path: '/student/questions', icon: 'el-icon-edit-outline', type: 'success' },
          { text: '错题本', path: '/student/wrong-book', icon: 'el-icon-document-delete', type: 'warning' },
          { text: '学习分析', path: '/student/analysis', icon: 'el-icon-s-data', type: 'info' }
        ];
      } else if (this.userRole === 'teacher') {
        return [
          { text: '题目管理', path: '/teacher/questions', icon: 'el-icon-edit-outline', type: 'primary' },
          { text: '考试发布', path: '/teacher/exam-manage', icon: 'el-icon-trophy', type: 'success' },
          { text: '阅卷管理', path: '/teacher/marking', icon: 'el-icon-document-checked', type: 'warning' },
          { text: '教学分析', path: '/teacher/analysis', icon: 'el-icon-s-data', type: 'info' }
        ];
      } else if (this.userRole === 'admin') {
        return [
          { text: '用户管理', path: '/admin/user-manage', icon: 'el-icon-user', type: 'primary' },
          { text: '资源审核', path: '/admin/resource-audit', icon: 'el-icon-document-check', type: 'success' },
          { text: '系统分析', path: '/admin/system-analysis', icon: 'el-icon-s-data', type: 'warning' },
          { text: '个人中心', path: '/admin/center', icon: 'el-icon-user-solid', type: 'info' }
        ];
      }
      return [];
    }
  },
  methods: {
    updateTime() {
      const now = new Date();
      this.currentTime = now.toLocaleString('zh-CN', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      });
    }
  },
  created() {
    // 初始化时间
    this.updateTime();
    // 每秒更新时间
    this.timeInterval = setInterval(() => {
      this.updateTime();
    }, 1000);
    
    console.log('欢迎界面已加载');
  },
  beforeUnmount() {
    // 清除时间更新定时器
    if (this.timeInterval) {
      clearInterval(this.timeInterval);
    }
  }
};
</script>

<style lang="scss" scoped>
.welcome-container {
  position: relative;
  padding: 20px;
  background-color: #f5f7fa;
  min-height: calc(100vh - 160px);
  overflow: hidden;
}

/* 背景装饰 */
.background-decoration {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 0;
  overflow: hidden;
}

.circle {
  position: absolute;
  border-radius: 50%;
  opacity: 0.08;
  background: radial-gradient(circle, rgba(102, 126, 234, 0.5) 0%, rgba(118, 75, 162, 0) 70%);
  animation: float 20s ease-in-out infinite;
}

.circle-1 {
  width: 400px;
  height: 400px;
  top: -100px;
  left: -100px;
  animation-delay: 0s;
}

.circle-2 {
  width: 300px;
  height: 300px;
  top: 50%;
  right: -150px;
  animation-delay: -5s;
}

.circle-3 {
  width: 250px;
  height: 250px;
  bottom: -100px;
  left: 50%;
  animation-delay: -10s;
}

.circle-4 {
  width: 200px;
  height: 200px;
  top: 20%;
  left: 70%;
  animation-delay: -15s;
}

@keyframes float {
  0%, 100% { transform: translate(0, 0) rotate(0deg); }
  25% { transform: translate(50px, -50px) rotate(90deg); }
  50% { transform: translate(0, -100px) rotate(180deg); }
  75% { transform: translate(-50px, -50px) rotate(270deg); }
}

.welcome-card {
  position: relative;
  max-width: 1200px;
  margin: 0 auto;
  border-radius: 16px;
  border: none;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
  
  &:hover {
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.15);
  }
}

.welcome-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 16px 16px 0 0;
  
  .header-content {
    display: flex;
    align-items: center;
    padding: 30px 40px;
  }
  
  .header-icon {
    width: 70px;
    height: 70px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.2);
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 25px;
    font-size: 32px;
    backdrop-filter: blur(10px);
  }
  
  .header-text {
    flex: 1;
  }
  
  h2 {
    font-size: 28px;
    font-weight: 700;
    margin-bottom: 8px;
    color: white;
  }
  
  .current-time {
    font-size: 14px;
    opacity: 0.9;
    margin: 0;
  }
}

.welcome-content {
  padding: 40px;
}

.welcome-message {
  text-align: center;
  margin-bottom: 40px;
  
  .greeting {
    font-size: 28px;
    font-weight: 700;
    color: #2c3e50;
    margin-bottom: 15px;
    animation: fadeInUp 0.8s ease-out;
  }
  
  .role-message {
    font-size: 18px;
    color: #7f8c8d;
    margin: 0;
    animation: fadeInUp 0.8s ease-out 0.2s both;
  }
}

.welcome-stats {
  margin-bottom: 40px;
}

.stat-card {
  background: rgba(255, 255, 255, 0.9);
  border-radius: 16px;
  padding: 25px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  animation: fadeInUp 0.8s ease-out 0.3s both;
  
  &:hover {
    transform: translateY(-8px);
    box-shadow: 0 15px 35px rgba(0, 0, 0, 0.15);
  }
}

.stat-icon {
  width: 70px;
  height: 70px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 20px;
  font-size: 32px;
  color: white;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
  background-size: 200% 200%;
  transition: all 0.3s ease;
  
  &.exam {
    background: linear-gradient(135deg, #67c23a 0%, #85ce61 100%);
  }
  
  &.questions {
    background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
  }
  
  &.progress {
    background: linear-gradient(135deg, #e6a23c 0%, #ebb563 100%);
  }
  
  &:hover {
    transform: scale(1.05);
  }
}

.stat-info {
  flex: 1;
}

.stat-number {
  font-size: 32px;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 8px;
  line-height: 1;
}

.stat-label {
  font-size: 16px;
  color: #7f8c8d;
  font-weight: 500;
}

.welcome-quick-links {
  .section-title {
    display: flex;
    align-items: center;
    gap: 12px;
    font-size: 24px;
    font-weight: 600;
    color: #2c3e50;
    margin-bottom: 25px;
    animation: fadeInUp 0.8s ease-out 0.4s both;
    
    i {
      color: #f39c12;
      font-size: 20px;
    }
  }
}

.quick-link-btn {
  width: 100%;
  margin-bottom: 15px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 18px;
  font-size: 16px;
  font-weight: 500;
  border-radius: 12px;
  border: none;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  animation: fadeInUp 0.8s ease-out 0.5s both;
  
  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 12px 25px rgba(0, 0, 0, 0.2);
  }
  
  &:active {
    transform: translateY(-2px);
  }
}

/* 动画 */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .welcome-container {
    padding: 15px;
  }
  
  .welcome-header {
    .header-content {
      flex-direction: column;
      text-align: center;
      padding: 25px 20px;
      
      .header-icon {
        margin-right: 0;
        margin-bottom: 20px;
        width: 60px;
        height: 60px;
        font-size: 28px;
      }
    }
    
    h2 {
      font-size: 24px;
    }
  }
  
  .welcome-content {
    padding: 25px;
  }
  
  .welcome-message {
    .greeting {
      font-size: 24px;
    }
    
    .role-message {
      font-size: 16px;
    }
  }
  
  .stat-card {
    padding: 20px;
    flex-direction: column;
    text-align: center;
    
    .stat-icon {
      margin-right: 0;
      margin-bottom: 15px;
      width: 60px;
      height: 60px;
      font-size: 28px;
    }
  }
  
  .stat-number {
    font-size: 28px;
  }
  
  .quick-link-btn {
    padding: 15px;
    font-size: 15px;
  }
}

@media (max-width: 480px) {
  .welcome-header {
    h2 {
      font-size: 20px;
    }
  }
  
  .welcome-content {
    padding: 20px 15px;
  }
  
  .welcome-message {
    .greeting {
      font-size: 20px;
    }
    
    .role-message {
      font-size: 14px;
    }
  }
  
  .section-title {
    font-size: 20px !important;
  }
}
</style>