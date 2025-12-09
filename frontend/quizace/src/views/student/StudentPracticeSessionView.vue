<template>
  <div class="practice-page">
    <div class="page-header">
      <el-button type="text" @click="goBack">
        <i class="el-icon-arrow-left"></i> 返回科目选择
      </el-button>
      <div class="header-info">
        <h2>{{ subjectName || '练习' }} · {{ currentTypeLabel }}</h2>
        <p>系统随机抽取 {{ questions.length }} 道题，请在规定时间内完成。</p>
        <div class="header-tags" v-if="attemptSummary">
          <el-tag v-if="isExam" type="danger" size="small">正式考试</el-tag>
          <el-tag v-else type="info" size="small">练习模式</el-tag>
          <span v-if="attemptSummary.assignment_title" class="assignment-title">{{ attemptSummary.assignment_title }}</span>
        </div>
      </div>
      <div class="header-actions">
        <div class="timer" :class="{ danger: remainingSeconds <= 60 }">
          <i class="el-icon-time"></i>
          <span>{{ formattedCountdown }}</span>
        </div>
        <el-tag :type="statusTagType">{{ statusLabel }}</el-tag>
        <el-button type="primary" :loading="loading" @click="restartAttempt">重新抽题</el-button>
      </div>
    </div>

    <el-alert
      v-if="attemptStatus === 'expired' && !showResult"
      class="mb-16"
      title="练习已超时，将自动交卷"
      type="warning"
      show-icon
    />

    <el-row :gutter="16">
      <el-col :span="17">
        <el-card class="question-card" shadow="hover">
          <el-skeleton v-if="loading" :rows="6" animated />
          <el-empty v-else-if="questions.length === 0" description="暂无题目，请返回重新选择" />
          <div v-else class="question-list">
            <div v-for="question in questions" :key="question.id" class="question-item">
              <div class="question-header">
                <span class="index">第 {{ question.order }} 题</span>
                <el-tag size="mini" type="info">{{ question.question_type === 'objective' ? '客观题' : '主观题' }}</el-tag>
                <el-tag size="mini">{{ question.subject_name }}</el-tag>
                <span class="score">{{ question.score }} 分</span>
              </div>
              <p class="question-content">{{ question.content }}</p>
              <div v-if="question.media_url" class="question-media">
                <img :src="formatMediaUrl(question.media_url)" alt="题目图片" />
              </div>

              <div v-if="question.question_type === 'objective'" class="option-wrapper">
                <el-radio-group
                  v-model="question.user_answer"
                  :disabled="!isInteractive"
                  class="option-group"
                >
                  <el-radio v-for="(text, key) in question.options" :key="key" :label="key">
                    {{ key }}. {{ text }}
                  </el-radio>
                </el-radio-group>
              </div>
              <div v-else class="subjective-answer">
                <el-input
                  v-model="question.user_answer"
                  type="textarea"
                  :autosize="{ minRows: 4 }"
                  :disabled="!isInteractive"
                  placeholder="请输入你的作答..."
                />
              </div>

              <div v-if="showResult" class="analysis-block">
                <div v-if="question.question_type === 'objective'" class="result-line">
                  <el-tag :type="question.is_correct ? 'success' : 'danger'" size="small">
                    {{ question.is_correct ? '回答正确' : '回答错误' }}
                  </el-tag>
                  <span class="user-answer">你的答案：{{ question.user_answer || '未作答' }}</span>
                </div>
                <div v-else-if="attemptSummary && !attemptSummary.is_review_required" class="result-line">
                  <el-tag type="success" size="small">
                    得分：{{ question.awarded_score }} / {{ question.score || '--' }}
                  </el-tag>
                </div>
                <p v-if="question.answer"><strong>参考答案：</strong>{{ question.answer }}</p>
                <p v-if="question.analysis"><strong>解析：</strong>{{ question.analysis }}</p>
                <div class="wrong-book-action" v-if="canCollectWrongBook(question)">
                  <el-button
                    type="warning"
                    size="mini"
                    :loading="isCollecting(question)"
                    @click="collectWrongQuestion(question)"
                  >
                    {{ question.in_wrong_book ? '再次收录' : '收录到错题本' }}
                  </el-button>
                  <el-tag v-if="question.in_wrong_book" type="success" size="small">已收录</el-tag>
                </div>
              </div>
            </div>
          </div>
        </el-card>

        <div class="submit-bar">
          <el-button
            type="primary"
            :disabled="submitDisabled"
            :loading="submitting"
            @click="handleSubmit()"
          >
            {{ showResult ? '已提交' : '提交答卷' }}
          </el-button>
        </div>
      </el-col>

      <el-col :span="7">
        <el-card class="aside-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>练习概览</span>
            </div>
          </template>
          <ul class="meta-list">
            <li><span>状态</span><strong>{{ statusLabel }}</strong></li>
            <li><span>类型</span><strong>{{ isExam ? '考试' : '练习' }}</strong></li>
            <li><span>剩余时间</span><strong>{{ formattedCountdown }}</strong></li>
            <li><span>题目数量</span><strong>{{ questions.length }} 题</strong></li>
            <li v-if="showResult && attemptSummary?.question_type === 'objective'">
              <span>正确数</span>
              <strong>{{ attemptSummary.correct_count }}/{{ attemptSummary.total_questions }}</strong>
            </li>
            <li v-if="showResult && attemptSummary?.question_type === 'objective'">
              <span>得分</span>
              <strong>{{ attemptSummary.obtained_score }}/{{ expectedTotalScore }}</strong>
            </li>
            <li v-if="showResult && attemptSummary?.submitted_at">
              <span>提交时间</span>
              <strong>{{ formatDateTime(attemptSummary.submitted_at) }}</strong>
            </li>
            <li v-if="showResult && attemptSummary?.review_comment">
              <span>评语</span>
              <strong>{{ attemptSummary.review_comment }}</strong>
            </li>
          </ul>
          <el-alert
            v-if="showResult && attemptSummary?.question_type === 'subjective'"
            class="mt-12"
            :title="attemptSummary?.is_review_required ? '已提交，等待老师批阅' : '批阅完成，可查看参考答案'"
            :type="attemptSummary?.is_review_required ? 'info' : 'success'"
            show-icon
          />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute, useRouter, onBeforeRouteLeave } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { get, post, getMediaBaseUrl } from '@/util/request'

