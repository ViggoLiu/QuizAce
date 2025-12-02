<template>
  <div class="student-dashboard">
    <!-- 欢迎区域 -->
    <div class="welcome-section">
      <h1>欢迎回来，{{ username }}！</h1>
      <p>今天是 {{ currentDate }}，让我们开始今天的学习之旅吧 📚</p>
    </div>

    <!-- 统计卡片区域 -->
    <div class="stats-section">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="stat-card" shadow="hover">
            <div class="stat-content">
              <div class="stat-icon question-icon">
                <i class="el-icon-edit-outline"></i>
              </div>
              <div class="stat-info">
                <div class="stat-number">{{ totalQuestions }}</div>
                <div class="stat-label">已完成题目</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card" shadow="hover">
            <div class="stat-content">
              <div class="stat-icon exam-icon">
                <i class="el-icon-document-copy"></i>
              </div>
              <div class="stat-info">
                <div class="stat-number">{{ totalExams }}</div>
                <div class="stat-label">已参加考试</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card" shadow="hover">
            <div class="stat-content">
              <div class="stat-icon correct-icon">
                <i class="el-icon-check"></i>
              </div>
              <div class="stat-info">
                <div class="stat-number">{{ correctRate }}%</div>
                <div class="stat-label">正确率</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card" shadow="hover">
            <div class="stat-content">
              <div class="stat-icon streak-icon">
                <i class="el-icon-date"></i>
              </div>
              <div class="stat-info">
                <div class="stat-number">{{ studyStreak }}</div>
                <div class="stat-label">学习 streak</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 主要内容区域 -->
    <div class="main-content">
      <!-- 左侧：推荐练习 -->
      <el-col :span="16">
        <el-card class="content-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>📝 推荐练习</span>
              <el-button type="text" @click="goToPractice">查看全部</el-button>
            </div>
          </template>
          <div class="practice-list">
            <div class="practice-item" v-for="(practice, index) in recommendedPractices" :key="index">
              <div class="practice-info">
                <h4>{{ practice.title }}</h4>
                <p>{{ practice.description }}</p>
                <div class="practice-meta">
                  <span class="meta-item">{{ practice.subject }}</span>
                  <span class="meta-item">{{ practice.difficulty }}</span>
                  <span class="meta-item">{{ practice.questionCount }} 题</span>
                </div>
              </div>
              <el-button type="primary" size="small" @click="startPractice(practice.id)">开始练习</el-button>
            </div>
          </div>
        </el-card>

        <!-- 学习进度 -->
        <el-card class="content-card" shadow="hover" style="margin-top: 20px;">
          <template #header>
            <div class="card-header">
              <span>📊 学习进度</span>
              <el-button type="text" @click="goToAnalysis">查看详情</el-button>
            </div>
          </template>
          <div class="progress-list">
            <div class="progress-item" v-for="(progress, index) in learningProgress" :key="index">
              <div class="progress-header">
                <span>{{ progress.subject }}</span>
                <span class="progress-percentage">{{ progress.percentage }}%</span>
              </div>
              <el-progress :percentage="progress.percentage" :color="progress.color" />
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 右侧：快速入口和最近活动 -->
      <el-col :span="8">
        <!-- 快速入口 -->
        <el-card class="content-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>🚀 快速入口</span>
            </div>
          </template>
          <div class="quick-links">
            <div class="quick-link-item" @click="goToExam">
              <div class="quick-link-icon exam-link">
                <i class="el-icon-trophy"></i>
              </div>
              <span>考试中心</span>
            </div>
            <div class="quick-link-item" @click="goToWrongBook">
              <div class="quick-link-icon wrong-link">
                <i class="el-icon-document-delete"></i>
              </div>
              <span>错题本</span>
            </div>
            <div class="quick-link-item" @click="goToResource">
              <div class="quick-link-icon resource-link">
                <i class="el-icon-document"></i>
              </div>
              <span>学习资源</span>
            </div>
            <div class="quick-link-item" @click="goToAnalysis">
              <div class="quick-link-icon analysis-link">
                <i class="el-icon-s-data"></i>
              </div>
              <span>学习分析</span>
            </div>
          </div>
        </el-card>

        <!-- 最近活动 -->
        <el-card class="content-card" shadow="hover" style="margin-top: 20px;">
          <template #header>
            <div class="card-header">
              <span>📅 最近活动</span>
            </div>
          </template>
          <div class="activity-list">
            <div class="activity-item" v-for="(activity, index) in recentActivities" :key="index">
              <div class="activity-time">{{ activity.time }}</div>
              <div class="activity-content">{{ activity.content }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useStore } from 'vuex'

const router = useRouter()
const store = useStore()

// 用户信息
const username = computed(() => store.getters.getUser?.username || '同学')

