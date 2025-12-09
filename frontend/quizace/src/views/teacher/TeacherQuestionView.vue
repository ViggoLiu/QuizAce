<template>
  <div class="teacher-question-upload">
    <el-card class="upload-intro" shadow="hover">
      <div class="intro-text">
        <h1>上传题目</h1>
        <p>通过上传题干图片快速构建题库，系统将根据题型提供相应的作答方式。</p>
      </div>
      <div class="intro-meta">
        <div class="meta-item">
          <span class="meta-label">当前教师</span>
          <strong>{{ username }}</strong>
        </div>
        <div class="meta-item">
          <span class="meta-label">日期</span>
          <strong>{{ currentDate }}</strong>
        </div>
      </div>
      <div class="intro-actions">
        <el-button type="primary" size="large" @click="openUploadDialog">上传新题目</el-button>
      </div>
    </el-card>

    <el-card class="upload-flow" shadow="never">
      <template #header>
        <div class="card-header">
          <span>上传流程</span>
        </div>
      </template>
      <el-steps :active="1" align-center>
        <el-step title="选择科目与题型" description="确定题目归属科目，选择客观/主观类型" />
        <el-step title="上传题干图片" description="上传题干（及可选解析）图片资源" />
        <el-step title="配置答案" description="客观题选择正确选项，主观题填写参考答案" />
      </el-steps>
    </el-card>
  </div>

  <el-dialog
    title="上传题目设置"
    v-model="uploadDialogVisible"
    width="460px"
    @close="resetQuestionSetupForm"
  >
    <el-form
      ref="questionSetupFormRef"
      :model="questionSetupForm"
      :rules="questionSetupRules"
      label-width="100px"
    >
      <el-form-item label="所属科目" prop="course">
        <el-input v-model="questionSetupForm.course" placeholder="请输入课程或科目名称" />
      </el-form-item>
      <el-form-item label="题目类型" prop="questionType">
        <el-radio-group v-model="questionSetupForm.questionType">
          <el-radio-button label="objective">客观题</el-radio-button>
          <el-radio-button label="subjective">主观题</el-radio-button>
        </el-radio-group>
      </el-form-item>
      <el-alert
        v-if="questionSetupForm.questionType === 'objective'"
        title="客观题默认提供四个选择按钮，请确保题干图片包含选项内容"
        type="info"
        show-icon
      />
      <el-alert
        v-else
        title="主观题仅需题干图片，可设置参考答案供学生参考或作为批阅标准"
        type="success"
        show-icon
        style="margin-top: 12px;"
      />
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="uploadDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleQuestionSetupConfirm">下一步</el-button>
      </span>
    </template>
  </el-dialog>

  <TeacherQuestionUploadStep
    v-if="uploadStepVisible"
    :visible="uploadStepVisible"
    :questionType="uploadContext.questionType"
    :course="uploadContext.course"
    @close="handleUploadStepClose"
    @submit="handleQuestionUploadSubmit"
  />
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
import { useStore } from 'vuex'
import { ElMessage } from 'element-plus'
import TeacherQuestionUploadStep from './TeacherQuestionUploadStep.vue'

const store = useStore()
const username = computed(() => store.getters.getUser?.username || '教师')
const currentDate = computed(() => {
  const date = new Date()
  return date.toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' })
})

const uploadDialogVisible = ref(false)
const uploadStepVisible = ref(false)
const questionSetupForm = reactive({
  course: '',
  questionType: 'objective'
})
const uploadContext = reactive({
  course: '',
  questionType: 'objective'
})
const questionSetupFormRef = ref(null)
const questionSetupRules = {
  course: [{ required: true, message: '请输入所属科目', trigger: 'blur' }],
  questionType: [{ required: true, message: '请选择题目类型', trigger: 'change' }]
}

const openUploadDialog = () => {
  uploadDialogVisible.value = true
}

const resetQuestionSetupForm = () => {
  questionSetupForm.course = ''
  questionSetupForm.questionType = 'objective'
  questionSetupFormRef.value?.clearValidate()
}

const handleQuestionSetupConfirm = () => {
  if (!questionSetupFormRef.value) return
  questionSetupFormRef.value.validate(valid => {
    if (!valid) return
    uploadContext.course = questionSetupForm.course
    uploadContext.questionType = questionSetupForm.questionType
    uploadDialogVisible.value = false
    uploadStepVisible.value = true
  })
}

const handleQuestionUploadSubmit = (payload) => {
  // TODO: 实现API提交题目数据
  ElMessage.success('题目上传成功！')
  handleUploadStepClose()
}

const handleUploadStepClose = () => {
  uploadStepVisible.value = false
  uploadContext.course = ''
  uploadContext.questionType = 'objective'
}
</script>

<style lang="scss" scoped>
.teacher-question-upload {
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.upload-intro {
  display: flex;
  flex-direction: column;
  gap: 16px;
  border-radius: 16px;
  background: linear-gradient(120deg, #f6f8ff, #fef5ff);
  border: none;
}

.intro-text h1 {
  margin: 0;
  font-size: 28px;
  color: #1f2d3d;
}

.intro-text p {
  margin: 8px 0 0;
  color: #606266;
}

.intro-meta {
  display: flex;
  gap: 24px;
  flex-wrap: wrap;
}

.meta-item {
  display: flex;
  flex-direction: column;
  font-size: 14px;
  color: #909399;
}

.meta-item strong {
  margin-top: 4px;
  font-size: 18px;
  color: #303133;
}

.intro-actions {
  margin-top: 8px;
}

.upload-flow {
  border-radius: 16px;
}

.card-header {
  font-weight: 600;
  font-size: 16px;
  color: #303133;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>