const route = useRoute()
const router = useRouter()

const subjectId = ref(route.query.subject_id || '')
const subjectName = ref(route.query.subject_name || '')
const questionType = ref(route.query.question_type || 'objective')
const attemptId = ref(route.query.attempt_id ? Number(route.query.attempt_id) : null)
const attemptStatus = ref('pending')
const attemptSummary = ref(null)
const questions = ref([])
const loading = ref(false)
const submitting = ref(false)
const showResult = ref(false)
const remainingSeconds = ref(0)
const expiresAt = ref(null)
const timerRef = ref(null)
const collectingMap = ref({})

const questionTypes = {
  objective: { label: '客观题练习', size: 10, score: 10 },
  subjective: { label: '主观题练习', size: 5, score: 20 }
}

const currentTypeLabel = computed(() => questionTypes[questionType.value]?.label || '练习')
const statusMap = {
  pending: '待开始',
  ongoing: '进行中',
  completed: '已提交',
  expired: '已超时'
}

const statusLabel = computed(() => statusMap[attemptStatus.value] || '待开始')
const statusTagType = computed(() => {
  switch (attemptStatus.value) {
    case 'completed':
      return 'success'
    case 'expired':
      return 'warning'
    case 'ongoing':
      return 'info'
    default:
      return 'info'
  }
})

const formatCountdown = (value) => {
  const safe = Math.max(0, Number(value) || 0)
  const h = Math.floor(safe / 3600)
  const m = Math.floor((safe % 3600) / 60)
  const s = safe % 60
  return [h, m, s].map((n) => String(n).padStart(2, '0')).join(':')
}

const formattedCountdown = computed(() => formatCountdown(remainingSeconds.value))
const isInteractive = computed(() => attemptStatus.value === 'ongoing' && !showResult.value && remainingSeconds.value > 0)
const submitDisabled = computed(() => !attemptId.value || showResult.value || attemptStatus.value !== 'ongoing' || submitting.value)
const isExam = computed(() => attemptSummary.value?.mode === 'exam')
const expectedTotalScore = computed(() => {
  const summary = attemptSummary.value
  if (!summary) return 0
  if (summary.total_score) return summary.total_score
  const meta = questionTypes[summary.question_type]
  if (!meta) return 0
  return (summary.total_questions || meta.size || 0) * (meta.score || 0)
})

