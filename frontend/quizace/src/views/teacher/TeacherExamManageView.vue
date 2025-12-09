<template>
  <div class="teacher-exam-manage-view">
    <section class="hero-card">
      <div>
        <p class="eyebrow">考试发布</p>
        <h1>选择科目，整理题目</h1>
        <p class="subline">快速查看你已上传题目的科目，并按题型整理，便于后续组卷与发布。</p>
      </div>
      <div class="hero-stats">
        <div class="stat-box">
          <span>已建科目</span>
          <strong>{{ totalSubjects }}</strong>
        </div>
        <div class="stat-box">
          <span>当前科目题量</span>
          <strong>{{ activeTotals.total }}</strong>
        </div>
        <div class="stat-box">
          <span>客观 / 主观</span>
          <strong>{{ activeTotals.objective }} / {{ activeTotals.subjective }}</strong>
        </div>
      </div>
    </section>

    <div class="content-grid">
      <el-card class="subject-panel" shadow="never">
        <template #header>
          <div class="panel-header">
            <div>
              <h2>上传过题目的科目</h2>
              <p>点击科目以查看该科目的客观题与主观题</p>
            </div>
            <el-button type="primary" link @click="fetchSubjectStats">刷新</el-button>
          </div>
        </template>
        <div class="subject-list" v-loading="subjectLoading">
          <el-empty v-if="!subjectLoading && !subjects.length" description="暂无科目，先去上传题目吧" />
          <el-scrollbar v-else>
            <div
              v-for="subject in subjects"
              :key="subject.subject_id"
              class="subject-item"
              :class="{ active: subject.subject_id === activeSubjectId }"
              @click="handleSelectSubject(subject)"
            >
              <div>
                <p class="subject-name">{{ subject.subject_name }}</p>
                <small>最后更新：{{ formatDate(subject.last_updated) }}</small>
              </div>
              <div class="subject-counts">
                <el-tag size="small" type="success">客观 {{ subject.objective_questions }}</el-tag>
                <el-tag size="small" type="warning">主观 {{ subject.subjective_questions }}</el-tag>
                <el-tag size="small" type="info">总计 {{ subject.total_questions }}</el-tag>
              </div>
            </div>
          </el-scrollbar>
        </div>
      </el-card>

      <el-card class="question-panel" shadow="never" v-loading="questionLoading">
        <template #header>
          <div class="panel-header">
            <div>
              <h2>{{ activeSubject?.subject_name || '请选择科目' }}</h2>
              <p v-if="activeSubject">共有 {{ activeSubject.total_questions }} 道题，最近更新 {{ formatDate(activeSubject.last_updated) }}</p>
            </div>
            <el-button
              v-if="activeSubject"
              type="primary"
              @click="fetchQuestionsForSubject(activeSubject.subject_id)"
            >重新获取</el-button>
          </div>
        </template>
        <el-empty v-if="!activeSubject" description="先在左侧选择一个科目" />
        <div v-else>
          <div class="selection-summary">
            <div>
              <h4>抽题发布</h4>
              <p>需选择 5 道客观题与 5 道主观题，每题 10 分，共 100 分。</p>
              <p class="selection-stats">
                客观：<strong>{{ selectedQuestions.objective.length }}/5</strong>
                <span class="divider" />
                主观：<strong>{{ selectedQuestions.subjective.length }}/5</strong>
              </p>
            </div>
            <div class="selection-actions">
              <el-button size="small" @click="clearSelections" :disabled="!hasSelection">清空选择</el-button>
              <el-button type="primary" size="small" :disabled="!isSelectionComplete" @click="openPublishDialog">
                发布考试
              </el-button>
            </div>
          </div>
          <section
            v-for="group in questionGroups"
            :key="group.key"
            class="question-group"
          >
            <div class="group-header">
              <h3>{{ group.title }}</h3>
              <span>{{ questionLists[group.key].length }} 道</span>
            </div>
            <el-empty
              v-if="!questionLists[group.key].length"
              :description="group.empty"
            />
            <div v-else class="question-cards">
              <div
                v-for="question in questionLists[group.key]"
                :key="question.id"
                class="question-card"
                :class="{ selected: isSelected(group.key, question.id) }"
              >
                <div class="q-title">{{ question.content || '图文题目' }}</div>
                <div class="q-meta">
                  <span>分值：{{ question.score }}</span>
                  <span>来源：{{ question.source_mode === 'ocr' ? 'OCR' : '手动' }}</span>
                  <span>状态：{{ translateStatus(question.status) }}</span>
                </div>
                <div class="q-foot">
                  <span>提交于 {{ formatDate(question.updated_at || question.created_at) }}</span>
                  <el-tag v-if="question.media_url" size="small" type="info">含图片</el-tag>
                </div>
                <div class="q-actions">
                  <div class="q-actions-left">
                    <el-button
                      v-if="question.media_url"
                      size="small"
                      text
                      type="info"
                      @click="openPreview(question)"
                    >查看图片</el-button>
                    <el-button
                      size="small"
                      text
                      type="primary"
                      @click="openEditDialog(question)"
                    >编辑答案</el-button>
                    <el-button
                      size="small"
                      text
                      type="danger"
                      :loading="deleteLoadingId === question.id"
                      @click="handleDeleteQuestion(question)"
                    >删除题目</el-button>
                  </div>
                  <el-button
                    size="small"
                    :type="isSelected(group.key, question.id) ? 'danger' : 'primary'"
                    @click="toggleQuestionSelection(group.key, question)"
                  >{{ isSelected(group.key, question.id) ? '取消选择' : '加入试卷' }}</el-button>
                </div>
              </div>
            </div>
          </section>
        </div>
      </el-card>
    </div>

    <el-dialog
      v-model="publishDialogVisible"
      width="520px"
      title="发布考试"
      destroy-on-close
    >
      <el-form :model="publishForm" label-width="90px" class="publish-form">
        <el-form-item label="考试标题">
          <el-input v-model="publishForm.title" placeholder="请输入考试标题" maxlength="40" show-word-limit />
        </el-form-item>
        <el-form-item label="考试时长">
          <div class="duration-input">
            <el-input-number v-model="publishForm.durationMinutes" :min="30" :max="180" />
            <span>分钟</span>
          </div>
        </el-form-item>
        <el-form-item label="开始时间">
          <el-date-picker
            v-model="publishForm.startTime"
            type="datetime"
            placeholder="请选择开始时间"
            format="YYYY-MM-DD HH:mm"
          />
        </el-form-item>
        <el-form-item label="结束时间">
          <el-date-picker
            v-model="publishForm.endTime"
            type="datetime"
            placeholder="请选择结束时间"
            format="YYYY-MM-DD HH:mm"
          />
        </el-form-item>
        <el-form-item label="考试说明">
          <el-input
            v-model="publishForm.description"
            type="textarea"
            :rows="3"
            placeholder="可填写给学生的提示"
            maxlength="120"
            show-word-limit
          />
        </el-form-item>
        <el-alert
          title="固定题目：客观 5 道 + 主观 5 道，每题 10 分，满分 100 分"
          type="info"
          show-icon
        />
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="publishDialogVisible = false" :disabled="submitLoading">取消</el-button>
          <el-button type="primary" :loading="submitLoading" @click="handlePublish">确认发布</el-button>
        </span>
      </template>
    </el-dialog>

    <el-dialog
      v-model="editDialogVisible"
      width="520px"
      title="编辑参考答案"
      destroy-on-close
    >
      <div v-if="editingQuestion" class="edit-dialog-body">
        <div class="edit-meta">
          <el-tag size="small">{{ questionTypeLabel(editingQuestion.question_type) }}</el-tag>
          <span>{{ editingQuestion.subject_name }}</span>
        </div>
        <p class="edit-question-content">{{ editingQuestion.content || '图文题目' }}</p>
        <el-form label-width="90px" class="edit-form">
          <el-form-item label="参考答案">
            <el-input
              v-if="editingQuestion.question_type === 'objective'"
              v-model="editForm.answer"
              placeholder="请输入正确选项，如 A 或 ABC"
              maxlength="8"
              clearable
            />
            <el-input
              v-else
              v-model="editForm.answer"
              type="textarea"
              :rows="4"
              placeholder="请输入参考答案"
              maxlength="400"
              show-word-limit
            />
          </el-form-item>
          <el-form-item label="答案解析">
            <el-input
              v-model="editForm.analysis"
              type="textarea"
              :rows="3"
              placeholder="可选，填写解析或批阅要点"
              maxlength="300"
              show-word-limit
            />
          </el-form-item>
          <el-form-item v-if="editingQuestion.question_type === 'objective' && editingQuestion.options" label="选项预览">
            <ul class="preview-options compact">
              <li v-for="(text, label) in editingQuestion.options" :key="label">
                <strong>{{ label }}.</strong>
                <span>{{ text }}</span>
              </li>
            </ul>
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="editDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleEditSubmit">保存</el-button>
        </span>
      </template>
    </el-dialog>

    <el-dialog
      v-model="previewState.visible"
      width="680px"
      title="题目内容"
      destroy-on-close
      @closed="closePreview"
    >
      <div v-if="previewState.question" class="preview-dialog-body">
        <div class="preview-pill">{{ questionTypeLabel(previewState.question.question_type) }}</div>
        <h4 class="preview-question-title">{{ previewState.question.content || '图文题目' }}</h4>
        <ul
          v-if="previewState.question.question_type === 'objective' && previewState.question.options"
          class="preview-options"
        >
          <li v-for="(text, label) in previewState.question.options" :key="label">
            <strong>{{ label }}.</strong>
            <span>{{ text }}</span>
          </li>
        </ul>
        <div class="preview-meta">
          <el-tag size="small" type="info">分值 {{ previewState.question.score }}</el-tag>
          <el-tag v-if="previewState.question.source_mode === 'ocr'" size="small" type="success">OCR 解析</el-tag>
          <el-tag v-else size="small" type="warning">手动录入</el-tag>
          <el-tag size="small" type="primary">{{ translateStatus(previewState.question.status) }}</el-tag>
        </div>
        <div class="preview-media">
          <el-image
            :src="previewState.question.resolvedMedia"
            fit="contain"
            :preview-src-list="[previewState.question.resolvedMedia]"
          >
            <template #error>
              <div class="preview-media-error">图片加载失败</div>
            </template>
          </el-image>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { get, post, put, del, getMediaBaseUrl } from '@/util/request'

