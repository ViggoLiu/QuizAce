<template>
  <div class="teacher-analysis">
    <el-card shadow="never" class="summary-card-wrapper" v-loading="overviewLoading">
      <div class="summary-grid">
        <div class="summary-card" v-for="card in summaryCards" :key="card.label">
          <p class="summary-label">{{ card.label }}</p>
          <h2>{{ card.value }}</h2>
          <p class="summary-desc">{{ card.desc }}</p>
        </div>
      </div>
    </el-card>

    <el-row :gutter="16" class="chart-section">
      <el-col :span="12">
        <el-card shadow="never" class="chart-card" v-loading="overviewLoading">
          <template #header>
            <div class="card-header">
              <div>
                <h3>题目类型占比</h3>
                <p>客观 / 主观题数量分布</p>
              </div>
              <el-button type="primary" link size="small" @click="fetchOverview">刷新</el-button>
            </div>
          </template>
          <div v-if="questionTotal" ref="questionChartRef" class="chart-canvas"></div>
          <el-empty v-else description="暂无题目数据" />
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="never" class="chart-card" v-loading="overviewLoading">
          <template #header>
            <div class="card-header">
              <div>
                <h3>考试任务阶段</h3>
                <p>各科目考试处于的阶段分布</p>
              </div>
            </div>
          </template>
          <div v-if="assignmentBarData.categories.length" ref="assignmentChartRef" class="chart-canvas"></div>
          <el-empty v-else description="暂无考试任务数据" />
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" class="detail-section">
      <el-col :span="14">
        <el-card shadow="never" v-loading="overviewLoading">
          <template #header>
            <div class="card-header">
              <div>
                <h3>科目题量概览</h3>
                <p>掌握不同科目的题目覆盖情况</p>
              </div>
            </div>
          </template>
          <el-table :data="questionStats.subjects" border size="small">
            <el-table-column prop="subject_name" label="科目" min-width="140" />
            <el-table-column prop="total" label="总题量" width="90" />
            <el-table-column prop="objective" label="客观题" width="90" />
            <el-table-column prop="subjective" label="主观题" width="90" />
            <el-table-column label="最后更新">
              <template #default="{ row }">
                {{ formatDateTime(row.last_updated) }}
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-if="!questionStats.subjects.length" description="暂无科目数据" />
        </el-card>
      </el-col>
      <el-col :span="10">
        <el-card shadow="never" v-loading="overviewLoading">
          <template #header>
            <div class="card-header">
              <div>
                <h3>待批阅主观题</h3>
                <p>最近等待批阅的考试或练习</p>
              </div>
            </div>
          </template>
          <el-timeline v-if="pendingItems.length">
            <el-timeline-item
              v-for="item in pendingItems"
              :key="item.id"
              :timestamp="formatDateTime(item.submitted_at)"
              type="warning"
            >
              <div class="pending-item">
                <strong>{{ item.subject_name }}</strong>
                <p>{{ item.assignment_title || '练习提交' }} · {{ item.mode === 'exam' ? '考试' : '练习' }}</p>
                <small>{{ item.question_type === 'mixed' ? '组合题型' : '主观题' }}</small>
              </div>
            </el-timeline-item>
          </el-timeline>
          <el-empty v-else description="暂无待批阅记录" />
        </el-card>
      </el-col>
    </el-row>

    <el-card shadow="never" class="recent-card" v-loading="overviewLoading">
      <template #header>
        <div class="card-header">
          <div>
            <h3>近期考试任务</h3>
            <p>关注考试状态与待办工作量</p>
          </div>
        </div>
      </template>
      <el-table :data="assignmentStats.recent" border size="small">
        <el-table-column prop="title" label="考试" min-width="160" />
        <el-table-column prop="subject_name" label="科目" width="120" />
        <el-table-column prop="phase" label="阶段" width="100">
          <template #default="{ row }">
            <el-tag size="small" :type="phaseTagType(row.phase)">{{ phaseLabel(row.phase) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="时间" min-width="180">
          <template #default="{ row }">
            <div>{{ formatDateTime(row.start_time) }}</div>
            <div>{{ formatDateTime(row.end_time) }}</div>
          </template>
        </el-table-column>
        <el-table-column label="作答情况" width="150">
          <template #default="{ row }">
            <span>总作答 {{ row.total_attempts || 0 }}</span>
            <br />
            <span>待批阅 {{ row.pending_reviews || 0 }}</span>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!assignmentStats.recent.length" description="暂无考试任务" />
    </el-card>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import { get } from '@/util/request'

const overviewLoading = ref(false)
const overviewData = ref(null)
const questionChartRef = ref(null)
const assignmentChartRef = ref(null)
let questionChartInstance = null
let assignmentChartInstance = null

const defaultQuestionStats = { total: 0, objective: 0, subjective: 0, subjects: [] }
const defaultAssignmentStats = {
  total: 0,
  status: { draft: 0, published: 0, closed: 0 },
  phase: { upcoming: 0, ongoing: 0, ended: 0 },
  subjects: [],
  recent: [],
}

const questionStats = computed(() => overviewData.value?.question_stats || defaultQuestionStats)
const assignmentStats = computed(() => overviewData.value?.assignment_stats || defaultAssignmentStats)
const pendingItems = computed(() => overviewData.value?.pending_reviews?.items || [])
const questionTotal = computed(() => questionStats.value.total || 0)

const summaryCards = computed(() => {
  const pendingTotal = overviewData.value?.pending_reviews?.total || 0
  return [
    {
      label: '题库条目',
      value: questionStats.value.total || 0,
      desc: `客观 ${questionStats.value.objective || 0} · 主观 ${questionStats.value.subjective || 0}`,
    },
    {
      label: '考试任务',
      value: assignmentStats.value.total || 0,
      desc: `进行中 ${assignmentStats.value.phase?.ongoing || 0} · 待开始 ${assignmentStats.value.phase?.upcoming || 0}`,
    },
    {
      label: '待批阅',
      value: pendingTotal,
      desc: pendingTotal ? '请尽快完成批阅' : '暂无待批阅试卷',
    },
  ]
})

const questionChartData = computed(() => [
  { value: questionStats.value.objective || 0, name: '客观题' },
  { value: questionStats.value.subjective || 0, name: '主观题' },
])

const assignmentBarData = computed(() => {
  const subjects = assignmentStats.value.subjects || []
  return {
    categories: subjects.map((item) => item.subject_name || '未分类'),
    upcoming: subjects.map((item) => item.upcoming || 0),
    ongoing: subjects.map((item) => item.ongoing || 0),
    ended: subjects.map((item) => item.ended || 0),
  }
})

const renderQuestionChart = () => {
  if (!questionChartRef.value) return
  if (!questionChartInstance) {
    questionChartInstance = echarts.init(questionChartRef.value)
  }
  const hasData = questionChartData.value.some((item) => item.value > 0)
  if (!hasData) {
    questionChartInstance.clear()
    return
  }
  questionChartInstance.setOption({
    tooltip: { trigger: 'item' },
    legend: { bottom: 0 },
    series: [
      {
        type: 'pie',
        radius: ['50%', '80%'],
        itemStyle: { borderRadius: 8, borderColor: '#fff', borderWidth: 2 },
        label: { formatter: '{b}\n{d}%' },
        data: questionChartData.value,
      },
    ],
  })
}

const renderAssignmentChart = () => {
  if (!assignmentChartRef.value) return
  if (!assignmentChartInstance) {
    assignmentChartInstance = echarts.init(assignmentChartRef.value)
  }
  if (!assignmentBarData.value.categories.length) {
    assignmentChartInstance.clear()
    return
  }
  assignmentChartInstance.setOption({
    tooltip: { trigger: 'axis' },
    legend: { bottom: 0 },
    grid: { left: 40, right: 20, top: 20, bottom: 50 },
    xAxis: {
      type: 'category',
      data: assignmentBarData.value.categories,
      axisLabel: { interval: 0, rotate: 20 },
    },
    yAxis: { type: 'value', minInterval: 1 },
    series: [
      {
        name: '待开始',
        type: 'bar',
        stack: 'phase',
        data: assignmentBarData.value.upcoming,
        emphasis: { focus: 'series' },
      },
      {
        name: '进行中',
        type: 'bar',
        stack: 'phase',
        data: assignmentBarData.value.ongoing,
      },
      {
        name: '已结束',
        type: 'bar',
        stack: 'phase',
        data: assignmentBarData.value.ended,
      },
    ],
  })
}

watch(questionChartData, async () => {
  await nextTick()
  renderQuestionChart()
})

watch(assignmentBarData, async () => {
  await nextTick()
  renderAssignmentChart()
})

const formatDateTime = (value) => {
  if (!value) return '-'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return '-'
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  const h = String(date.getHours()).padStart(2, '0')
  const mi = String(date.getMinutes()).padStart(2, '0')
  return `${y}-${m}-${d} ${h}:${mi}`
}

const phaseLabel = (phase) => {
  if (phase === 'upcoming') return '未开始'
  if (phase === 'ongoing') return '进行中'
  if (phase === 'ended') return '已结束'
  return phase || '-'
}

const phaseTagType = (phase) => {
  if (phase === 'ongoing') return 'success'
  if (phase === 'upcoming') return 'info'
  return 'warning'
}

const fetchOverview = async () => {
  overviewLoading.value = true
  try {
    const response = await get('/exam/dashboard/teacher/overview/')
    if (response.data?.code === 200) {
      overviewData.value = response.data.data || null
    } else {
      ElMessage.error(response.data?.info || '获取教学分析失败')
    }
  } catch (error) {
    console.error(error)
    ElMessage.error('获取教学分析失败，请稍后重试')
  } finally {
    overviewLoading.value = false
  }
}

const handleResize = () => {
  questionChartInstance?.resize()
  assignmentChartInstance?.resize()
}

onMounted(() => {
  fetchOverview()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  questionChartInstance?.dispose()
  assignmentChartInstance?.dispose()
  questionChartInstance = null
  assignmentChartInstance = null
})
</script>

<style scoped lang="scss">
.teacher-analysis {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.summary-card-wrapper {
  border-radius: 18px;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 16px;
}

.summary-card {
  border: 1px solid #e1e8ff;
  border-radius: 16px;
  padding: 16px;
  background: linear-gradient(135deg, #f8fbff, #fdfdff);
}

.summary-label {
  margin: 0;
  font-size: 14px;
  color: #6b748d;
}

.summary-card h2 {
  margin: 6px 0;
  font-size: 28px;
  color: #1b2a4e;
}

.summary-desc {
  margin: 0;
  color: #8a92ab;
  font-size: 13px;
}

.chart-section,
.detail-section {
  align-items: stretch;
}

.chart-card {
  border-radius: 18px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card-header h3 {
  margin: 0;
}

.card-header p {
  margin: 4px 0 0;
  color: #8c96b5;
}

.chart-canvas {
  height: 320px;
}

.pending-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.pending-item p {
  margin: 0;
  color: #636c8c;
}

.pending-item small {
  color: #9aa1b9;
}

.recent-card {
  border-radius: 18px;
}

:deep(.el-table) {
  margin-top: 8px;
}
</style>