const clearTimer = () => {
  if (timerRef.value) {
    clearInterval(timerRef.value)
    timerRef.value = null
  }
}

const startTimer = (expires, fallbackSeconds) => {
  clearTimer()
  const deadline = expires ? new Date(expires).getTime() : Date.now() + (fallbackSeconds || 0) * 1000
  const tick = () => {
    const diff = Math.floor((deadline - Date.now()) / 1000)
    remainingSeconds.value = diff > 0 ? diff : 0
    if (diff <= 0) {
      clearTimer()
      if (attemptStatus.value === 'ongoing' && !showResult.value) {
        attemptStatus.value = 'expired'
        handleSubmit(true)
      }
    }
  }
  tick()
  timerRef.value = setInterval(tick, 1000)
}

const mediaBaseUrl = getMediaBaseUrl()

const formatMediaUrl = (value) => {
  if (!value) return ''
  if (/^https?:/i.test(value)) {
    return value
  }
  if (value.startsWith('http')) {
    return value
  }
  if (value.startsWith('/')) {
    return `${mediaBaseUrl}${value}`
  }
  return `${mediaBaseUrl}/${value}`
}

const OPTION_KEYS = ['A', 'B', 'C', 'D']

const normalizeOptions = (options = {}) => {
  const normalized = {}
  OPTION_KEYS.forEach((key) => {
    normalized[key] = options?.[key] ?? ''
  })
  return normalized
}

const normalizeStartQuestions = (list = []) => {
  return list.map((item, index) => ({
    id: item.id,
    order: item.order || index + 1,
    question_type: item.question_type,
    content: item.content,
    subject_name: item.subject_name,
    options: item.question_type === 'objective' ? normalizeOptions(item.options || {}) : {},
    score: item.score,
    user_answer: item.user_answer || '',
    is_correct: item.is_correct ?? null,
    answer: item.answer,
    analysis: item.analysis,
    awarded_score: item.awarded_score ?? 0,
    item_id: null,
    in_wrong_book: false,
    media_url: item.media_url || '',
  }))
}

const normalizeAttemptItems = (items = []) => {
  return items.map((item) => ({
    id: item.question.id,
    order: item.order,
    question_type: item.question.question_type,
    content: item.question.content,
    subject_name: item.question.subject_name,
    options: item.question.question_type === 'objective' ? normalizeOptions(item.question.options || {}) : {},
    score: item.question.score,
    answer: item.question.answer,
    analysis: item.question.analysis,
    user_answer: item.user_answer || '',
    is_correct: item.is_correct,
    awarded_score: item.awarded_score ?? 0,
    item_id: item.id,
    in_wrong_book: Boolean(item.in_wrong_book),
    media_url: item.question.media_url || '',
  }))
}

const syncRouteQuery = () => {
  router.replace({
    path: route.path,
    query: {
      subject_id: subjectId.value,
      subject_name: subjectName.value,
      question_type: questionType.value,
      ...(attemptId.value ? { attempt_id: attemptId.value } : {}),
    },
  })
}

const saveProgressIfNeeded = async () => {
  if (!attemptId.value || attemptStatus.value !== 'ongoing' || showResult.value) return
  try {
    await post(`/exam/practice/attempts/${attemptId.value}/save/`, {
      answers: questions.value.map((q) => ({
        question_id: q.id,
        user_answer: q.user_answer || '',
      })),
    })
  } catch (error) {
    console.warn('保存作答失败', error)
  }
}