const subjects = ref([])
const subjectLoading = ref(false)
const questionLoading = ref(false)
const activeSubjectId = ref(null)
const questionLists = reactive({ objective: [], subjective: [] })
const questionGroups = [
  { key: 'objective', title: '客观题', empty: '暂无客观题，可先上传选择题' },
  { key: 'subjective', title: '主观题', empty: '暂无主观题，可先上传问答题' }
]
const selectedQuestions = reactive({ objective: [], subjective: [] })
const selectionLimit = { objective: 5, subjective: 5 }
const publishDialogVisible = ref(false)
const submitLoading = ref(false)
const publishForm = reactive({
  title: '',
  durationMinutes: 60,
  startTime: null,
  endTime: null,
  description: ''
})
const previewState = reactive({ visible: false, question: null })
const editDialogVisible = ref(false)
const editingQuestion = ref(null)
const editForm = reactive({ answer: '', analysis: '' })
const deleteLoadingId = ref(null)
const mediaBaseUrl = getMediaBaseUrl()
const PER_QUESTION_SCORE = 10

const activeSubject = computed(() => subjects.value.find(item => item.subject_id === activeSubjectId.value) || null)
const totalSubjects = computed(() => subjects.value.length)
const activeTotals = computed(() => ({
  total: activeSubject.value?.total_questions || 0,
  objective: activeSubject.value?.objective_questions || 0,
  subjective: activeSubject.value?.subjective_questions || 0
}))
const hasSelection = computed(() => selectedQuestions.objective.length > 0 || selectedQuestions.subjective.length > 0)
const isSelectionComplete = computed(() => (
  selectedQuestions.objective.length === selectionLimit.objective &&
  selectedQuestions.subjective.length === selectionLimit.subjective
))

