<template>
  <div class="student-exam">
    <el-card shadow="never" class="section-card">
      <template #header>
        <div class="card-header">
          <div>
            <h3>进行中的练习 / 考试</h3>
            <p>支持多个练习与正式考试同时进行，可随时继续。</p>
          </div>
          <div>
            <el-button type="primary" size="small" :loading="ongoingLoading" @click="fetchOngoing">
              刷新
            </el-button>
          </div>
        </div>
      </template>
      <el-empty v-if="!ongoingList.length" description="暂无进行中的试卷" />
      <el-row v-else :gutter="16">
        <el-col v-for="attempt in ongoingList" :key="attempt.id" :span="8">
          <el-card class="attempt-card" shadow="hover">
            <div class="attempt-card__title">
              <el-tag :type="attempt.mode === 'exam' ? 'danger' : 'info'" size="small">
                {{ attempt.mode === 'exam' ? '考试' : '练习' }}
              </el-tag>
              <span>{{ attempt.subject_name }}</span>
            </div>
            <p class="attempt-card__meta">题型：{{ questionTypeLabel(attempt.question_type) }}</p>
            <p class="attempt-card__meta">剩余时间：{{ formatCountdown(attempt.remaining_seconds) }}</p>
            <p v-if="attempt.assignment_title" class="attempt-card__meta">考试：{{ attempt.assignment_title }}</p>
            <el-button type="primary" size="small" @click="resumeAttempt(attempt)">
              继续作答
            </el-button>
          </el-card>
        </el-col>
      </el-row>
    </el-card>

    <el-card shadow="never" class="section-card">
      <template #header>
        <div class="card-header">
          <div>
            <h3>考试中心</h3>
            <p>查看老师发布的正式考试，按时间窗口进入作答。</p>
          </div>
          <el-button size="small" :loading="assignmentLoading" @click="fetchAssignments">刷新</el-button>
        </div>
      </template>
      <el-table :data="assignmentList" border v-loading="assignmentLoading" size="small" class="assignment-table">
        <el-table-column prop="title" label="考试" min-width="160">
          <template #default="{ row }">
            <div class="assignment-title">
              <strong>{{ row.title }}</strong>
              <p>{{ row.subject_name }}</p>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="question_type" label="题型" width="100">
          <template #default="{ row }">
            {{ row.question_type === 'objective' ? '客观题' : '主观题' }}
          </template>
        </el-table-column>
        <el-table-column label="考试时间" min-width="200">
          <template #default="{ row }">
            <div>{{ formatDateTime(row.start_time) }} ~</div>
            <div>{{ formatDateTime(row.end_time) }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="duration_seconds" label="时长" width="90">
          <template #default="{ row }">{{ Math.floor((row.duration_seconds || 0) / 60) }} 分钟</template>
        </el-table-column>
        <el-table-column label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="phaseTagType(row.phase)" size="small">{{ phaseLabel(row) }}</el-tag>
            <p v-if="row.attempt_status" class="attempt-status">
              {{ attemptStatusLabel(row.attempt_status) }}
            </p>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              :disabled="isActionDisabled(row)"
              :loading="startingId === row.id"
              @click="handleExamAction(row)"
            >
              {{ actionLabel(row) }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!assignmentLoading && !assignmentList.length" description="暂无可参加的考试" />
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { get, post } from '@/util/request'

const router = useRouter()
const ongoingLoading = ref(false)
const assignmentLoading = ref(false)
const ongoingList = ref([])
const assignmentList = ref([])
const startingId = ref(null)

const questionTypeLabel = (value) => (value === 'objective' ? '客观题' : '主观题')

const formatCountdown = (value) => {
  const safe = Math.max(0, Number(value) || 0)
  const minutes = Math.floor(safe / 60)
  const seconds = safe % 60
  return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`
}

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

const phaseLabel = (row) => {
  if (row.phase === 'upcoming') return '未开始'
  if (row.phase === 'ongoing') return '进行中'
  return '已结束'
}

const phaseTagType = (phase) => {
  if (phase === 'ongoing') return 'success'
  if (phase === 'upcoming') return 'info'
  return 'warning'
}

const attemptStatusLabel = (status) => {
  const map = {
    ongoing: '进行中',
    completed: '已完成',
    expired: '已超时',
  }
  return map[status] || status
}

const fetchOngoing = async () => {
  ongoingLoading.value = true
  try {
    const res = await get('/exam/practice/attempts/ongoing/')
    ongoingList.value = res.data?.data || []
  } catch (error) {
    console.error(error)
    ElMessage.error('获取进行中试卷失败')
  } finally {
    ongoingLoading.value = false
  }
}

const fetchAssignments = async () => {
  assignmentLoading.value = true
  try {
    const res = await get('/exam/assignments/available/')
    assignmentList.value = res.data?.data || []
  } catch (error) {
    console.error(error)
    ElMessage.error('获取考试列表失败')
  } finally {
    assignmentLoading.value = false
  }
}

const resumeAttempt = (attempt) => {
  router.push({
    path: '/student/practice',
    query: {
      attempt_id: attempt.id,
      subject_id: attempt.subject_id,
      subject_name: attempt.subject_name,
      question_type: attempt.question_type,
    },
  })
}

const isActionDisabled = (assignment) => {
  if (assignment.phase !== 'ongoing') return true
  if (assignment.attempt_status === 'completed') return true
  return false
}

const actionLabel = (assignment) => {
  if (assignment.phase === 'upcoming') return '未开始'
  if (assignment.phase === 'ended') return '已结束'
  if (assignment.attempt_status === 'completed') return '已完成'
  if (assignment.attempt_status === 'ongoing') return '继续考试'
  return '开始考试'
}

const handleExamAction = async (assignment) => {
  if (assignment.phase !== 'ongoing') {
    ElMessage.info('该考试暂不可进入')
    return
  }
  if (assignment.attempt_status === 'completed') {
    ElMessage.success('你已完成该考试')
    return
  }
  startingId.value = assignment.id
  try {
    const res = await post(`/exam/assignments/${assignment.id}/start/`)
    if (res.data.code === 200) {
      const attemptId = res.data.data?.attempt_id
      if (attemptId) {
        router.push({ path: '/student/practice', query: { attempt_id: attemptId } })
        ElMessage.success(res.data.info || '考试已创建')
        await Promise.all([fetchOngoing(), fetchAssignments()])
      } else {
        ElMessage.error('未获取到试卷编号')
      }
    } else {
      ElMessage.error(res.data.info || '无法开始考试')
    }
  } catch (error) {
    console.error(error)
    ElMessage.error('无法开始考试')
  } finally {
    startingId.value = null
  }
}

onMounted(() => {
  fetchOngoing()
  fetchAssignments()
})
</script>

<style scoped lang="scss">
.student-exam {
  padding: 16px;
}

.section-card {
  margin-bottom: 20px;
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

.attempt-card {
  margin-bottom: 12px;

  &__title {
    display: flex;
    align-items: center;
    gap: 8px;
    font-weight: 600;
    margin-bottom: 6px;
  }

  &__meta {
    margin: 0 0 4px;
    color: #606266;
    font-size: 13px;
  }
}

.assignment-title {
  strong {
    display: block;
  }

  p {
    margin: 2px 0 0;
    color: #909399;
  }
}

.attempt-status {
  margin: 4px 0 0;
  color: #909399;
}

.assignment-table .el-table__empty-block {
  min-height: 120px;
}
</style>
