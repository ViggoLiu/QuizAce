<template>
  <div class="student-dashboard">
    <div class="welcome-section">
      <h1>模拟练习</h1>
      <p>选择科目后即可开启对应的客观题或主观题练习</p>
    </div>

    <el-card class="content-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>选择科目</span>
          <el-button type="text" @click="fetchSubjects" :loading="subjectLoading">刷新</el-button>
        </div>
      </template>
      <el-empty v-if="!subjectLoading && subjects.length === 0" description="暂无科目，请联系老师添加" />
      <el-row v-else :gutter="16">
        <el-col v-for="item in subjects" :key="item.id" :span="6">
          <div class="subject-card" @click="openTypeDialog(item)">
            <h4>{{ item.name }}</h4>
            <p>{{ item.description || '暂无简介' }}</p>
            <el-button type="primary" text>选择练习</el-button>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <el-dialog v-model="typeDialogVisible" title="选择题型" width="360px" destroy-on-close>
      <div v-if="selectedSubject">
        <p class="dialog-tip">当前科目：{{ selectedSubject.name }}</p>
        <el-radio-group v-model="selectedType" class="type-radio-group">
          <el-radio-button v-for="type in questionTypes" :key="type.value" :label="type.value">
            {{ type.label }}
          </el-radio-button>
        </el-radio-group>
      </div>
      <template #footer>
        <el-button @click="typeDialogVisible = false">取消</el-button>
        <el-button type="primary" :disabled="!selectedType" @click="confirmStart">开始答题</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { get } from '@/util/request'

const router = useRouter()

const subjects = ref([])
const subjectLoading = ref(false)
const selectedSubject = ref(null)
const selectedType = ref('objective')
const typeDialogVisible = ref(false)

const questionTypes = [
  { label: '客观题练习（10题）', value: 'objective' },
  { label: '主观题练习（5题）', value: 'subjective' }
]

const fetchSubjects = async () => {
  subjectLoading.value = true
  try {
    const res = await get('/exam/subjects/')
    if (res.data.code === 200) {
      subjects.value = res.data.data || []
    } else {
      subjects.value = []
      ElMessage.error(res.data.info || '获取科目失败，请稍后重试')
    }
  } catch (error) {
    console.error(error)
    subjects.value = []
    ElMessage.error('获取科目失败，请稍后重试')
  } finally {
    subjectLoading.value = false
  }
}

const openTypeDialog = (subject) => {
  selectedSubject.value = subject
  selectedType.value = 'objective'
  typeDialogVisible.value = true
}

const confirmStart = () => {
  if (!selectedSubject.value) {
    return ElMessage.warning('请选择科目')
  }
  typeDialogVisible.value = false
  router.push({
    path: '/student/practice',
    query: {
      subject_id: selectedSubject.value.id,
      subject_name: selectedSubject.value.name,
      question_type: selectedType.value
    }
  })
}

onMounted(() => {
  fetchSubjects()
})
</script>

<style lang="scss" scoped>
.student-dashboard {
  padding: 20px;
}

.welcome-section {
  margin-bottom: 20px;
  padding: 20px;
  background: linear-gradient(120deg, #667eea, #764ba2);
  border-radius: 12px;
  color: #fff;

  h1 {
    margin: 0 0 8px;
    font-size: 28px;
    font-weight: 600;
  }

  p {
    margin: 0;
    opacity: 0.9;
  }
}

.content-card {
  border-radius: 12px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.subject-card {
  border: 1px solid #ebeef5;
  border-radius: 10px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s ease;
  height: 140px;
  margin-bottom: 16px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;

  h4 {
    margin: 0;
  }

  p {
    margin: 8px 0;
    color: #666;
    font-size: 13px;
    line-height: 1.4;
  }

  &:hover {
    border-color: #409eff;
    box-shadow: 0 2px 10px rgba(64, 158, 255, 0.2);
  }
}

.dialog-tip {
  margin-bottom: 12px;
  font-weight: 600;
}

.type-radio-group {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
</style>