const formatDate = value => {
  if (!value) return '暂无记录'
  return new Date(value).toLocaleString('zh-CN', { hour12: false })
}

const translateStatus = status => {
  const mapping = { ready: '可用', draft: '草稿', archived: '已归档' }
  return mapping[status] || status
}

const questionTypeLabel = type => {
  if (type === 'objective') return '客观题'
  if (type === 'subjective') return '主观题'
  if (type === 'mixed') return '组合题'
  return '题目'
}

const formatMediaUrl = value => {
  if (!value) return ''
  if (/^https?:/i.test(value)) return value
  if (value.startsWith('/')) return `${mediaBaseUrl}${value}`
  return `${mediaBaseUrl}/${value}`
}

const openPreview = question => {
  if (!question?.media_url) return
  const resolved = formatMediaUrl(question.media_url)
  if (!resolved) return
  previewState.question = {
    ...question,
    resolvedMedia: resolved,
  }
  previewState.visible = true
}

const closePreview = () => {
  previewState.question = null
}

const resetSelections = () => {
  selectedQuestions.objective = []
  selectedQuestions.subjective = []
}

const clearSelections = () => {
  if (!hasSelection.value) return
  resetSelections()
  ElMessage.success('已清空所选题目')
}

const isSelected = (type, id) => selectedQuestions[type].includes(id)

