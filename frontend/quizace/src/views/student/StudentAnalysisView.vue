<template>
  <div class="student-analysis">
    <el-row :gutter="16" class="analysis-grid">
      <el-col :span="14">
        <el-card shadow="never">
          <template #header>
            <div class="card-header">
              <div>
                <h3>全部历史记录</h3>
                <p>查看全部练习与考试的提交情况，按科目快速筛选。</p>
              </div>
              <div class="history-controls">
                <el-select
                  v-model="subjectFilter"
                  clearable
                  size="small"
                  placeholder="全部科目"
                  @change="handleSubjectChange"
                >
                  <el-option label="全部科目" value="" />
                  <el-option
                    v-for="subject in subjectOptions"
                    :key="subject.id"
                    :label="subject.name"
                    :value="subject.id"
                  />
                </el-select>
                <el-button type="primary" size="small" @click="refreshHistory">刷新</el-button>
              </div>
            </div>
          </template>
          <el-table :data="historyList" border v-loading="historyLoading" size="small">
            <el-table-column prop="subject_name" label="科目" width="140" />
            <el-table-column prop="mode" label="类型" width="90">
              <template #default="{ row }">
                <el-tag size="small" :type="row.mode === 'exam' ? 'danger' : 'info'">
                  {{ row.mode === 'exam' ? '考试' : '练习' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="question_type" label="题型" width="110">
              <template #default="{ row }">
                {{ row.question_type === 'objective' ? '客观题' : '主观题' }}
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">{{ statusLabel(row.status) }}</template>
            </el-table-column>
            <el-table-column prop="obtained_score" label="得分" width="110">
              <template #default="{ row }">
                <span v-if="row.question_type === 'objective'">{{ row.obtained_score }}/{{ row.total_score }}</span>
                <span v-else>{{ row.obtained_score || '--' }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="submitted_at" label="提交时间">
              <template #default="{ row }">{{ formatDateTime(row.submitted_at) }}</template>
            </el-table-column>
            <el-table-column label="操作" width="120">
              <template #default="{ row }">
                <el-button type="text" size="small" @click="viewDetail(row)">查看</el-button>
              </template>
            </el-table-column>
          </el-table>
          <div class="table-footer">
            <el-pagination
              background
              layout="prev, pager, next, sizes, total"
              :current-page="historyPagination.page"
              :page-size="historyPagination.pageSize"
              :total="historyPagination.total"
              :page-sizes="[5, 10, 20, 50]"
              @current-change="handlePageChange"
              @size-change="handlePageSizeChange"
            />
          </div>
        </el-card>
      </el-col>
      <el-col :span="10">
        <div class="insights-column">
          <el-card shadow="never" class="usage-card" v-loading="usageLoading">
            <template #header>
              <div class="card-header">
                <div>
                  <h3>学习资源时长分布</h3>
                  <p>最近的资源访问次数作为时长投入参考。</p>
                </div>
                <el-button type="primary" link size="small" @click="fetchUsageStats">刷新</el-button>
              </div>
            </template>
            <div class="usage-card__body" v-if="usageStats.length">
              <div class="usage-chart" ref="usageChartRef"></div>
              <ul class="usage-legend">
                <li v-for="(item, index) in usageStats" :key="item.course + index">
                  <span class="usage-legend__dot" :style="{ backgroundColor: getChartColor(index) }"></span>
                  <div class="usage-legend__meta">
                    <span class="usage-legend__name">{{ item.course }}</span>
                    <span class="usage-legend__value">{{ item.value }} 次访问 · {{ item.percentage }}%</span>
                  </div>
                </li>
              </ul>
              <p class="usage-total">合计 {{ totalUsage || 0 }} 次访问</p>
            </div>
            <el-empty v-else description="暂无学习资源使用记录" />
          </el-card>

          <el-card shadow="never" v-loading="pendingLoading">
            <template #header>
              <div class="card-header">
                <div>
                  <h3>待批阅主观题</h3>
                  <p>这些主观题已提交，等待老师批阅。</p>
                </div>
              </div>
            </template>
            <el-empty v-if="!pendingList.length" description="暂无待批阅记录" />
            <el-timeline v-else>
              <el-timeline-item
                v-for="item in pendingList"
                :key="item.id"
                :timestamp="formatDateTime(item.submitted_at)"
                :type="item.mode === 'exam' ? 'danger' : 'info'"
              >
                <div class="pending-item">
                  <p class="pending-item__title">{{ item.subject_name }} · {{ item.assignment_title || '练习' }}</p>
                  <small>{{ item.mode === 'exam' ? '考试' : '练习' }} · 主观题</small>
                </div>
              </el-timeline-item>
            </el-timeline>
          </el-card>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { nextTick, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import { get } from '@/util/request'

const router = useRouter()
const historyList = ref([])
const pendingList = ref([])
const subjectOptions = ref([])
const subjectFilter = ref('')
const historyLoading = ref(false)
const pendingLoading = ref(false)
const usageLoading = ref(false)
const usageStats = ref([])
const totalUsage = ref(0)
const usageChartRef = ref(null)
let usageChartInstance = null

const chartColors = ['#5B8FF9', '#61DDAA', '#65789B', '#F6BD16', '#7262FD', '#78D3F8']
const getChartColor = (index) => chartColors[index % chartColors.length]

const historyPagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0,
})

const statusMap = {
  ongoing: '进行中',
  completed: '已提交',
  expired: '已超时',
}

const statusLabel = (value) => statusMap[value] || value

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

const initUsageChart = () => {
  if (usageChartRef.value && !usageChartInstance) {
    usageChartInstance = echarts.init(usageChartRef.value)
  }
}

const disposeUsageChart = () => {
  if (usageChartInstance) {
    usageChartInstance.dispose()
    usageChartInstance = null
  }
}

const handleResize = () => {
  usageChartInstance?.resize()
}

const renderUsageChart = () => {
  if (!usageStats.value.length) {
    usageChartInstance?.clear()
    return
  }
  initUsageChart()
  if (!usageChartInstance) return

  usageChartInstance.setOption({
    color: chartColors,
    tooltip: {
      trigger: 'item',
      formatter: '{b}<br/>次数：{c}<br/>占比：{d}%',
    },
    series: [
      {
        name: '学习资源时长',
        type: 'pie',
        radius: ['55%', '80%'],
        center: ['45%', '50%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 8,
          borderColor: '#fff',
          borderWidth: 2,
        },
        label: {
          show: false,
          position: 'center',
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 16,
            fontWeight: 'bold',
            formatter: '{b}\n{d}%',
          },
        },
        labelLine: {
          show: false,
        },
        data: usageStats.value.map((item) => ({
          value: item.value,
          name: item.course,
        })),
      },
    ],
  })
}

watch(usageStats, async () => {
  await nextTick()
  renderUsageChart()
})

const fetchSubjects = async () => {
  try {
    const res = await get('/exam/subjects/')
    subjectOptions.value = res.data?.data || []
  } catch (error) {
    console.error(error)
  }
}

const fetchHistory = async () => {
  historyLoading.value = true
  try {
    const params = {
      page: historyPagination.page,
      page_size: historyPagination.pageSize,
    }
    if (subjectFilter.value) {
      params.subject_id = subjectFilter.value
    }
    const res = await get('/exam/practice/attempts/history/', params)
    const data = res.data?.data || {}
    historyList.value = data.results || []
    historyPagination.total = data.total || 0
    historyPagination.page = data.page || historyPagination.page
    historyPagination.pageSize = data.page_size || historyPagination.pageSize
  } catch (error) {
    console.error(error)
    ElMessage.error('获取历史记录失败，请稍后重试')
  } finally {
    historyLoading.value = false
  }
}

const fetchPending = async () => {
  pendingLoading.value = true
  try {
    const res = await get('/exam/practice/attempts/pending-review/')
    pendingList.value = res.data?.data || []
  } catch (error) {
    console.error(error)
    ElMessage.error('获取待批阅记录失败，请稍后重试')
  } finally {
    pendingLoading.value = false
  }
}

const fetchUsageStats = async () => {
  usageLoading.value = true
  try {
    const res = await get('/learning_resource/usage/stats/')
    const data = res.data?.data || {}
    usageStats.value = data.items || []
    totalUsage.value = data.total || 0
  } catch (error) {
    console.error(error)
    usageStats.value = []
    totalUsage.value = 0
    ElMessage.error('获取学习资源使用统计失败，请稍后重试')
  } finally {
    usageLoading.value = false
  }
}

const refreshHistory = () => {
  historyPagination.page = 1
  fetchHistory()
}

const handleSubjectChange = () => {
  historyPagination.page = 1
  fetchHistory()
}

const handlePageChange = (page) => {
  historyPagination.page = page
  fetchHistory()
}

const handlePageSizeChange = (size) => {
  historyPagination.pageSize = size
  historyPagination.page = 1
  fetchHistory()
}

const viewDetail = (attempt) => {
  router.push({
    path: '/student/practice',
    query: { attempt_id: attempt.id },
  })
}

onMounted(() => {
  fetchSubjects()
  fetchHistory()
  fetchPending()
  fetchUsageStats()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  disposeUsageChart()
})
</script>

<style scoped lang="scss">
.student-analysis {
  padding: 16px;
}

.analysis-grid {
  align-items: stretch;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;

  h3 {
    margin: 0;
  }

  p {
    margin: 2px 0 0;
    color: #909399;
  }
}

.insights-column {
  display: flex;
  flex-direction: column;
  gap: 16px;
  height: 100%;
}

.usage-card__body {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.usage-chart {
  width: 100%;
  height: 260px;
}

.usage-legend {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.usage-legend li {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 10px;
  border-radius: 6px;
  background-color: #f5f7fa;
}

.usage-legend__dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}

.usage-legend__meta {
  display: flex;
  flex-direction: column;
  line-height: 1.4;
}

.usage-legend__name {
  font-weight: 600;
}

.usage-legend__value {
  color: #606266;
  font-size: 13px;
}

.usage-total {
  margin: 0;
  font-weight: 600;
  color: #303133;
}

.history-controls {
  display: flex;
  align-items: center;
  gap: 8px;
}

.table-footer {
  margin-top: 12px;
  display: flex;
  justify-content: flex-end;
}

.pending-item {
  &__title {
    margin: 0;
    font-weight: 600;
  }

  small {
    color: #909399;
  }
}

.mt-16 {
  margin-top: 16px;
}
</style>
