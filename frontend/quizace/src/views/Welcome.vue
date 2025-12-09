<template>
  <div class="dashboard-home">
    <div class="background-decoration">
      <div class="circle circle-1"></div>
      <div class="circle circle-2"></div>
      <div class="circle circle-3"></div>
      <div class="circle circle-4"></div>
    </div>

    <section class="hero-section">
      <div class="hero-profile">
        <div class="avatar-wrapper">
          <img v-if="userAvatar" :src="userAvatar" alt="avatar" />
          <div v-else class="avatar-fallback">{{ userInitial }}</div>
        </div>
        <div class="hero-text">
          <p class="hero-greeting">{{ greetingText }}</p>
          <h1>{{ userName }}</h1>
          <div class="hero-meta">
            <el-tag size="small" type="warning">{{ roleLabel }}</el-tag>
            <span class="meta-item">
              <i class="el-icon-time"></i>
              {{ currentTime }}
            </span>
          </div>
        </div>
      </div>
      <div class="hero-stats">
        <div class="hero-stat" v-for="stat in heroStats" :key="stat.label">
          <span class="stat-label">{{ stat.label }}</span>
          <strong class="stat-value">{{ stat.value }}</strong>
          <small class="stat-desc">{{ stat.desc }}</small>
        </div>
      </div>
    </section>

    <section class="info-section">
      <div class="section-header">
        <div>
          <h2>{{ overviewTitle }}</h2>
          <p>{{ overviewSubtitle }}</p>
        </div>
      </div>
      <el-row :gutter="20">
        <el-col :xs="24" :sm="12" :md="8" v-for="card in statCards" :key="card.label">
          <div class="stat-card" :class="card.theme">
            <div class="stat-card-icon">
              <i :class="card.icon"></i>
            </div>
            <div class="stat-card-body">
              <p class="label">{{ card.label }}</p>
              <p class="value">{{ card.value }}</p>
              <p class="desc">{{ card.desc }}</p>
            </div>
          </div>
        </el-col>
      </el-row>
    </section>

    <section class="info-section highlights" v-if="highlightCards.length">
      <div class="section-header">
        <div>
          <h2>{{ highlightTitle }}</h2>
          <p>{{ highlightSubtitle }}</p>
        </div>
      </div>
      <el-row :gutter="20">
        <el-col :xs="24" :md="12" v-for="item in highlightCards" :key="item.title">
          <div class="highlight-card">
            <div class="highlight-badge">{{ item.badge }}</div>
            <div>
              <h3>{{ item.title }}</h3>
              <p>{{ item.desc }}</p>
              <span class="meta">{{ item.meta }}</span>
            </div>
            <el-button type="primary" text size="small" @click="navigate(item.path)">
              {{ item.action }}
            </el-button>
          </div>
        </el-col>
      </el-row>
    </section>

    <section class="info-section quick-launch">
      <div class="section-header">
        <div>
          <h2>
            <i class="el-icon-lightning"></i>
            快速开始
          </h2>
          <p>常用入口一键直达</p>
        </div>
      </div>
      <el-row :gutter="16">
        <el-col
          :xs="24"
          :sm="12"
          :md="6"
          v-for="(link, index) in quickLinks"
          :key="index"
        >
          <el-button
            class="quick-link-btn"
            :type="link.type"
            :icon="link.icon"
            @click="$router.push(link.path)"
          >
            {{ link.text }}
          </el-button>
        </el-col>
      </el-row>
    </section>
  </div>
</template>