const toggleQuestionSelection = (type, question) => {
  if (!activeSubject.value) {
    ElMessage.warning('请先选择科目')
    return
  }
  const list = selectedQuestions[type]
  const existingIndex = list.indexOf(question.id)
  if (existingIndex >= 0) {
    list.splice(existingIndex, 1)
    return
  }
  if (list.length >= selectionLimit[type]) {
    ElMessage.warning(`该题型最多选择 ${selectionLimit[type]} 道题`)
    return
  }
  list.push(question.id)
}

const removeQuestionFromSelections = (questionId) => {
  Object.keys(selectedQuestions).forEach(key => {
    const filtered = selectedQuestions[key].filter(id => id !== questionId)
    selectedQuestions[key] = filtered
  })
}

const updateQuestionInState = (question) => {
  const typeKey = question.question_type
  if (!questionLists[typeKey]) return
  const index = questionLists[typeKey].findIndex(item => item.id === question.id)
  if (index >= 0) {
    questionLists[typeKey].splice(index, 1, { ...questionLists[typeKey][index], ...question })
  }
}

const removeQuestionFromState = (question) => {
  const typeKey = question.question_type
  if (!questionLists[typeKey]) return
  const index = questionLists[typeKey].findIndex(item => item.id === question.id)
  if (index >= 0) {
    questionLists[typeKey].splice(index, 1)
  }
  removeQuestionFromSelections(question.id)
}

const openEditDialog = (question) => {
  editingQuestion.value = question
  editForm.answer = question.answer || ''
  editForm.analysis = question.analysis || ''
  editDialogVisible.value = true
}

const handleEditSubmit = async () => {
  if (!editingQuestion.value) return
  const isObjective = editingQuestion.value.question_type === 'objective'
  const answerText = (editForm.answer || '').trim()
  if (!answerText) {
    ElMessage.warning(isObjective ? '请输入客观题标准答案' : '请输入主观题参考答案')
    return
  }
  const payloadAnswer = isObjective ? answerText.toUpperCase() : answerText
  try {
    const response = await put(`/exam/teacher/questions/${editingQuestion.value.id}/`, {
      answer: payloadAnswer,
      analysis: editForm.analysis || ''
    })
    if (response.data.code === 200) {
      const updated = response.data.data
      updateQuestionInState(updated)
      editDialogVisible.value = false
      ElMessage.success('题目答案已更新')
    } else {
      ElMessage.error(response.data.info || '更新失败')
    }
  } catch (error) {
    console.error(error)
    ElMessage.error('更新失败，请稍后重试')
  }
}

const handleDeleteQuestion = (question) => {
  ElMessageBox.confirm('删除后该题目将无法恢复且无法用于考试，是否继续？', '删除题目', {
    confirmButtonText: '确认删除',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    deleteLoadingId.value = question.id
    try {
      const response = await del(`/exam/teacher/questions/${question.id}/`)
      if (response.data.code === 200) {
        removeQuestionFromState(question)
        fetchSubjectStats()
        ElMessage.success('题目已删除')
      } else {
        ElMessage.error(response.data.info || '删除失败')
      }
    } catch (error) {
      console.error(error)
      ElMessage.error('删除失败，请稍后重试')
    } finally {
      deleteLoadingId.value = null
    }
  }).catch(() => {})
}

const hydratePublishForm = () => {
  const subjectName = activeSubject.value?.subject_name || '综合试卷'
  const now = new Date()
  const start = new Date(now.getTime() + 10 * 60 * 1000)
  publishForm.title = `${subjectName} 综合试卷`
  publishForm.durationMinutes = 60
  publishForm.startTime = start
  publishForm.endTime = new Date(start.getTime() + publishForm.durationMinutes * 60 * 1000)
  publishForm.description = ''
}

const openPublishDialog = () => {
  if (!activeSubject.value) {
    ElMessage.warning('请选择科目后再发布考试')
    return
  }
  if (!isSelectionComplete.value) {
    ElMessage.warning('请选择 5 道客观题与 5 道主观题')
    return
  }
  hydratePublishForm()
  publishDialogVisible.value = true
}

