<template>
  <div class="student-wrong-book-view">
    <div class="page-header">
      <div>
        <h2>错题本</h2>
        <p>按照科目筛选并分页复习你的错题。</p>
      </div>
      <div class="header-actions">
        <el-select
          v-model="selectedSubject"
          clearable
          size="small"
          placeholder="全部科目"
          :disabled="loading"
          @change="handleSubjectChange"
        >
          <el-option label="全部科目" value="" />
          <el-option
            v-for="subject in subjectOptions"
            :key="subject.id"
            :label="`${subject.name} (${subject.count})`"
            :value="subject.id"
          />
        </el-select>
        <el-button type="primary" size="small" :loading="loading" @click="refreshEntries">
          刷新
        </el-button>
      </div>
    </div>

    <el-card shadow="never">
      <div class="summary-bar">
        <span>共收录 {{ totalCount }} 道错题</span>
        <span v-if="selectedSubjectName">当前科目：{{ selectedSubjectName }}</span>
      </div>
      <el-skeleton v-if="loading" :rows="6" animated />
      <el-empty v-else-if="!entries.length" description="该科目暂无错题" />
      <div v-else>
        <div class="wrong-question-list">
          <el-card
            v-for="item in entries"
            :key="item.id"
            class="wrong-question-card"
            shadow="hover"
          >
            <div class="card-header">
              <div>
                <p class="question-type">
                  {{ item.question.question_type === 'objective' ? '客观题' : '主观题' }} ·
                  {{ item.question.score }} 分 · {{ item.subject_name }}
                </p>
                <h4>{{ item.question.content }}</h4>
              </div>
              <div class="card-meta">
                <el-tag type="warning" size="small">错 {{ item.wrong_times }} 次</el-tag>
                <small>{{ formatDateTime(item.last_wrong_at) }}</small>
                <el-button
                  type="text"
                  size="small"
                  :loading="isRemoving(item.id)"
                  @click="removeEntry(item.id)"
                >
                  移出
                </el-button>
              </div>
            </div>
            <div v-if="item.question.question_type === 'objective'" class="option-list">
              <div
                v-for="(text, key) in item.question.options || {}"
                :key="key"
                class="option-item"
                :class="{ 'is-answer': key === item.question.answer }"
              >
                {{ key }}. {{ text }}
              </div>
            </div>
            <p class="user-answer"><strong>我的答案：</strong>{{ item.last_user_answer || '未作答' }}</p>
            <p class="reference"><strong>参考答案：</strong>{{ item.question.answer || '暂无' }}</p>
            <p v-if="item.question.analysis" class="analysis">
              <strong>解析：</strong>{{ item.question.analysis }}
            </p>
          </el-card>
        </div>
        <div class="list-footer">
          <el-pagination
            background
            layout="prev, pager, next, sizes, total"
            :current-page="pagination.page"
            :page-size="pagination.pageSize"
            :page-sizes="[5, 10, 20, 50]"
            :total="pagination.total"
            :disabled="loading"
            @current-change="handlePageChange"
            @size-change="handlePageSizeChange"
          />
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { del, get } from '@/util/request'

const loading = ref(false)
const entries = ref([])
const subjectOptions = ref([])
const selectedSubject = ref('')
const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0,
})
const removingMap = ref({})
const totalCount = computed(() => subjectOptions.value.reduce((sum, subject) => sum + (subject.count || 0), 0))
const selectedSubjectName = computed(() => {
  if (!selectedSubject.value) return ''
  const target = subjectOptions.value.find((item) => item.id === selectedSubject.value)
  return target ? target.name : ''
})

const buildParams = () => {
  const params = {
    page: pagination.page,
    page_size: pagination.pageSize,
  }
  if (selectedSubject.value) {
    params.subject_id = selectedSubject.value
  }
  return params
}

const fetchWrongBook = async () => {
  loading.value = true
  try {
    const res = await get('/exam/wrong-book/items/', buildParams())
    const data = res.data?.data || {}
    entries.value = data.results || []
    pagination.total = data.total || 0
    pagination.page = data.page || pagination.page
    pagination.pageSize = data.page_size || pagination.pageSize
    subjectOptions.value = (data.subjects || [])
      .filter((item) => item.id !== null && item.id !== undefined)
      .map((item) => ({
        ...item,
        id: String(item.id),
      }))
    if (selectedSubject.value && !subjectOptions.value.some((item) => item.id === selectedSubject.value)) {
      selectedSubject.value = ''
    }
    removingMap.value = {}
  } catch (error) {
    console.error(error)
    ElMessage.error('获取错题本失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

const refreshEntries = () => {
  fetchWrongBook()
}

const handleSubjectChange = () => {
  pagination.page = 1
  fetchWrongBook()
}

const handlePageChange = (page) => {
  pagination.page = page
  fetchWrongBook()
}

const handlePageSizeChange = (size) => {
  pagination.pageSize = size
  pagination.page = 1
  fetchWrongBook()
}

const setRemoving = (id, value) => {
  removingMap.value = { ...removingMap.value, [id]: value }
}

const isRemoving = (id) => Boolean(removingMap.value[id])

const removeEntry = async (entryId) => {
  setRemoving(entryId, true)
  try {
    const res = await del(`/exam/wrong-book/items/${entryId}/`)
    if (res.data.code === 200) {
      ElMessage.success('已移出错题本')
      const remaining = Math.max(pagination.total - 1, 0)
      const maxPage = Math.max(1, Math.ceil(remaining / pagination.pageSize))
      if (pagination.page > maxPage) {
        pagination.page = maxPage
      }
      await fetchWrongBook()
    } else {
      ElMessage.error(res.data.info || '操作失败')
    }
  } catch (error) {
    console.error(error)
    ElMessage.error('操作失败，请稍后重试')
  } finally {
    setRemoving(entryId, false)
  }
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

onMounted(() => {
  fetchWrongBook()
})
</script>

<style scoped lang="scss">
.student-wrong-book-view {
  padding: 16px;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;

  h2 {
    margin: 0;
  }

  p {
    margin: 4px 0 0;
    color: #909399;
  }
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.summary-bar {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
  color: #606266;
}

.wrong-question-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.list-footer {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

.wrong-question-card {
  border-radius: 10px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;

  h4 {
    margin: 4px 0 0;
  }

  .question-type {
    margin: 0;
    color: #909399;
  }

  .card-meta {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 4px;

    small {
      color: #909399;
    }
  }
}

.option-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-bottom: 8px;

  .option-item {
    padding: 4px 8px;
    border-radius: 4px;
    background: #f5f7fa;

    &.is-answer {
      border: 1px solid #67c23a;
      background: #f0f9eb;
    }
  }
}

.user-answer,
.reference,
.analysis {
  margin: 4px 0;
  color: #606266;
}

.analysis {
  background: #f5f7fa;
  padding: 8px;
  border-radius: 4px;
}
</style>