<script>
import { getMediaBaseUrl, get } from '@/util/request.js'
const ROLE_CONFIGS = {
  student: {
    heroStats: [
      { label: '进行中的考试', value: '0', desc: '请关注考试中心' },
      { label: '练习完成数', value: '0', desc: '坚持练习收获更多' },
      { label: '学习进度', value: '0%', desc: '保持稳定输出' }
    ],
    statCards: [
      { label: '模拟练习', value: '0 套', desc: '全部练习记录可回顾', icon: 'el-icon-edit-outline', theme: 'primary' },
      { label: '错题本', value: '0 题', desc: '复盘薄弱知识点', icon: 'el-icon-document-delete', theme: 'warning' },
      { label: '学习分析', value: '即将更新', desc: '掌握你的成长曲线', icon: 'el-icon-data-analysis', theme: 'info' }
    ],
    highlights: [
      { badge: '考试提醒', title: '暂无考试安排', desc: '若有新考试会立刻提醒你', meta: '建议先去模拟练习热身', path: '/student/exam', action: '前往考试中心' },
      { badge: '成绩追踪', title: '学习轨迹待开启', desc: '完成练习后即可查看表现', meta: '练习越多数据越丰富', path: '/student/analysis', action: '查看分析' }
    ],
    overviewTitle: '学习概览',
    overviewSubtitle: '随时掌握考试与练习状态',
    highlightTitle: '学习提醒',
    highlightSubtitle: '跟进你的近期计划'
  },
  teacher: {
    heroStats: [
      { label: '题库条目', value: '0', desc: '可继续扩充题库' },
      { label: '待批阅试卷', value: '0', desc: '阅卷完成更高效' },
      { label: '教学活动', value: '0 场', desc: '合理安排教学节奏' }
    ],
    statCards: [
      { label: '题目管理', value: '0 道', desc: '覆盖单选/多选/主观题', icon: 'el-icon-notebook-1', theme: 'primary' },
      { label: '考试发布', value: '0 场', desc: '可快速生成线上考试', icon: 'el-icon-trophy', theme: 'success' },
      { label: '教学分析', value: '即将更新', desc: '掌握班级整体表现', icon: 'el-icon-data-analysis', theme: 'info' }
    ],
    highlights: [
      { badge: '阅卷提醒', title: '暂无待批阅试卷', desc: '学生交卷后会立即提醒', meta: '保持通知开启以免错过', path: '/teacher/marking', action: '进入阅卷' },
      { badge: '发布计划', title: '创建下一场考试', desc: '制定一份新的考试任务', meta: '支持多题型组合', path: '/teacher/exam-manage', action: '去发布' }
    ],
    overviewTitle: '教学概览',
    overviewSubtitle: '帮助老师掌握题库与考试动态',
    highlightTitle: '工作提醒',
    highlightSubtitle: '关注待办事项与课程计划'
  },
  admin: {
    heroStats: [
      { label: '入驻用户', value: '0', desc: '含学生和老师' },
      { label: '待审核资源', value: '0', desc: '请至资源审核处理' },
      { label: '论坛待处理', value: '0', desc: '保持社区健康' }
    ],
    statCards: [
      { label: '用户管理', value: '0 人', desc: '账号启停、角色调整', icon: 'el-icon-user', theme: 'primary' },
      { label: '资源审核', value: '0 条', desc: '确保资料质量可靠', icon: 'el-icon-document-checked', theme: 'success' },
      { label: '论坛管理', value: '0 条', desc: '处理不当发言', icon: 'el-icon-message-solid', theme: 'warning' }
    ],
    highlights: [
      { badge: '资源提醒', title: '暂无待审核资源', desc: '资源提交后将出现在此', meta: '合理安排审核时间', path: '/admin/resource-audit', action: '前往审核' },
      { badge: '社区提醒', title: '论坛运行良好', desc: '如有举报信息将出现这里', meta: '可定期巡查发言', path: '/admin/forum-manage', action: '进入论坛管理' }
    ],
    overviewTitle: '运营概览',
    overviewSubtitle: '快速掌握平台运行态势',
    highlightTitle: '待办提醒',
    highlightSubtitle: '及时处理重要事件'
  }
}