const handlePublish = async () => {
  if (!activeSubject.value) {
    ElMessage.warning('请选择科目')
    return
  }
  const title = (publishForm.title || '').trim()
  if (!title) {
    ElMessage.warning('请填写考试标题')
    return
  }
  if (!publishForm.startTime || !publishForm.endTime) {
    ElMessage.warning('请设置开始与结束时间')
    return
  }
  const startDate = new Date(publishForm.startTime)
  const endDate = new Date(publishForm.endTime)
  if (Number.isNaN(startDate.getTime()) || Number.isNaN(endDate.getTime())) {
    ElMessage.warning('时间格式不正确')
    return
  }
  if (endDate <= startDate) {
    ElMessage.warning('结束时间需晚于开始时间')
    return
  }
  const durationSeconds = Math.max(600, Math.floor((Number(publishForm.durationMinutes) || 60) * 60))
  const questionIds = [...selectedQuestions.objective, ...selectedQuestions.subjective]
  submitLoading.value = true
  try {
    const response = await post('/exam/assignments/', {
      title,
      subject_id: activeSubjectId.value,
      duration_seconds: durationSeconds,
      start_time: startDate.toISOString(),
      end_time: endDate.toISOString(),
      description: publishForm.description || '',
      question_ids: questionIds,
      per_question_score: PER_QUESTION_SCORE,
      status: 'published'
    })
    if (response.data.code === 200) {
      ElMessage.success(response.data.info || '考试发布成功')
      publishDialogVisible.value = false
      resetSelections()
    } else {
      ElMessage.error(response.data.info || '考试发布失败')
    }
  } catch (error) {
    console.error(error)
    const message = error?.response?.data?.info || '网络异常，发布失败'
    ElMessage.error(message)
  } finally {
    submitLoading.value = false
  }
}

const fetchSubjectStats = async () => {
  subjectLoading.value = true
  try {
    const response = await get('/exam/teacher/questions/subjects/')
    if (response.data.code === 200) {
      subjects.value = response.data.data || []
      if (subjects.value.length) {
        handleSelectSubject(subjects.value[0])
      } else {
        activeSubjectId.value = null
        questionLists.objective = []
        questionLists.subjective = []
        resetSelections()
      }
    } else {
      ElMessage.error(response.data.info || '获取科目信息失败')
    }
  } catch (error) {
    console.error(error)
    ElMessage.error('网络异常，无法获取科目信息')
  } finally {
    subjectLoading.value = false
  }
}

const fetchQuestionsForSubject = async subjectId => {
  if (!subjectId) return
  questionLoading.value = true
  try {
    const [objectiveResp, subjectiveResp] = await Promise.all([
      get('/exam/teacher/questions/', { subject_id: subjectId, question_type: 'objective' }),
      get('/exam/teacher/questions/', { subject_id: subjectId, question_type: 'subjective' })
    ])
    if (objectiveResp.data.code === 200) {
      questionLists.objective = objectiveResp.data.data || []
    } else {
      questionLists.objective = []
      ElMessage.error(objectiveResp.data.info || '获取客观题失败')
    }
    if (subjectiveResp.data.code === 200) {
      questionLists.subjective = subjectiveResp.data.data || []
    } else {
      questionLists.subjective = []
      ElMessage.error(subjectiveResp.data.info || '获取主观题失败')
    }
  } catch (error) {
    console.error(error)
    ElMessage.error('网络异常，无法获取题目')
    questionLists.objective = []
    questionLists.subjective = []
  } finally {
    questionLoading.value = false
  }
}

const handleSelectSubject = subject => {
  if (!subject) return
  activeSubjectId.value = subject.subject_id
  resetSelections()
  fetchQuestionsForSubject(subject.subject_id)
}

watch(activeSubjectId, value => {
  if (!value) {
    resetSelections()
  }
})

onMounted(() => {
  fetchSubjectStats()
})
</script>