const startAttempt = async () => {
  if (!subjectId.value) {
    ElMessage.warning('缺少科目信息，请返回重新选择')
    return
  }
  collectingMap.value = {}
  loading.value = true
  showResult.value = false
  attemptStatus.value = 'pending'
  questions.value = []
  try {
    const res = await post('/exam/practice/attempts/start/', {
      subject_id: subjectId.value,
      question_type: questionType.value,
      size: questionTypes[questionType.value]?.size,
    })
    if (res.data.code === 200) {
      const data = res.data.data
      attemptId.value = data.attempt_id
      attemptStatus.value = 'ongoing'
      const perQuestionScore = questionTypes[data.question_type || questionType.value]?.score || 0
      const questionCount = data.questions?.length || questionTypes[questionType.value]?.size || 0
      attemptSummary.value = {
        mode: 'practice',
        question_type: data.question_type,
        total_questions: questionCount,
        correct_count: 0,
        total_score: questionCount * perQuestionScore,
        obtained_score: 0,
        subject_name: data.subject?.name || subjectName.value,
        assignment_title: null,
      }
      subjectName.value = data.subject?.name || subjectName.value
      expiresAt.value = data.expires_at
      remainingSeconds.value = data.remaining_seconds ?? data.duration_seconds
      questions.value = normalizeStartQuestions(data.questions)
      startTimer(expiresAt.value, remainingSeconds.value)
      syncRouteQuery()
      ElMessage.success('已生成新的练习试卷')
    } else {
      ElMessage.error(res.data.info || '创建练习失败')
    }
  } catch (error) {
    console.error(error)
    ElMessage.error('创建练习失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

const loadAttemptDetail = async () => {
  if (!attemptId.value) return
  collectingMap.value = {}
  loading.value = true
  try {
    const res = await get(`/exam/practice/attempts/${attemptId.value}/`)
    if (res.data.code === 200) {
      const data = res.data.data
      const attempt = data.attempt
      attemptSummary.value = attempt
      attemptStatus.value = attempt.status
      questionType.value = attempt.question_type
      subjectId.value = attempt.subject
      subjectName.value = attempt.subject_name || subjectName.value
      expiresAt.value = data.expires_at
      remainingSeconds.value = data.remaining_seconds ?? 0
      questions.value = normalizeAttemptItems(data.items)
      showResult.value = attempt.status !== 'ongoing'
      if (!showResult.value) {
        startTimer(expiresAt.value, remainingSeconds.value)
      } else {
        clearTimer()
      }
      syncRouteQuery()
    } else {
      ElMessage.error(res.data.info || '无法读取练习信息')
    }
  } catch (error) {
    console.error(error)
    ElMessage.error('获取练习失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

const restartAttempt = async () => {
  if (attemptStatus.value === 'ongoing' && !showResult.value) {
    try {
      await ElMessageBox.confirm('当前练习尚未提交，重新抽题将清空作答，是否继续？', '提示', {
        confirmButtonText: '继续',
        cancelButtonText: '取消',
        type: 'warning',
      })
    } catch (error) {
      return
    }
  }
  startAttempt()
}

const updateCollectingFlag = (itemId, value) => {
  if (!itemId) return
  collectingMap.value = {
    ...collectingMap.value,
    [itemId]: value,
  }
}

const isCollecting = (question) => {
  if (!question?.item_id) return false
  return Boolean(collectingMap.value[question.item_id])
}

const canCollectWrongBook = (question) => {
  if (!showResult.value || !question?.item_id) return false
  if (question.question_type === 'objective') {
    return question.is_correct === false
  }
  if (attemptSummary.value?.is_review_required) return false
  const maxScore = Number(question.score) || 0
  const currentScore = Number(question.awarded_score) || 0
  return maxScore > 0 && currentScore < maxScore
}

const collectWrongQuestion = async (question) => {
  if (!question?.item_id) {
    ElMessage.warning('缺少题目记录，无法加入错题本')
    return
  }
  const alreadyCollected = Boolean(question.in_wrong_book)
  updateCollectingFlag(question.item_id, true)
  try {
    const res = await post('/exam/wrong-book/items/', { attempt_item_id: question.item_id })
    if (res.data.code === 200) {
      question.in_wrong_book = true
      ElMessage.success(alreadyCollected ? '已再次收录' : '已加入错题本')
    } else {
      ElMessage.error(res.data.info || '加入错题本失败')
    }
  } catch (error) {
    console.error(error)
    ElMessage.error('加入错题本失败，请稍后重试')
  } finally {
    updateCollectingFlag(question.item_id, false)
  }
}

const handleSubmit = async (auto = false) => {
  if (!attemptId.value) return
  if (!auto && submitDisabled.value) return
  if (!auto) {
    try {
      await ElMessageBox.confirm('确认提交本次练习吗？', '提交确认', {
        confirmButtonText: '提交',
        cancelButtonText: '取消',
        type: 'warning',
      })
    } catch (error) {
      return
    }
  }

  submitting.value = true
  try {
    const payload = {
      answers: questions.value.map((q) => ({
        question_id: q.id,
        user_answer: q.user_answer || '',
      })),
    }
    const res = await post(`/exam/practice/attempts/${attemptId.value}/submit/`, payload)
    if (res.data.code === 200) {
      const { attempt, items } = res.data.data
      attemptSummary.value = attempt
      attemptStatus.value = attempt.status
      showResult.value = true
      clearTimer()
      questions.value = normalizeAttemptItems(items)
      if (auto) {
        ElMessage.warning(res.data.info || '已自动交卷')
      } else {
        ElMessage.success('提交成功')
      }
    } else {
      ElMessage.error(res.data.info || '提交失败')
    }
  } catch (error) {
    console.error(error)
    ElMessage.error('提交失败，请稍后重试')
  } finally {
    submitting.value = false
  }
}

const goBack = async () => {
  if (attemptStatus.value === 'ongoing' && !showResult.value) {
    try {
      await ElMessageBox.confirm('返回将离开当前练习，确定吗？', '提示', {
        confirmButtonText: '离开',
        cancelButtonText: '取消',
        type: 'warning',
      })
    } catch (error) {
      return
    }
  }
  router.push('/student/questions')
}

const formatDateTime = (value) => {
  if (!value) return '-'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return '-'
  const y = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  return `${y}-${month}-${day} ${hours}:${minutes}`
}

onMounted(() => {
  if (attemptId.value) {
    loadAttemptDetail()
    return
  }
  if (!subjectId.value) {
    ElMessage.warning('缺少科目信息，请返回重新选择')
    router.push('/student/questions')
    return
  }
  startAttempt()
})

onBeforeUnmount(() => {
  clearTimer()
})

onBeforeRouteLeave(async (to, from, next) => {
  await saveProgressIfNeeded()
  next()
})
</script>

<style lang="scss" scoped>
.practice-page {
  padding: 20px;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;

  .header-info {
    text-align: left;

    h2 {
      margin: 0;
      font-size: 22px;
    }

    p {
      margin: 2px 0 0;
      color: #909399;
    }

    .header-tags {
      margin-top: 6px;
      display: flex;
      align-items: center;
      gap: 8px;

      .assignment-title {
        font-size: 13px;
        color: #606266;
      }
    }
  }

  .header-actions {
    display: flex;
    align-items: center;
    gap: 12px;
  }
}

.timer {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  border-radius: 20px;
  background: #f5f7fa;
  font-weight: 600;

  &.danger {
    color: #f56c6c;
    background: #fef0f0;
  }
}

.mb-16 {
  margin-bottom: 16px;
}

.question-card {
  border-radius: 12px;
}

.question-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.question-item {
  border: 1px solid #f0f0f0;
  border-radius: 10px;
  padding: 16px;
}

.question-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;

  .index {
    font-weight: 600;
  }

  .score {
    margin-left: auto;
    font-weight: 600;
    color: #606266;
  }
}

.question-content {
  font-size: 15px;
  line-height: 1.6;
  margin-bottom: 10px;
}

.question-media {
  margin-bottom: 16px;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid #e6eaf2;
  background: #f9fafc;

  img {
    display: block;
    width: 100%;
    max-height: 360px;
    object-fit: contain;
    background: #fff;
  }
}

.option-wrapper {
  margin-bottom: 10px;
}

.option-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
  align-items: flex-start;
}

.option-group :deep(.el-radio) {
  display: block;
  width: 100%;
  margin-right: 0;
}

.option-group :deep(.el-radio__label) {
  width: 100%;
  text-align: left;
}

.analysis-block {
  margin-top: 12px;
  padding-top: 8px;
  border-top: 1px dashed #ebeef5;

  .result-line {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 6px;
  }

  .user-answer {
    color: #606266;
  }

  .wrong-book-action {
    margin-top: 8px;
  }
}

.submit-bar {
  margin-top: 16px;
  text-align: right;
}

.aside-card {
  border-radius: 12px;
}

.meta-list {
  list-style: none;
  padding: 0;
  margin: 0;

  li {
    display: flex;
    justify-content: space-between;
    padding: 6px 0;

    span {
      color: #909399;
    }
  }
}

.mt-12 {
  margin-top: 12px;
}
</style>