export default {
  name: 'Welcome',
  data() {
    return {
      currentTime: '',
      adminMetrics: null,
      adminMetricsLoading: false,
      teacherOverview: null,
      teacherOverviewLoading: false,
      studentOverview: null,
      studentOverviewLoading: false
    }
  },
  mounted() {
    this.refreshUserInfo()
  },
  computed: {
    getUser() {
      return this.$store.state.user
    },
    userRole() {
      return this.$store.getters.getUserRole
    },
    userName() {
      return this.getUser?.username || '用户'
    },
    userAvatar() {
      return this.formatAvatar(this.getUser?.avatar)
    },
    userInitial() {
      return this.userName ? this.userName.slice(0, 1).toUpperCase() : 'U'
    },
    roleLabel() {
      const map = { student: '学生端', teacher: '教师端', admin: '管理员端' }
      return map[this.userRole] || '访客'
    },
    greetingText() {
      const map = {
        student: '欢迎回来，继续保持学习节奏',
        teacher: '老师好，祝您教学顺利',
        admin: '管理员好，平台运营辛苦啦'
      }
      return map[this.userRole] || '欢迎回来'
    },
    roleConfig() {
      return ROLE_CONFIGS[this.userRole] || {
        heroStats: [],
        statCards: [],
        highlights: [],
        overviewTitle: '概览',
        overviewSubtitle: '暂无数据',
        highlightTitle: '提醒',
        highlightSubtitle: ''
      }
    },
    heroStats() {
      if (this.userRole === 'teacher' && this.teacherOverview) {
        const questionStats = this.teacherOverview.question_stats || {}
        const assignmentStats = this.teacherOverview.assignment_stats || {}
        const pendingTotal = this.teacherOverview.pending_reviews?.total || 0
        return [
          {
            label: '题库条目',
            value: `${questionStats.total || 0}`,
            desc: `客观 ${questionStats.objective || 0} · 主观 ${questionStats.subjective || 0}`
          },
          {
            label: '待批阅试卷',
            value: `${pendingTotal}`,
            desc: pendingTotal ? '请尽快完成批阅' : '暂无需要批阅'
          },
          {
            label: '教学活动',
            value: `${assignmentStats.total || 0} 场`,
            desc: `进行中 ${assignmentStats.phase?.ongoing || 0} · 待开始 ${assignmentStats.phase?.upcoming || 0}`
          }
        ]
      }
      if (this.userRole === 'student' && this.studentOverview) {
        const examStats = this.studentOverview.exam_stats || {}
        const practiceStats = this.studentOverview.practice_stats || {}
        return [
          {
            label: '进行中的考试',
            value: `${examStats.ongoing || 0}`,
            desc: `已完成 ${examStats.completed || 0} 场 · 待开始 ${examStats.upcoming || 0} 场`
          },
          {
            label: '练习完成数',
            value: `${practiceStats.completed || 0}`,
            desc: `总练习 ${practiceStats.total || 0}`
          },
          {
            label: '学习进度',
            value: `${practiceStats.progress_percent || 0}%`,
            desc: '根据近7天练习计算'
          }
        ]
      }
      if (this.userRole === 'admin' && this.adminMetrics) {
        const student = this.adminMetrics.student_count || 0
        const teacher = this.adminMetrics.teacher_count || 0
        const pendingResources = this.adminMetrics.pending_resource_count || 0
        const forumPending = this.adminMetrics.forum_comment_count || 0
        return [
          {
            label: '入驻用户',
            value: `${student + teacher}`,
            desc: `学生 ${student} · 老师 ${teacher}`
          },
          {
            label: '待审核资源',
            value: `${pendingResources}`,
            desc: '请至资源审核处理'
          },
          {
            label: '论坛待处理',
            value: `${forumPending} 条评论`,
            desc: '当前社区评论总量'
          }
        ]
      }
      return this.roleConfig.heroStats
    },
    statCards() {
      const cards = this.roleConfig.statCards.map(card => ({ ...card }))
      if (this.userRole === 'teacher' && this.teacherOverview) {
        const questionStats = this.teacherOverview.question_stats || {}
        const assignmentStats = this.teacherOverview.assignment_stats || {}
        const pendingTotal = this.teacherOverview.pending_reviews?.total || 0
        const subjectCount = (questionStats.subjects || []).length
        return cards.map(card => {
          const next = { ...card }
          if (card.label === '题目管理') {
            next.value = `${questionStats.total || 0} 道`
            next.desc = `覆盖 ${subjectCount} 个科目`
          } else if (card.label === '考试发布') {
            next.value = `${assignmentStats.total || 0} 场`
            next.desc = `进行中 ${assignmentStats.phase?.ongoing || 0} · 待开始 ${assignmentStats.phase?.upcoming || 0}`
          } else if (card.label === '教学分析') {
            next.value = pendingTotal ? `${pendingTotal} 份` : '实时更新'
            next.desc = pendingTotal ? '主观题等待批阅' : '暂无待批阅试卷'
          }
          return next
        })
      }
      if (this.userRole === 'student' && this.studentOverview) {
        const practiceStats = this.studentOverview.practice_stats || {}
        const wrongBookCount = this.studentOverview.wrong_book_count || 0
        const pendingReviews = this.studentOverview.pending_reviews || 0
        return cards.map(card => {
          const next = { ...card }
          if (card.label === '模拟练习') {
            next.value = `${practiceStats.total || 0} 套`
            next.desc = `近7天完成 ${practiceStats.recent_completed || 0} 套`
          } else if (card.label === '错题本') {
            next.value = `${wrongBookCount} 题`
            next.desc = pendingReviews ? `有 ${pendingReviews} 题待老师批阅` : '复盘薄弱知识点'
          } else if (card.label === '学习分析') {
            next.value = `${practiceStats.progress_percent || 0}%`
            next.desc = '掌握你的成长曲线'
          }
          return next
        })
      }
      if (this.userRole === 'admin' && this.adminMetrics) {
        const student = this.adminMetrics.student_count || 0
        const teacher = this.adminMetrics.teacher_count || 0
        const admin = this.adminMetrics.admin_count || 0
        const pendingResources = this.adminMetrics.pending_resource_count || 0
        const totalResources = this.adminMetrics.total_resource_count || 0
        const forumPending = this.adminMetrics.forum_comment_count || 0

        return cards.map(card => {
          const next = { ...card }
          if (card.label === '用户管理') {
            next.value = `${student + teacher + admin} 人`
            next.desc = `学生 ${student} · 老师 ${teacher} · 管理员 ${admin}`
          } else if (card.label === '资源审核') {
            next.value = `${pendingResources} 条`
            next.desc = `累计 ${totalResources} 条资源`
          } else if (card.label === '论坛管理') {
            next.value = `${forumPending} 条`
            next.desc = '当前论坛评论总量'
          }
          return next
        })
      }
      return cards
    },
    highlightCards() {
      if (this.userRole === 'teacher' && this.teacherOverview) {
        const pendingTotal = this.teacherOverview.pending_reviews?.total || 0
        const pendingSubjects = new Set(
          (this.teacherOverview.pending_reviews?.items || [])
            .map(item => item.subject_name)
            .filter(Boolean)
        )
        const recentAssignments = this.teacherOverview.assignment_stats?.recent || []
        const upcomingAssignment = recentAssignments.find(item => item.phase === 'upcoming') || recentAssignments[0]
        return [
          {
            badge: '阅卷提醒',
            title: pendingTotal ? `有 ${pendingTotal} 份主观题待批阅` : '暂无待批阅试卷',
            desc: pendingTotal ? '及时处理以免影响成绩发布' : '学生交卷后会立即提醒',
            meta: pendingTotal ? `涉及 ${pendingSubjects.size || 0} 个科目` : '保持通知开启以免错过',
            path: '/teacher/marking',
            action: '进入阅卷'
          },
          {
            badge: '发布计划',
            title: upcomingAssignment
              ? `${upcomingAssignment.title} · ${this.phaseLabel(upcomingAssignment.phase)}`
              : '创建下一场考试',
            desc: upcomingAssignment
              ? `开始时间 ${this.formatDateTime(upcomingAssignment.start_time)}`
              : '制定一份新的考试任务',
            meta: upcomingAssignment
              ? `当前待批阅 ${upcomingAssignment.pending_reviews || 0}`
              : '支持多题型组合',
            path: '/teacher/exam-manage',
            action: '去发布'
          }
        ]
      }
      if (this.userRole === 'student' && this.studentOverview) {
        const examStats = this.studentOverview.exam_stats || {}
        const practiceStats = this.studentOverview.practice_stats || {}
        const pendingReviews = this.studentOverview.pending_reviews || 0
        const recentAssignments = examStats.recent || []
        const nextExam = recentAssignments.find(item => item.student_phase !== 'completed' && item.phase !== 'ended') || null
        return [
          {
            badge: '考试提醒',
            title: nextExam ? `${nextExam.title}` : '暂无待完成考试',
            desc: nextExam
              ? `${this.phaseLabel(nextExam.student_phase || nextExam.phase)} · ${nextExam.subject_name || '未分科'}`
              : '当前没有需要完成的考试任务',
            meta: nextExam
              ? `开始时间 ${this.formatDateTime(nextExam.start_time)}`
              : '若发布新考试会第一时间提示',
            path: '/student/exam',
            action: '前往考试中心'
          },
          {
            badge: '成绩追踪',
            title: `近7天完成 ${practiceStats.recent_completed || 0} 套练习`,
            desc: pendingReviews ? `有 ${pendingReviews} 题待老师批阅` : '练习越多数据越丰富',
            meta: `整体进度 ${practiceStats.progress_percent || 0}%`,
            path: '/student/analysis',
            action: '查看分析'
          }
        ]
      }
      const cards = this.roleConfig.highlights.map(item => ({ ...item }))
      if (this.userRole === 'admin' && this.adminMetrics) {
        const pendingResources = this.adminMetrics.pending_resource_count || 0
        const totalResources = this.adminMetrics.total_resource_count || 0
        const forumPending = this.adminMetrics.forum_comment_count || 0

        return cards.map(card => {
          const next = { ...card }
          if (card.badge === '资源提醒') {
            if (pendingResources > 0) {
              next.title = `有 ${pendingResources} 条待审核资源`
              next.desc = '请尽快处理，保障资料质量'
              next.meta = `累计 ${totalResources} 条资源`
            } else {
              next.title = '暂无待审核资源'
              next.desc = '资源提交后将出现在此'
              next.meta = '保持关注审核队列'
            }
          } else if (card.badge === '社区提醒') {
            if (forumPending > 0) {
              next.title = `论坛有 ${forumPending} 条评论`
              next.desc = '可从论坛管理快速巡查'
              next.meta = '如遇异常及时处理'
            } else {
              next.title = '论坛运行良好'
              next.desc = '暂无评论需处理'
              next.meta = '如有举报信息会出现这里'
            }
          }
          return next
        })
      }
      return cards
    },
    overviewTitle() {
      return this.roleConfig.overviewTitle
    },
    overviewSubtitle() {
      return this.roleConfig.overviewSubtitle
    },
    highlightTitle() {
      return this.roleConfig.highlightTitle
    },
    highlightSubtitle() {
      return this.roleConfig.highlightSubtitle
    },
    quickLinks() {
      if (this.userRole === 'student') {
        return [
          { text: '考试中心', path: '/student/exam', icon: 'el-icon-trophy', type: 'primary' },
          { text: '模拟练习', path: '/student/questions', icon: 'el-icon-edit-outline', type: 'success' },
          { text: '错题本', path: '/student/wrong-book', icon: 'el-icon-document-delete', type: 'warning' },
          { text: '学习分析', path: '/student/analysis', icon: 'el-icon-s-data', type: 'info' }
        ]
      }
      if (this.userRole === 'teacher') {
        return [
          { text: '题目管理', path: '/teacher/questions', icon: 'el-icon-edit', type: 'primary' },
          { text: '考试发布', path: '/teacher/exam-manage', icon: 'el-icon-trophy', type: 'success' },
          { text: '阅卷管理', path: '/teacher/marking', icon: 'el-icon-document-checked', type: 'warning' },
          { text: '教学分析', path: '/teacher/analysis', icon: 'el-icon-s-data', type: 'info' }
        ]
      }
      if (this.userRole === 'admin') {
        return [
          { text: '用户管理', path: '/admin/user-manage', icon: 'el-icon-user', type: 'primary' },
          { text: '资源审核', path: '/admin/resource-audit', icon: 'el-icon-document-checked', type: 'success' },
          { text: '论坛管理', path: '/admin/forum-manage', icon: 'el-icon-message-solid', type: 'warning' }
        ]
      }
      return []
    }
  },
  watch: {
    userRole: {
      immediate: true,
      handler(role) {
        if (role === 'admin') {
          if (!this.adminMetrics && !this.adminMetricsLoading) {
            this.fetchAdminOverview()
          }
        } else {
          this.adminMetrics = null
        }
        if (role === 'teacher') {
          if (!this.teacherOverview && !this.teacherOverviewLoading) {
            this.fetchTeacherOverview()
          }
        } else {
          this.teacherOverview = null
        }
        if (role === 'student') {
          if (!this.studentOverview && !this.studentOverviewLoading) {
            this.fetchStudentOverview()
          }
        } else {
          this.studentOverview = null
        }
      }
    }
  },
  methods: {
    updateTime() {
      const now = new Date()
      this.currentTime = now.toLocaleString('zh-CN', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      })
    },
    navigate(path) {
      if (path) {
        this.$router.push(path)
      }
    },
    formatAvatar(path) {
      if (!path) return ''
      if (/^https?:/i.test(path)) {
        return path
      }
      const base = getMediaBaseUrl()
      return path.startsWith('/') ? `${base}${path}` : `${base}/${path}`
    },
    formatDateTime(value) {
      if (!value) return '-'
      const date = new Date(value)
      if (Number.isNaN(date.getTime())) return '-'
      const y = date.getFullYear()
      const m = String(date.getMonth() + 1).padStart(2, '0')
      const d = String(date.getDate()).padStart(2, '0')
      const h = String(date.getHours()).padStart(2, '0')
      const mi = String(date.getMinutes()).padStart(2, '0')
      return `${y}-${m}-${d} ${h}:${mi}`
    },
    phaseLabel(phase) {
      if (phase === 'upcoming') return '未开始'
      if (phase === 'ongoing') return '进行中'
      if (phase === 'ended') return '已结束'
      if (phase === 'completed') return '已完成'
      return phase || '-'
    },
    async refreshUserInfo() {
      try {
        const res = await get('/user/info/')
        if (res.data?.code === 200 && res.data.data) {
          this.$store.commit('setUser', res.data.data)
        }
      } catch (error) {
        console.warn('刷新用户信息失败', error)
      }
    },
    async fetchTeacherOverview(force = false) {
      if (this.userRole !== 'teacher') return
      if (this.teacherOverviewLoading) return
      if (this.teacherOverview && !force) return
      this.teacherOverviewLoading = true
      try {
        const response = await get('/exam/dashboard/teacher/overview/')
        if (response?.data?.code === 200) {
          this.teacherOverview = response.data.data || null
        } else {
          console.error('获取教师概览失败', response?.data)
        }
      } catch (error) {
        console.error('获取教师概览失败', error)
      } finally {
        this.teacherOverviewLoading = false
      }
    },
    async fetchStudentOverview(force = false) {
      if (this.userRole !== 'student') return
      if (this.studentOverviewLoading) return
      if (this.studentOverview && !force) return
      this.studentOverviewLoading = true
      try {
        const response = await get('/exam/dashboard/student/overview/')
        if (response?.data?.code === 200) {
          this.studentOverview = response.data.data || null
        } else {
          console.error('获取学生概览失败', response?.data)
        }
      } catch (error) {
        console.error('获取学生概览失败', error)
      } finally {
        this.studentOverviewLoading = false
      }
    },
    async fetchAdminOverview() {
      if (this.userRole !== 'admin' || this.adminMetricsLoading) return
      this.adminMetricsLoading = true
      try {
        const response = await get('/user/admin/overview/')
        if (response?.data?.code === 200) {
          this.adminMetrics = response.data.data || null
        } else {
          console.error('获取管理员统计失败', response?.data)
        }
      } catch (error) {
        console.error('获取管理员统计失败', error)
      } finally {
        this.adminMetricsLoading = false
      }
    }
  },
  created() {
    this.updateTime()
    this.timeInterval = setInterval(this.updateTime, 1000)
    if (this.userRole === 'admin' && !this.adminMetrics) {
      this.fetchAdminOverview()
    }
    if (this.userRole === 'teacher' && !this.teacherOverview) {
      this.fetchTeacherOverview()
    }
    if (this.userRole === 'student' && !this.studentOverview) {
      this.fetchStudentOverview()
    }
  },
  beforeUnmount() {
    if (this.timeInterval) {
      clearInterval(this.timeInterval)
    }
  }
}
</script>