// 当前日期
const currentDate = computed(() => {
  const date = new Date()
  const options = { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' }
  return date.toLocaleDateString('zh-CN', options)
})

// 统计数据
const totalQuestions = ref(127)
const totalExams = ref(8)
const correctRate = ref(85)
const studyStreak = ref(12)

// 推荐练习
const recommendedPractices = ref([
  {
    id: 1,
    title: '数学函数专项练习',
    description: '针对函数概念和应用的专项训练',
    subject: '数学',
    difficulty: '中等',
    questionCount: 20
  },
  {
    id: 2,
    title: '英语语法综合训练',
    description: '涵盖时态、语态、从句等语法知识点',
    subject: '英语',
    difficulty: '简单',
    questionCount: 30
  },
  {
    id: 3,
    title: '物理力学提高练习',
    description: '牛顿运动定律和机械能守恒定律的应用',
    subject: '物理',
    difficulty: '困难',
    questionCount: 15
  }
])

// 学习进度
const learningProgress = ref([
  {
    subject: '数学',
    percentage: 75,
    color: '#409EFF'
  },
  {
    subject: '英语',
    percentage: 68,
    color: '#67C23A'
  },
  {
    subject: '物理',
    percentage: 56,
    color: '#E6A23C'
  },
  {
    subject: '化学',
    percentage: 82,
    color: '#F56C6C'
  }
])

// 最近活动
const recentActivities = ref([
  {
    time: '今天 09:30',
    content: '完成了数学函数专项练习，正确率 85%'
  },
  {
    time: '昨天 16:45',
    content: '参加了英语单元测试，得分 92 分'
  },
  {
    time: '昨天 14:20',
    content: '在错题本中添加了 3 道物理题'
  },
  {
    time: '前天 10:15',
    content: '学习了化学元素周期表的相关知识'
  }
])

// 方法
const goToPractice = () => {
  router.push('/student/questions')
}

const startPractice = (id) => {
  router.push(`/student/questions/practice/${id}`)
}

const goToExam = () => {
  router.push('/student/exam')
}

const goToWrongBook = () => {
  router.push('/student/wrong-book')
}

const goToResource = () => {
  router.push('/student/resource')
}

const goToAnalysis = () => {
  router.push('/student/analysis')
}
</script>

<style lang="scss" scoped>
.student-dashboard {
  padding: 20px;
}

.welcome-section {
  margin-bottom: 30px;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  color: white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);

  h1 {
    margin: 0 0 10px 0;
    font-size: 32px;
    font-weight: 600;
  }

  p {
    margin: 0;
    font-size: 16px;
    opacity: 0.9;
  }
}

.stats-section {
  margin-bottom: 30px;
}

.stat-card {
  height: 120px;
  border-radius: 12px;
  transition: transform 0.3s ease;

  &:hover {
    transform: translateY(-5px);
  }
}

.stat-content {
  display: flex;
  align-items: center;
  height: 100%;
}

.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: white;
  margin-right: 20px;
}

.question-icon {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.exam-icon {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.correct-icon {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.streak-icon {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.stat-info {
  flex: 1;
}

.stat-number {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  color: #666;
}

.main-content {
  display: flex;
  gap: 20px;
}

.content-card {
  border-radius: 12px;
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.practice-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.practice-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 15px;
  border: 1px solid #f0f0f0;
  border-radius: 8px;
  transition: background-color 0.3s ease;

  &:hover {
    background-color: #fafafa;
  }
}

.practice-info {
  flex: 1;
}

.practice-info h4 {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
}

.practice-info p {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #666;
  line-height: 1.5;
}

.practice-meta {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}

.meta-item {
  font-size: 12px;
  padding: 4px 10px;
  background-color: #f0f0f0;
  border-radius: 12px;
  color: #666;
}

.progress-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.progress-item {
  padding: 10px 0;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  font-size: 14px;
  font-weight: 500;
}

.progress-percentage {
  color: #409EFF;
}

.quick-links {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
}

.quick-link-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px 10px;
  border: 1px solid #f0f0f0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;

  &:hover {
    background-color: #f0f9ff;
    border-color: #409EFF;
    transform: translateY(-3px);
  }
}

.quick-link-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  color: white;
  margin-bottom: 10px;
}

.exam-link {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.wrong-link {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.resource-link {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.analysis-link {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.activity-item {
  padding: 10px;
  border-left: 3px solid #409EFF;
  background-color: #f9f9f9;
  border-radius: 0 8px 8px 0;
}

.activity-time {
  font-size: 12px;
  color: #999;
  margin-bottom: 5px;
}

.activity-content {
  font-size: 14px;
  color: #333;
  line-height: 1.5;
}
</style>