<style lang="scss" scoped>
.teacher-exam-manage-view {
  min-height: 100vh;
  padding: 24px;
  background: #eef3f7;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.hero-card {
  border-radius: 18px;
  padding: 24px;
  background: linear-gradient(135deg, #0f6ba8, #11a37f);
  color: #fff;
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 24px;
}

.eyebrow {
  text-transform: uppercase;
  letter-spacing: 4px;
  font-size: 12px;
  opacity: 0.8;
  margin: 0 0 10px;
}

.hero-card h1 {
  margin: 0;
  font-size: 30px;
}

.subline {
  margin-top: 6px;
  max-width: 520px;
  color: rgba(255, 255, 255, 0.85);
}

.hero-stats {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.stat-box {
  min-width: 140px;
  padding: 14px 18px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.18);
  backdrop-filter: blur(6px);
  text-align: center;
}

.stat-box span {
  display: block;
  font-size: 13px;
  opacity: 0.85;
}

.stat-box strong {
  display: block;
  margin-top: 6px;
  font-size: 26px;
}

.content-grid {
  display: grid;
  grid-template-columns: 360px 1fr;
  gap: 20px;
}

.subject-panel,
.question-panel {
  border-radius: 16px;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.panel-header h2 {
  margin: 0;
  font-size: 18px;
}

.panel-header p {
  margin: 2px 0 0;
  color: #72808f;
}

.subject-list {
  max-height: 560px;
}

.subject-item {
  border: 1px solid transparent;
  border-radius: 12px;
  padding: 14px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
  transition: border 0.2s, background 0.2s;
  cursor: pointer;
}

.subject-item.active {
  border-color: #0f6ba8;
  background: rgba(15, 107, 168, 0.08);
}

.subject-item:hover {
  border-color: #11a37f;
}

.subject-name {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

.subject-counts {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.question-group {
  margin-bottom: 28px;
}

.group-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.group-header h3 {
  margin: 0;
}

.question-cards {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.question-card {
  border: 1px solid #dbe4ed;
  border-radius: 12px;
  padding: 14px;
  background: #fff;
}

.question-card.selected {
  border-color: #0f6ba8;
  box-shadow: 0 8px 18px rgba(15, 107, 168, 0.12);
}

.q-title {
  font-weight: 600;
  margin-bottom: 8px;
  color: #1a2c3d;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.q-meta {
  display: flex;
  gap: 16px;
  color: #5f6b7c;
  font-size: 13px;
  flex-wrap: wrap;
}

.q-foot {
  margin-top: 10px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
  color: #8a96a8;
}

.q-actions {
  margin-top: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.q-actions-left {
  display: flex;
  gap: 6px;
  align-items: center;
}

.selection-summary {
  border: 1px dashed #b7c6d6;
  background: #f7fbff;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.selection-summary h4 {
  margin: 0 0 6px;
}

.selection-summary p {
  margin: 0;
  color: #5f6b7c;
}

.selection-stats {
  margin-top: 6px;
  font-size: 14px;
  color: #1a2c3d;
}

.selection-stats strong {
  color: #0f6ba8;
  font-size: 16px;
  margin: 0 4px;
}

.selection-stats .divider {
  display: inline-block;
  width: 1px;
  height: 14px;
  background: #d0d8e2;
  margin: 0 10px;
}

.selection-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.duration-input {
  display: flex;
  align-items: center;
  gap: 8px;
}

.preview-dialog-body {
  border: 1px solid #dbe4ed;
  border-radius: 16px;
  padding: 18px;
  background: #f9fbfe;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.preview-pill {
  align-self: flex-start;
  background: #0f6ba8;
  color: #fff;
  padding: 4px 12px;
  border-radius: 999px;
  font-size: 13px;
}

.preview-question-title {
  margin: 0;
  font-size: 18px;
  color: #152332;
  line-height: 1.4;
}

.preview-options {
  list-style: none;
  padding: 0;
  margin: 0;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  background: #fff;
}

.preview-options li {
  padding: 10px 14px;
  display: flex;
  gap: 6px;
  border-bottom: 1px solid #edf1f7;
}

.preview-options li:last-child {
  border-bottom: none;
}

.preview-options strong {
  color: #0f6ba8;
}

.preview-meta {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.preview-media {
  border-radius: 14px;
  background: #fff;
  border: 1px solid #e2e8f0;
  padding: 12px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.preview-media :deep(.el-image) {
  width: 100%;
}

.preview-media-error {
  padding: 60px 0;
  color: #c0c4cc;
  text-align: center;
}

.edit-dialog-body {
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  padding: 16px;
  background: #fdfefe;
}

.edit-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 13px;
  color: #5f6b7c;
}

.edit-question-content {
  margin: 12px 0 18px;
  font-weight: 600;
  color: #1a2c3d;
}

.preview-options.compact {
  background: #f6f8fb;
}

.preview-options.compact li {
  border-bottom: 1px solid #e3e9f2;
}

.preview-options.compact li:last-child {
  border-bottom: none;
}

@media (max-width: 1200px) {
  .content-grid {
    grid-template-columns: 1fr;
  }

  .subject-list {
    max-height: none;
  }
}
</style>