<style lang="scss" scoped>
.dashboard-home {
  position: relative;
  padding: 24px;
  min-height: calc(100vh - 160px);
  background: #f5f7fb;
  overflow: hidden;
}

.background-decoration {
  position: absolute;
  inset: 0;
  z-index: 0;
  overflow: hidden;
}

.circle {
  position: absolute;
  border-radius: 50%;
  opacity: 0.08;
  background: radial-gradient(circle, rgba(79, 127, 255, 0.4) 0%, rgba(79, 127, 255, 0));
  animation: float 18s linear infinite;
}

.circle-1 { width: 420px; height: 420px; top: -120px; left: -120px; }
.circle-2 { width: 280px; height: 280px; top: 10%; right: -160px; animation-delay: -3s; }
.circle-3 { width: 240px; height: 240px; bottom: -140px; left: 25%; animation-delay: -6s; }
.circle-4 { width: 180px; height: 180px; top: 45%; right: 15%; animation-delay: -9s; }

.hero-section {
  position: relative;
  z-index: 1;
  background: linear-gradient(120deg, #5c8fff, #8b6ff5);
  color: #fff;
  border-radius: 24px;
  padding: 32px;
  margin-bottom: 24px;
  display: flex;
  flex-wrap: wrap;
  gap: 24px;
  box-shadow: 0 25px 60px rgba(92, 143, 255, 0.3);
}

.hero-profile {
  display: flex;
  align-items: center;
  gap: 20px;
  flex: 1 1 320px;
}

.avatar-wrapper {
  width: 96px;
  height: 96px;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.25);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  border: 2px solid rgba(255, 255, 255, 0.4);
  backdrop-filter: blur(6px);
}

