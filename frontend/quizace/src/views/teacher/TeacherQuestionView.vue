<template>
  <div class="teacher-dashboard">
    <!-- 欢迎区域 -->
    <div class="welcome-section">
      <h1>欢迎回来，{{ username }}老师！</h1>
      <p>今天是 {{ currentDate }}，让我们开始今天的教学工作吧 📚</p>
    </div>

    <!-- 统计卡片区域 -->
    <div class="stats-section">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="stat-card" shadow="hover">
            <div class="stat-content">
              <div class="stat-icon question-icon">
                <i class="el-icon-document-add"></i>
              </div>
              <div class="stat-info">
                <div class="stat-number">{{ totalQuestions }}</div>
                <div class="stat-label">已发布题目</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card" shadow="hover">
            <div class="stat-content">
              <div class="stat-icon exam-icon">
                <i class="el-icon-trophy"></i>
              </div>
              <div class="stat-info">
                <div class="stat-number">{{ totalExams }}</div>
                <div class="stat-label">已创建考试</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card" shadow="hover">
            <div class="stat-content">
              <div class="stat-icon pending-icon">
                <i class="el-icon-time"></i>
              </div>
              <div class="stat-info">
                <div class="stat-number">{{ pendingMarks }}</div>
                <div class="stat-label">待批试卷</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card" shadow="hover">
            <div class="stat-content">
              <div class="stat-icon student-icon">
                <i class="el-icon-user"></i>
              </div>
              <div class="stat-info">
                <div class="stat-number">{{ totalStudents }}</div>
                <div class="stat-label">管理学生</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 主要内容区域 -->
    <div class="main-content">
      <!-- 左侧：待办事项和考试统计 -->
      <el-col :span="16">
        <!-- 待办事项 -->
        <el-card class="content-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>📋 待办事项</span>
              <el-button type="text" @click="goToTasks">查看全部</el-button>
            </div>
          </template>
          <div class="task-list">
            <div class="task-item" v-for="(task, index) in pendingTasks" :key="index">
              <el-checkbox v-model="task.completed">{{ task.title }}</el-checkbox>
              <div class="task-info">
                <span class="task-deadline">{{ task.deadline }}</span>
                <el-tag :type="task.priority === 'high' ? 'danger' : task.priority === 'medium' ? 'warning' : 'info'" size="small">
                  {{ task.priority === 'high' ? '高' : task.priority === 'medium' ? '中' : '低' }}优先级
                </el-tag>
              </div>
            </div>
          </div>
        </el-card>

        <!-- 考试统计 -->
        <el-card class="content-card" shadow="hover" style="margin-top: 20px;">
          <template #header>
            <div class="card-header">
              <span>📊 最近考试统计</span>
              <el-button type="text" @click="goToExamAnalysis">查看详情</el-button>
            </div>
          </template>
          <div class="exam-stats">
            <div class="exam-item" v-for="(exam, index) in recentExams" :key="index">
              <div class="exam-header">
                <h4>{{ exam.title }}</h4>
                <span class="exam-date">{{ exam.date }}</span>
              </div>
              <div class="exam-details">
                <div class="detail-item">
                  <span class="detail-label">参考人数：</span>
                  <span class="detail-value">{{ exam.participants }}</span>
                </div>
                <div class="detail-item">
                  <span class="detail-label">平均分数：</span>
                  <span class="detail-value">{{ exam.averageScore }}分</span>
                </div>
                <div class="detail-item">
                  <span class="detail-label">最高分：</span>
                  <span class="detail-value">{{ exam.highestScore }}分</span>
                </div>
              </div>
              <el-progress :percentage="exam.completionRate" color="#67C23A" />
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 右侧：快速入口和教学工具 -->
      <el-col :span="8">
        <!-- 快速入口 -->
        <el-card class="content-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>🚀 快速操作</span>
            </div>
          </template>
          <div class="quick-links">
            <div class="quick-link-item" @click="goToCreateExam">
              <div class="quick-link-icon exam-link">
                <i class="el-icon-document-copy"></i>
              </div>
              <span>创建考试</span>
            </div>
            <div class="quick-link-item" @click="goToMarking">
              <div class="quick-link-icon marking-link">
                <i class="el-icon-edit"></i>
              </div>
              <span>批改试卷</span>
            </div>
            <div class="quick-link-item" @click="goToQuestionBank">
              <div class="quick-link-icon question-link">
                <i class="el-icon-edit-outline"></i>
              </div>
              <span>题库管理</span>
            </div>
            <div class="quick-link-item" @click="goToStudentAnalysis">
              <div class="quick-link-icon analysis-link">
                <i class="el-icon-s-data"></i>
              </div>
              <span>学生分析</span>
            </div>
          </div>
        </el-card>

        <!-- 教学工具 -->
        <el-card class="content-card" shadow="hover" style="margin-top: 20px;">
          <template #header>
            <div class="card-header">
              <span>🛠️ 教学工具</span>
            </div>
          </template>
          <div class="tool-list">
            <div class="tool-item" v-for="(tool, index) in teachingTools" :key="index">
              <i :class="tool.icon" class="tool-icon"></i>
              <div class="tool-info">
                <h5>{{ tool.name }}</h5>
                <p>{{ tool.description }}</p>
              </div>
              <el-button type="primary" size="small" @click="useTool(tool.id)">使用</el-button>
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
const username = computed(() => store.getters.getUser?.username || '教师')

