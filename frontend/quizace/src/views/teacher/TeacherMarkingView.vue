<template>
  <div class="teacher-marking">
    <el-row :gutter="16">
      <el-col :span="9">
        <el-card shadow="never" class="list-card">
          <template #header>
            <div class="card-header">
              <div>
                <h3>待批阅学生</h3>
                <p>查看所有有主观题待批阅的学生。</p>
              </div>
              <el-button type="primary" size="small" :loading="pendingLoading" @click="refreshStudents">
                刷新
              </el-button>
            </div>
          </template>
          <div class="filter-bar">
            <el-select
              v-model="assignmentFilter"
              clearable
              size="small"
              placeholder="全部考试/练习"
              @change="handleFilterChange"
            >
              <el-option label="全部" value="" />
              <el-option v-for="item in assignmentOptions" :key="item.id" :label="item.title" :value="item.id" />
            </el-select>
          </div>
          <el-table
            v-loading="pendingLoading"
            :data="studentList"
            border
            size="small"
            highlight-current-row
            @row-click="handleSelectStudent"
            :row-class-name="studentRowClass"
            height="560px"
          >
            <el-table-column prop="student_name" label="学生" min-width="120" />
            <el-table-column label="待批阅" width="100">
              <template #default="{ row }">
                <el-tag size="small" type="warning">{{ row.pending_count }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="最近提交" min-width="150">
              <template #default="{ row }">
                {{ formatDateTime(row.latest_submitted_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="110" fixed="right">
              <template #default="{ row }">
                <el-button type="text" size="small" @click.stop="handleSelectStudent(row)">查看</el-button>
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-if="!pendingLoading && !studentList.length" description="暂无学生待批阅" />
        </el-card>
      </el-col>
      <el-col :span="15">
        <el-card shadow="never" class="detail-card">
          <template #header>
            <div class="card-header">
              <div>
                <h3>阅卷面板</h3>
                <p v-if="selectedStudent">
                  {{ selectedStudent.student_name }} · 待批阅 {{ selectedStudent.pending_count }} 份
                </p>
              </div>
              <el-tag v-if="currentAttempt" type="danger" size="small">主观题</el-tag>
            </div>
          </template>

          <el-skeleton v-if="detailLoading" :rows="6" animated />
          <el-empty v-else-if="!selectedStudent" description="请选择左侧学生查看待批阅试卷" />
          <div v-else>
            <div class="attempt-section">
              <div class="attempt-header">
                <h4>待批阅试卷</h4>
                <span>共 {{ selectedStudent.pending_count }} 份</span>
              </div>
              <el-table
                :data="selectedStudent.attempts"
                size="small"
                border
                highlight-current-row
                @row-click="handleSelectAttempt"
                :row-class-name="attemptRowClass"
                class="attempt-table"
              >
                <el-table-column label="类型" width="90">
                  <template #default="{ row }">
                    <el-tag :type="modeTagType(row.mode)" size="small">{{ modeLabel(row.mode) }}</el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="assignment_title" label="考试/练习" min-width="140">
                  <template #default="{ row }">
                    {{ row.assignment_title || '练习' }}
                  </template>
                </el-table-column>
                <el-table-column prop="subject_name" label="科目" width="120" />
                <el-table-column label="提交时间" min-width="150">
                  <template #default="{ row }">
                    {{ formatDateTime(row.submitted_at) }}
                  </template>
                </el-table-column>
                <el-table-column label="状态" width="100">
                  <template #default="{ row }">
                    {{ statusLabel(row.status) }}
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="110" fixed="right">
                  <template #default="{ row }">
                    <el-button type="text" size="small" @click.stop="handleSelectAttempt(row)">
                      批阅
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
              <el-empty v-if="!selectedStudent.attempts?.length" description="该学生暂无待批阅试卷" />
            </div>

            <el-divider />

            <el-empty v-if="!currentAttempt" description="请选择上方试卷开始批阅" />
            <div v-else class="review-panel">
              <div class="attempt-meta">
                <p><strong>学生：</strong>{{ currentAttempt.student_name }}</p>
                <p><strong>科目：</strong>{{ currentAttempt.subject_name }}</p>
                <p><strong>来源：</strong>{{ currentAttempt.assignment_title || '练习' }}</p>
                <p><strong>提交时间：</strong>{{ formatDateTime(currentAttempt.submitted_at) }}</p>
                <p><strong>总分：</strong>{{ maxTotal }} 分</p>
              </div>

              <div class="question-list">
                <div v-for="item in reviewItems" :key="item.id" class="question-card">
                  <div class="question-card__header">
                    <span>第 {{ item.order }} 题</span>
                    <el-tag size="mini">{{ item.max_score }} 分</el-tag>
                  </div>
                  <p class="question-card__content">{{ item.content }}</p>
                  <div class="answer-block">
                    <p><strong>学生作答：</strong></p>
                    <p class="answer-text">{{ item.user_answer || '未作答' }}</p>
                  </div>
                  <div class="answer-block" v-if="item.reference">
                    <p><strong>参考答案：</strong></p>
                    <p class="answer-text">{{ item.reference }}</p>
                  </div>
                  <div class="score-input">
                    <span>得分：</span>
                    <el-input-number
                      v-model="item.awarded_score"
                      :min="0"
                      :max="item.max_score"
                      size="small"
                    />
                    <span class="max-score">/ {{ item.max_score }}</span>
                  </div>
                </div>
              </div>

              <div class="review-summary">
                <p>
                  当前得分：
                  <strong>{{ awardedTotal }}</strong>
                  / {{ maxTotal }}
                </p>
                <el-input
                  v-model="reviewComment"
                  type="textarea"
                  :autosize="{ minRows: 3 }"
                  placeholder="填写评语，反馈给学生"
                />
                <el-button
                  type="primary"
                  class="submit-btn"
                  :loading="submitting"
                  @click="submitReview"
                >
                  提交批阅
                </el-button>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { get, post } from '@/util/request'

const pendingLoading = ref(false)
const studentList = ref([])
const assignmentFilter = ref('')
const detailLoading = ref(false)
const selectedStudent = ref(null)
const selectedAttemptId = ref(null)
const currentAttempt = ref(null)
const reviewItems = ref([])
const reviewComment = ref('')
const submitting = ref(false)

const assignmentOptions = computed(() => {
  const map = new Map()
  let includePractice = false
  studentList.value.forEach((student) => {
    (student.attempts || []).forEach((attempt) => {
      if (attempt.assignment_id) {
        const key = String(attempt.assignment_id)
        if (!map.has(key)) {
          map.set(key, attempt.assignment_title || `考试 ${attempt.assignment_id}`)
        }
      } else {
        includePractice = true
      }
    })
  })
  const list = Array.from(map, ([id, title]) => ({ id, title }))
  if (includePractice) {
    list.unshift({ id: 'practice', title: '练习' })
  }
  return list
})

const maxTotal = computed(() => {
  const itemTotal = reviewItems.value.reduce((sum, item) => sum + (item.max_score || 0), 0)
  if (itemTotal) return itemTotal
  return currentAttempt.value?.total_score || 0
})

const awardedTotal = computed(() =>
  reviewItems.value.reduce((sum, item) => sum + (Number(item.awarded_score) || 0), 0),
)

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

const modeLabel = (mode) => (mode === 'exam' ? '考试' : '练习')
const modeTagType = (mode) => (mode === 'exam' ? 'danger' : 'info')
const statusLabel = (status) => {
  const map = {
    completed: '已提交',
    expired: '已超时',
    ongoing: '进行中',
  }
  return map[status] || status
}

const studentRowClass = ({ row }) => (
  selectedStudent.value && row.student_id === selectedStudent.value.student_id ? 'is-active-row' : ''
)
const attemptRowClass = ({ row }) => (row.id === selectedAttemptId.value ? 'is-active-row' : '')

const refreshStudents = () => {
  fetchStudents()
}

const handleFilterChange = () => {
  fetchStudents()
}

const handleSelectStudent = (row) => {
  if (!row) return
  selectedStudent.value = row
  if (!row.attempts?.length) {
    selectedAttemptId.value = null
    currentAttempt.value = null
    reviewItems.value = []
    reviewComment.value = ''
    return
  }
  loadAttemptDetail(row.attempts[0].id)
}

const handleSelectAttempt = (row) => {
  if (!row) return
  loadAttemptDetail(row.id)
}

const fetchStudents = async () => {
  pendingLoading.value = true
  const previousStudentId = selectedStudent.value?.student_id || null
  const previousAttemptId = selectedAttemptId.value
  try {
    const params = {}
    if (assignmentFilter.value) {
      params.assignment_id = assignmentFilter.value
    }
    const res = await get('/exam/practice/attempts/pending-review/teacher/students/', params)
    studentList.value = res.data?.data || []
    await restoreSelection(previousStudentId, previousAttemptId)
  } catch (error) {
    console.error(error)
    ElMessage.error('获取待批阅学生失败')
  } finally {
    pendingLoading.value = false
  }
}

const restoreSelection = async (preferredStudentId, preferredAttemptId) => {
  if (!studentList.value.length) {
    selectedStudent.value = null
    selectedAttemptId.value = null
    currentAttempt.value = null
    reviewItems.value = []
    reviewComment.value = ''
    return
  }
  const targetStudent =
    studentList.value.find((student) => student.student_id === preferredStudentId) ||
    studentList.value[0]
  selectedStudent.value = targetStudent
  const attempts = targetStudent.attempts || []
  if (!attempts.length) {
    selectedAttemptId.value = null
    currentAttempt.value = null
    reviewItems.value = []
    reviewComment.value = ''
    return
  }
  const targetAttempt =
    attempts.find((attempt) => attempt.id === preferredAttemptId) || attempts[0]
  await loadAttemptDetail(targetAttempt.id)
}

const loadAttemptDetail = async (attemptId) => {
  if (!attemptId) return
  detailLoading.value = true
  selectedAttemptId.value = attemptId
  try {
    const res = await get(`/exam/practice/attempts/${attemptId}/teacher/`)
    if (res.data.code === 200) {
      const data = res.data.data
      currentAttempt.value = {
        ...data.attempt,
        student_name: data.attempt.user_name,
        assignment_title: data.attempt.assignment_title,
      }
      reviewComment.value = data.attempt.review_comment || ''
      reviewItems.value = (data.items || []).map((item) => ({
        id: item.id,
        order: item.order,
        content: item.question?.content || '',
        user_answer: item.user_answer,
        reference: item.question?.answer || '',
        max_score: item.question?.score || 0,
        awarded_score: item.awarded_score ?? 0,
      }))
    } else {
      ElMessage.error(res.data.info || '无法读取试卷详情')
    }
  } catch (error) {
    console.error(error)
    ElMessage.error('获取试卷详情失败')
  } finally {
    detailLoading.value = false
  }
}

const submitReview = async () => {
  if (!currentAttempt.value) {
    ElMessage.warning('请先选择需要批阅的试卷')
    return
  }
  if (!reviewItems.value.length) {
    ElMessage.warning('题目数据缺失，无法批阅')
    return
  }
  try {
    await ElMessageBox.confirm('确认提交本次批阅结果吗？', '提交确认', {
      confirmButtonText: '提交',
      cancelButtonText: '取消',
      type: 'warning',
    })
  } catch (error) {
    return
  }

  submitting.value = true
  try {
    const payload = {
      items: reviewItems.value.map((item) => ({
        id: item.id,
        awarded_score: Number(item.awarded_score) || 0,
      })),
      review_comment: reviewComment.value,
    }
    const res = await post(`/exam/practice/attempts/${currentAttempt.value.id}/review/`, payload)
    if (res.data.code === 200) {
      ElMessage.success('批阅完成')
      await fetchStudents()
    } else {
      ElMessage.error(res.data.info || '提交失败')
    }
  } catch (error) {
    console.error(error)
    ElMessage.error('提交失败，请稍后再试')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  fetchStudents()
})
</script>

<style scoped lang="scss">
.teacher-marking {
  padding: 16px;
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

.list-card,
.detail-card {
  min-height: 640px;
}

.filter-bar {
  margin-bottom: 12px;
}

.attempt-section {
  margin-bottom: 16px;
}

.attempt-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;

  h4 {
    margin: 0;
  }

  span {
    color: #909399;
  }
}

.attempt-table {
  cursor: pointer;
}

.is-active-row {
  background-color: #f0f9ff !important;
}

.review-panel {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.attempt-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  font-size: 14px;

  p {
    margin: 0;
  }
}

.question-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-height: 360px;
  overflow-y: auto;
  padding-right: 8px;
}

.question-card {
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 12px;

  &__header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 6px;
    font-weight: 600;
  }

  &__content {
    margin-bottom: 8px;
    line-height: 1.6;
  }
}

.answer-block {
  background: #f8f9fb;
  border-radius: 6px;
  padding: 8px;
  margin-bottom: 8px;

  p {
    margin: 0;
  }
}

.answer-text {
  white-space: pre-wrap;
  color: #606266;
}

.score-input {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.max-score {
  color: #909399;
}

.review-summary {
  border-top: 1px solid #ebeef5;
  padding-top: 12px;

  p {
    margin-top: 0;
  }
}

.submit-btn {
  margin-top: 12px;
}
</style>