.avatar-wrapper img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-fallback {
  font-size: 36px;
  font-weight: 700;
  color: #fff;
}

.hero-text h1 {
  margin: 4px 0 10px;
  font-size: 32px;
  font-weight: 700;
}

.hero-greeting {
  margin: 0;
  font-size: 16px;
  opacity: 0.85;
}

.hero-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  color: rgba(255, 255, 255, 0.85);
}

.meta-item i {
  margin-right: 4px;
}

.hero-stats {
  flex: 2 1 400px;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 16px;
}

.hero-stat {
  background: rgba(255, 255, 255, 0.12);
  border-radius: 16px;
  padding: 16px;
  backdrop-filter: blur(6px);
}

.stat-label {
  font-size: 14px;
  opacity: 0.85;
}

.stat-value {
  font-size: 28px;
  line-height: 1.2;
  margin: 8px 0;
  display: block;
}

.stat-desc {
  font-size: 13px;
  opacity: 0.8;
}

.info-section {
  position: relative;
  z-index: 1;
  background: #fff;
  border-radius: 20px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 12px 30px rgba(40, 65, 133, 0.08);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 18px;
}

.section-header h2 {
  margin: 0;
  font-size: 22px;
}

.section-header p {
  margin: 6px 0 0;
  color: #8690a3;
  font-size: 14px;
}

