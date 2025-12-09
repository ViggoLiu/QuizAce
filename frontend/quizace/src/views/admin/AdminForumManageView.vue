<template>
  <div class="admin-forum-manage-view">
    <div class="page-header">
      <div>
        <h1>🗂️ 论坛管理</h1>
        <p>查看学生与老师的全部发言，快速处理违规内容</p>
      </div>
      <el-tag type="danger" effect="plain">管理员专用</el-tag>
    </div>

    <el-card shadow="hover" class="filter-card">
      <div class="filter-grid">
        <el-input
          class="filter-field"
          v-model="filters.keyword"
          placeholder="搜索内容或用户名"
          clearable
          @clear="handleSearch"
          @keyup.enter="handleSearch"
          prefix-icon="el-icon-search"
        />
        <el-select class="filter-field" v-model="filters.userRole" placeholder="用户角色" clearable>
          <el-option label="全部角色" value="" />
          <el-option label="学生" value="student" />
          <el-option label="老师" value="teacher" />
        </el-select>
        <el-select class="filter-field" v-model="filters.speechType" placeholder="发言类型" clearable>
          <el-option label="全部发言" value="" />
          <el-option label="评论" value="comment" />
          <el-option label="回复" value="reply" />
          <el-option label="学习资源评论" value="resource_comment" />
        </el-select>
        <el-select class="filter-field" v-model="filters.sourceType" placeholder="来源" clearable>
          <el-option label="全部来源" value="" />
          <el-option label="论坛" value="forum" />
          <el-option label="学习资源" value="resource" />
        </el-select>
        <el-date-picker
          class="filter-field date-field"
          v-model="filters.dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          value-format="YYYY-MM-DD"
          unlink-panels
        />
        <div class="filter-actions">
          <el-button type="primary" @click="handleSearch" :loading="loading">查询</el-button>
          <el-button @click="resetFilters" :disabled="loading">重置</el-button>
        </div>
      </div>
    </el-card>

    <el-card shadow="hover" class="table-card">
      <div class="table-header">
        <div>
          <h2>发言列表</h2>
          <small>共 {{ pagination.total }} 条记录</small>
        </div>
        <el-button type="primary" text icon="el-icon-refresh" @click="handleSearch" :loading="loading">
          刷新
        </el-button>
      </div>

      <el-table :data="records" v-loading="loading" border stripe>
        <el-table-column type="index" label="#" width="60" />
        <el-table-column label="类型" width="140">
          <template #default="{ row }">
            <el-tag :type="speechTypeTag(row.type)">
              {{ speechTypeLabel(row.type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="来源" width="140">
          <template #default="{ row }">
            <el-tag :type="originTag(row.origin)">
              {{ originLabel(row.origin) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="用户" min-width="160">
          <template #default="{ row }">
            <div class="user-cell">
              <span class="user-name">{{ row.user?.username || '-' }}</span>
              <span class="user-role">{{ roleLabel(row.user?.role) }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="内容" min-width="320" show-overflow-tooltip>
          <template #default="{ row }">
            <div class="content-cell">
              <span class="content-text">{{ row.content }}</span>
              <div v-if="row.origin === 'resource'" class="resource-brief">
                <el-tag type="warning" size="small" effect="plain">
                  {{ row.resource?.name || '资源已删除' }}
                </el-tag>
                <span>{{ row.resource?.course || '未关联课程' }}</span>
                <span v-if="row.target_excerpt">{{ row.target_excerpt }}</span>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="关联对象" min-width="240" show-overflow-tooltip>
          <template #default="{ row }">
            <span v-if="row.type === 'reply'">
              回复 {{ row.to_user?.username || '用户' }} · {{ row.target_excerpt || '所属评论' }}
            </span>
            <span v-else-if="row.origin === 'resource'">
              {{ row.resource?.name || '资源已删除' }} · {{ row.resource?.course || '无课程信息' }}
            </span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="互动" width="160">
          <template #default="{ row }">
            <div v-if="row.type === 'comment'" class="stat-cell">
              <span>👍 {{ row.like_count }}</span>
              <span>💬 {{ row.reply_count }}</span>
            </div>
            <div v-else-if="row.origin === 'resource'" class="stat-cell">
              <span>⭐ {{ row.rating ? row.rating + ' 分' : '未评分' }}</span>
              <span>👍 {{ row.like_count }}</span>
            </div>
            <span v-else>—</span>
          </template>
        </el-table-column>
        <el-table-column label="时间" width="200">
          <template #default="{ row }">
            {{ formatTime(row.create_time) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row }">
            <el-button type="danger" size="small" plain @click="openDeleteDialog(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-bar">
        <el-pagination
          background
          layout="total, sizes, prev, pager, next"
          :current-page="pagination.currentPage"
          :page-size="pagination.pageSize"
          :page-sizes="[10, 20, 30, 50]"
          :total="pagination.total"
          @size-change="handlePageSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <el-dialog title="删除发言" v-model="deleteDialogVisible" width="420px">
      <p class="dialog-tip">删除后用户将收到通知，请填写具体原因</p>
      <div v-if="currentRecord" class="delete-meta">
        <el-tag size="small" :type="speechTypeTag(currentRecord.type)">
          {{ speechTypeLabel(currentRecord.type) }}
        </el-tag>
        <el-tag size="small" :type="originTag(currentRecord.origin)">
          {{ originLabel(currentRecord.origin) }}
        </el-tag>
      </div>
      <el-input
        type="textarea"
        v-model="deleteReason"
        :rows="4"
        maxlength="120"
        show-word-limit
        placeholder="请输入删除原因"
      />
      <template #footer>
        <el-button @click="deleteDialogVisible = false" :disabled="deleteSubmitting">取消</el-button>
        <el-button type="danger" :loading="deleteSubmitting" @click="confirmDelete">确认删除</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { get, del } from '@/util/request.js'

const loading = ref(false)
const records = ref([])
const pagination = reactive({
  currentPage: 1,
  pageSize: 10,
  total: 0
})
const filters = reactive({
  keyword: '',
  userRole: '',
  speechType: '',
  sourceType: '',
  dateRange: []
})
const deleteDialogVisible = ref(false)
const deleteReason = ref('违规发言')
const deleteSubmitting = ref(false)
const currentRecord = ref(null)

const roleMap = {
  student: '学生',
  teacher: '老师',
  admin: '管理员'
}

const speechTypeMeta = {
  comment: { label: '评论', tag: 'info' },
  reply: { label: '回复', tag: 'success' },
  resource_comment: { label: '资源评论', tag: 'warning' }
}

const originMeta = {
  forum: { label: '论坛', tag: 'primary' },
  resource: { label: '学习资源', tag: 'warning' }
}

const roleLabel = role => roleMap[role] || '—'
const speechTypeLabel = type => speechTypeMeta[type]?.label || '其他'
const speechTypeTag = type => speechTypeMeta[type]?.tag || 'info'
const originLabel = origin => originMeta[origin]?.label || '其他'
const originTag = origin => originMeta[origin]?.tag || 'info'
const formatTime = value => (value ? new Date(value).toLocaleString() : '-')

const buildQuery = () => {
  const params = {
    page: pagination.currentPage,
    page_size: pagination.pageSize
  }
  if (filters.keyword) params.keyword = filters.keyword
  if (filters.userRole) params.role = filters.userRole
  if (filters.speechType) params.type = filters.speechType
  if (filters.sourceType) params.source = filters.sourceType
  if (filters.dateRange && filters.dateRange.length === 2) {
    params.start_date = filters.dateRange[0]
    params.end_date = filters.dateRange[1]
  }
  return params
}

const fetchRecords = async () => {
  loading.value = true
  try {
    const { data } = await get('/forum/admin/moderation/', buildQuery())
    records.value = data.results || []
    pagination.total = data.count || 0
  } catch (error) {
    console.error(error)
    ElMessage.error('获取发言列表失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.currentPage = 1
  fetchRecords()
}

const resetFilters = () => {
  filters.keyword = ''
  filters.userRole = ''
  filters.speechType = ''
  filters.sourceType = ''
  filters.dateRange = []
  handleSearch()
}

const handlePageChange = page => {
  pagination.currentPage = page
  fetchRecords()
}

const handlePageSizeChange = size => {
  pagination.pageSize = size
  pagination.currentPage = 1
  fetchRecords()
}

const openDeleteDialog = record => {
  currentRecord.value = record
  deleteReason.value = '违规发言'
  deleteDialogVisible.value = true
}

const confirmDelete = async () => {
  if (!currentRecord.value) return
  deleteSubmitting.value = true
  try {
    const speechType = currentRecord.value.type || 'comment'
    await del(
      `/forum/admin/moderation/${currentRecord.value.id}/`,
      { type: speechType },
      { data: { deleted_reason: deleteReason.value } }
    )
    ElMessage.success('删除成功')
    deleteDialogVisible.value = false
    fetchRecords()
  } catch (error) {
    console.error(error)
    ElMessage.error('删除失败，请稍后重试')
  } finally {
    deleteSubmitting.value = false
  }
}

onMounted(fetchRecords)
</script>

<style lang="scss" scoped>
.admin-forum-manage-view {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 4px;

  h1 {
    margin: 0;
    font-size: 24px;
  }

  p {
    margin: 4px 0 0;
    color: #606266;
  }
}

.filter-card {
  .filter-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 14px 18px;
    align-items: stretch;
  }

  .filter-field {
    width: 100%;
  }

  .date-field {
    min-width: 280px;
  }

  .filter-actions {
    display: flex;
    gap: 12px;
    justify-content: flex-end;
    flex-wrap: wrap;
  }
}

.table-card {
  .table-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 14px;

    h2 {
      margin: 0;
    }

    small {
      color: #909399;
    }
  }
}

.user-cell {
  display: flex;
  flex-direction: column;
  line-height: 1.4;

  .user-name {
    font-weight: 600;
  }

  .user-role {
    font-size: 12px;
    color: #909399;
  }
}

.stat-cell {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.content-cell {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.resource-brief {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  font-size: 12px;
  color: #909399;
}

.pagination-bar {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

.dialog-tip {
  margin-bottom: 12px;
  color: #909399;
}

.delete-meta {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}
</style>