// 当前日期
const currentDate = computed(() => {
  const date = new Date()
  const options = { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' }
  return date.toLocaleDateString('zh-CN', options)
})

// 统计数据
const totalQuestions = ref(256)
const totalExams = ref(15)
const pendingMarks = ref(8)
const totalStudents = ref(42)

// 待办事项
const pendingTasks = ref([
  {
    id: 1,
    title: '批改数学单元测试试卷',
    deadline: '今天 17:00',
    priority: 'high',
    completed: false
  },
  {
    id: 2,
    title: '创建英语语法专项练习',
    deadline: '明天 12:00',
    priority: 'medium',
    completed: false
  },
  {
    id: 3,
    title: '审核学生提交的作业',
    deadline: '明天 18:00',
    priority: 'medium',
    completed: false
  },
  {
    id: 4,
    title: '更新物理题库',
    deadline: '本周日 23:59',
    priority: 'low',
    completed: false
  }
])

// 最近考试
const recentExams = ref([
  {
    id: 1,
    title: '数学函数单元测试',
    date: '2024-05-20',
    participants: 38,
    averageScore: 78.5,
    highestScore: 98,
    completionRate: 95
  },
  {
    id: 2,
    title: '英语阅读理解练习',
    date: '2024-05-18',
    participants: 42,
    averageScore: 82.3,
    highestScore: 95,
    completionRate: 100
  },
  {
    id: 3,
    title: '物理力学基础测试',
    date: '2024-05-15',
    participants: 35,
    averageScore: 72.1,
    highestScore: 92,
    completionRate: 83
  }
])

// 教学工具
const teachingTools = ref([
  {
    id: 1,
    name: '在线出题',
    description: '快速创建各种类型的题目',
    icon: 'el-icon-edit-outline'
  },
  {
    id: 2,
    name: '成绩分析',
    description: '自动生成考试成绩分析报告',
    icon: 'el-icon-chart'
  },
  {
    id: 3,
    name: '资源分享',
    description: '分享教学资源给学生',
    icon: 'el-icon-upload2'
  }
])

// 方法
const goToTasks = () => {
  // 跳转到任务管理页面
  console.log('跳转到任务管理页面')
}

const goToCreateExam = () => {
  router.push('/teacher/exam-manage')
}

const goToMarking = () => {
  router.push('/teacher/marking')
}

const goToQuestionBank = () => {
  router.push('/teacher/questions')
}

const goToStudentAnalysis = () => {
  router.push('/teacher/analysis')
}

const goToExamAnalysis = () => {
  // 跳转到考试分析页面
  console.log('跳转到考试分析页面')
}

const useTool = (toolId) => {
  // 使用教学工具
  console.log('使用教学工具:', toolId)
}
</script>

<style lang="scss" scoped>
.teacher-dashboard {
  padding: 20px;
}

.welcome-section {
  margin-bottom: 30px;
  padding: 20px;
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
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

.pending-icon {
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
}

.student-icon {
  background: linear-gradient(135deg, #30cfd0 0%, #330867 100%);
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

.task-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.task-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #f0f0f0;
}

.task-info {
  display: flex;
  gap: 15px;
  align-items: center;
}

.task-deadline {
  font-size: 14px;
  color: #666;
}

.exam-stats {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.exam-item {
  padding: 15px;
  border: 1px solid #f0f0f0;
  border-radius: 8px;
}

.exam-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.exam-header h4 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

.exam-date {
  font-size: 14px;
  color: #666;
}

.exam-details {
  display: flex;
  gap: 20px;
  margin-bottom: 15px;
  flex-wrap: wrap;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 5px;
}

.detail-label {
  font-size: 14px;
  color: #666;
}

.detail-value {
  font-size: 14px;
  font-weight: 600;
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
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.marking-link {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.question-link {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.analysis-link {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.tool-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.tool-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  border: 1px solid #f0f0f0;
  border-radius: 8px;
  transition: background-color 0.3s ease;

  &:hover {
    background-color: #fafafa;
  }
}

.tool-icon {
  font-size: 24px;
  color: #409EFF;
}

.tool-info {
  flex: 1;
}

.tool-info h5 {
  margin: 0 0 5px 0;
  font-size: 16px;
  font-weight: 600;
}

.tool-info p {
  margin: 0;
  font-size: 14px;
  color: #666;
  line-height: 1.4;
}
</style>