.stat-card {
  display: flex;
  gap: 16px;
  border-radius: 18px;
  padding: 16px;
  color: #1f2a44;
  border: 1px solid rgba(230, 235, 255, 0.9);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 16px 35px rgba(94, 116, 196, 0.15);
}

.stat-card-icon {
  width: 60px;
  height: 60px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  color: #fff;
}

.stat-card.primary .stat-card-icon { background: linear-gradient(135deg, #4f89ff, #6da0ff); }
.stat-card.success .stat-card-icon { background: linear-gradient(135deg, #42c79c, #60d7b0); }
.stat-card.warning .stat-card-icon { background: linear-gradient(135deg, #f6a623, #fdd256); }
.stat-card.info .stat-card-icon { background: linear-gradient(135deg, #7f7fff, #9c9cff); }

.stat-card-body .label {
  margin: 0;
  font-size: 15px;
  color: #5a6277;
}

.stat-card-body .value {
  margin: 6px 0;
  font-size: 24px;
  font-weight: 700;
}

.stat-card-body .desc {
  margin: 0;
  color: #9098b4;
  font-size: 13px;
}

.highlights .highlight-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 18px;
  border: 1px dashed #d8e3ff;
  border-radius: 16px;
}

.highlight-badge {
  padding: 6px 12px;
  border-radius: 12px;
  background: #eef3ff;
  color: #4f63ff;
  font-size: 12px;
  font-weight: 600;
}

.highlight-card h3 {
  margin: 0 0 6px;
}

.highlight-card p {
  margin: 0 0 4px;
  color: #626f91;
}

.highlight-card .meta {
  font-size: 13px;
  color: #a0a8c3;
}

.quick-launch .quick-link-btn {
  width: 100%;
  padding: 18px 12px;
  border-radius: 14px;
  font-size: 15px;
  font-weight: 600;
  transition: transform 0.2s ease;
}

.quick-launch .quick-link-btn:hover {
  transform: translateY(-4px);
}

@keyframes float {
  0% { transform: translate(0, 0); }
  50% { transform: translate(30px, -20px); }
  100% { transform: translate(0, 0); }
}

@media (max-width: 768px) {
  .dashboard-home { padding: 16px; }
  .hero-section { flex-direction: column; }
  .hero-stats { grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); }
}
</style>