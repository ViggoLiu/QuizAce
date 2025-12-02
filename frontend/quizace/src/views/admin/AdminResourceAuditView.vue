<template>
  <div class="admin-resource-audit-view">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>📋 资源审核</h1>
      <p>审核用户上传的学习资源，确保资源质量和合规性</p>
    </div>

    <!-- 筛选条件 -->
    <el-card class="filter-card" shadow="hover">
      <el-form :inline="true" :model="filterForm" class="filter-form">
        <el-form-item label="关键词">
          <el-input v-model="filterForm.keyword" placeholder="资源名称" clearable />
        </el-form-item>
        <el-form-item label="所属学院">
          <el-select v-model="filterForm.college" placeholder="请选择学院" clearable>
            <el-option
              v-for="college in colleges"
              :key="college"
              :label="college"
              :value="college"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="所属课程">
          <el-select v-model="filterForm.course" placeholder="请选择课程" clearable>
            <el-option
              v-for="course in courses"
              :key="course"
              :label="course"
              :value="course"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="审核状态">
          <el-select v-model="filterForm.status" placeholder="请选择状态" clearable>
            <el-option label="全部" :value="''" />
            <el-option label="审核中" :value="0" />
            <el-option label="已通过" :value="1" />
            <el-option label="已拒绝" :value="2" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchResources">搜索</el-button>
          <el-button @click="resetFilter">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 资源列表 -->
    <el-card class="resource-list-card" shadow="hover" style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>待审核资源</span>
          <span class="resource-count">共 {{ resources.length }} 条资源</span>
        </div>
      </template>
      
      <!-- 资源列表内容 -->
      <div class="resource-list">
        <el-empty v-if="resources.length === 0" description="暂无资源" />
        <div v-else>
          <div class="resource-item" v-for="resource in resources" :key="resource.id" @click="showResourceDetail(resource)">
            <div class="resource-cover">
              <div class="cover-icon" :style="{ backgroundColor: getCoverColor(resource.id) }">
                <i class="el-icon-document"></i>
              </div>
            </div>
            <div class="resource-content">
              <div class="resource-header">
                <h3 class="resource-name">{{ resource.name }}</h3>
                <el-tag size="small" :type="getResourceStatusType(resource.status)">
                  {{ getResourceStatusText(resource.status) }}
                </el-tag>
              </div>
              <div class="resource-meta">
                <span class="meta-item">{{ resource.college }}</span>
                <span class="meta-item">{{ resource.course }}</span>
                <span class="meta-item">{{ resource.uploader_name }}</span>
                <span class="meta-item">{{ formatDate(resource.create_time) }}</span>
              </div>
              <div class="resource-stats">
                <span class="stat-item">
                  <i class="el-icon-view"></i>
                  <span>{{ resource.click_count }} 浏览</span>
                </span>
                <span class="stat-item">
                  <i class="el-icon-download"></i>
                  <span>{{ resource.download_count }} 下载</span>
                </span>
                <span class="stat-item">
                  <i class="el-icon-star-on"></i>
                  <span>{{ resource.favorite_count }} 收藏</span>
                </span>
              </div>
            </div>
            <div class="resource-actions">
              <!-- 审核中状态 -->
              <el-button 
                v-if="resource.status === 0" 
                type="success" 
                size="small" 
                @click.stop="auditResource(resource, 1)"
              >
                通过
              </el-button>
              <el-button 
                v-if="resource.status === 0" 
                type="danger" 
                size="small" 
                @click.stop="showRejectDialog(resource)"
              >
                拒绝
              </el-button>
              
              <!-- 已通过状态 -->
              <el-button 
                v-if="resource.status === 1" 
                type="warning" 
                size="small" 
                @click.stop="auditResource(resource, 0)"
              >
                打回审核
              </el-button>
              <el-button 
                v-if="resource.status === 1" 
                type="danger" 
                size="small" 
                @click.stop="showRejectDialog(resource)"
              >
                拒绝
              </el-button>
              
              <!-- 已拒绝状态 -->
              <el-button 
                v-if="resource.status === 2" 
                type="primary" 
                size="small" 
                @click.stop="auditResource(resource, 0)"
              >
                恢复审核
              </el-button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 分页 -->
      <div class="pagination" v-if="resources.length > 0">
        <el-pagination
          background
          layout="prev, pager, next"
          :total="totalResources"
          :page-size="pageSize"
          :current-page="currentPage"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 资源详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="资源详情"
      width="70%"
      center
    >
      <div v-if="currentResource" class="resource-detail">
        <div class="detail-header">
          <h2>{{ currentResource.name }}</h2>
          <el-tag size="medium" :type="getResourceStatusType(currentResource.status)">
            {{ getResourceStatusText(currentResource.status) }}
          </el-tag>
        </div>
        
        <div class="detail-info">
          <div class="info-grid">
            <div class="info-item">
              <div class="info-label">所属学院</div>
              <div class="info-value">{{ currentResource.college }}</div>
            </div>
            <div class="info-item">
              <div class="info-label">所属课程</div>
              <div class="info-value">{{ currentResource.course }}</div>
            </div>
            <div class="info-item">
              <div class="info-label">上传者</div>
              <div class="info-value">{{ currentResource.uploader_name }}</div>
            </div>
            <div class="info-item">
              <div class="info-label">上传时间</div>
              <div class="info-value">{{ formatDate(currentResource.create_time) }}</div>
            </div>
            <div class="info-item">
              <div class="info-label">文件类型</div>
              <div class="info-value">{{ currentResource.file_type || '文件' }}</div>
            </div>
            <div class="info-item">
              <div class="info-label">文件大小</div>
              <div class="info-value">{{ currentResource.file_size || '未知' }}</div>
            </div>
          </div>
          
          <div class="detail-description">
            <div class="info-label">资源简介</div>
            <div class="description-content">{{ currentResource.description || '暂无简介' }}</div>
          </div>
        </div>
        
        <div class="detail-actions">
          <!-- 审核中状态 -->
          <template v-if="currentResource.status === 0">
            <el-button type="success" @click="auditResource(currentResource, 1)">通过审核</el-button>
            <el-button type="danger" @click="showRejectDialog(currentResource)">拒绝审核</el-button>
          </template>
          
          <!-- 已通过状态 -->
          <template v-else-if="currentResource.status === 1">
            <el-button type="warning" @click="auditResource(currentResource, 0)">打回审核</el-button>
            <el-button type="danger" @click="showRejectDialog(currentResource)">拒绝审核</el-button>
          </template>
          
          <!-- 已拒绝状态 -->
          <template v-else-if="currentResource.status === 2">
            <el-button type="primary" @click="auditResource(currentResource, 0)">恢复审核</el-button>
          </template>
        </div>
      </div>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="detailDialogVisible = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 拒绝审核对话框 -->
    <el-dialog
      v-model="rejectDialogVisible"
      title="拒绝审核"
      width="500px"
      center
    >
      <el-form :model="rejectForm" :rules="rejectRules" ref="rejectFormRef">
        <el-form-item label="资源名称" prop="resourceName">
          <el-input v-model="rejectForm.resourceName" readonly />
        </el-form-item>
        <el-form-item label="拒绝原因" prop="reason">
          <el-input
            v-model="rejectForm.reason"
            type="textarea"
            :rows="4"
            placeholder="请输入拒绝原因（必填）"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="rejectDialogVisible = false">取消</el-button>
          <el-button type="danger" @click="handleReject">确认拒绝</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { get, post } from '@/util/request.js'

// 筛选表单
const filterForm = ref({
  keyword: '',
  college: '',
  course: '',
  status: ''
})

// 资源列表
const resources = ref([])
const totalResources = ref(0)
const pageSize = ref(9)
const currentPage = ref(1)

// 学院和课程选项（实际项目中可从API获取）
const colleges = ref(['计算机学院', '电子工程学院', '机械工程学院', '经济管理学院', '文学院'])
const courses = ref(['高等数学', '大学英语', '计算机基础', '数据结构', '操作系统', '数据库原理'])

// 资源详情对话框
const detailDialogVisible = ref(false)
const currentResource = ref(null)

// 拒绝审核对话框
const rejectDialogVisible = ref(false)
const rejectForm = ref({
  resourceName: '',
  reason: ''
})
const rejectRules = ref({
  reason: [{ required: true, message: '请输入拒绝原因', trigger: 'blur' }]
})
const rejectFormRef = ref(null)
let rejectResource = null

// 格式化日期
const formatDate = (dateString) => {
  const date = new Date(dateString)
  const options = { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' }
  return date.toLocaleDateString('zh-CN', options)
}

// 获取封面颜色
const getCoverColor = (id) => {
  const colors = [
    '#667eea', '#764ba2', '#f093fb', '#f5576c',
    '#4facfe', '#00f2fe', '#43e97b', '#38f9d7',
    '#fa709a', '#fee140', '#fa709a', '#fee140'
  ]
  return colors[id % colors.length]
}

// 获取资源状态文本
const getResourceStatusText = (status) => {
  const statusMap = {
    0: '审核中',
    1: '已通过',
    2: '已拒绝'
  }
  return statusMap[status] || '未知'
}

// 获取资源状态类型
const getResourceStatusType = (status) => {
  const typeMap = {
    0: 'warning',
    1: 'success',
    2: 'danger'
  }
  return typeMap[status] || 'info'
}

// 获取资源列表
const fetchResources = async () => {
  try {
    // 获取所有资源
    const response = await get('/learning_resource/list/', {
      keyword: filterForm.value.keyword,
      college: filterForm.value.college,
      course: filterForm.value.course,
      page: currentPage.value,
      page_size: pageSize.value,
      all: true // 管理员查看所有状态的资源
    })
    
    if (response.data.code === 200) {
      let allResources = response.data.data
      
      // 在前端进行status筛选
      if (filterForm.value.status !== '' && filterForm.value.status !== undefined) {
        allResources = allResources.filter(resource => resource.status === filterForm.value.status)
      }
      
      resources.value = allResources
      totalResources.value = allResources.length
    } else {
      ElMessage.error(response.data.info || '获取资源失败')
    }
  } catch (error) {
    console.error('获取资源失败:', error)
    ElMessage.error('获取资源失败，请稍后重试')
  }
}

// 重置筛选条件
const resetFilter = () => {
  filterForm.value = {
    keyword: '',
    college: '',
    course: '',
    status: ''
  }
  fetchResources()
}

// 分页处理
const handleCurrentChange = (page) => {
  currentPage.value = page
  fetchResources()
}

// 显示资源详情
const showResourceDetail = (resource) => {
  currentResource.value = resource
  detailDialogVisible.value = true
}

// 显示拒绝审核对话框
const showRejectDialog = (resource) => {
  rejectForm.value = {
    resourceName: resource.name,
    reason: ''
  }
  rejectDialogVisible.value = true
  rejectResource = resource
}

// 审核资源
const auditResource = async (resource, status) => {
  try {
    const response = await post(`/learning_resource/audit/${resource.id}/`, {
      status: status
    })
    
    if (response.data.code === 200) {
      ElMessage.success(status === 1 ? '审核通过' : '审核拒绝')
      // 关闭对话框
      detailDialogVisible.value = false
      rejectDialogVisible.value = false
      // 刷新资源列表
      fetchResources()
    } else {
      ElMessage.error(response.data.info || '审核失败')
    }
  } catch (error) {
    console.error('审核失败:', error)
    ElMessage.error('审核失败，请稍后重试')
  }
}

// 处理拒绝审核
const handleReject = async () => {
  try {
    // 表单验证
    if (!rejectFormRef.value) return
    await rejectFormRef.value.validate()
    
    const response = await post(`/learning_resource/audit/${rejectResource.id}/`, {
      status: 2,
      reason: rejectForm.value.reason
    })
    
    if (response.data.code === 200) {
      ElMessage.success('拒绝审核成功')
      // 关闭对话框
      rejectDialogVisible.value = false
      // 刷新资源列表
      fetchResources()
    } else {
      ElMessage.error(response.data.info || '拒绝审核失败')
    }
  } catch (error) {
    console.error('拒绝审核失败:', error)
    if (error.name === 'Error') {
      // 表单验证失败
      return
    }
    ElMessage.error('拒绝审核失败，请稍后重试')
  }
}

// 组件挂载时获取资源列表
onMounted(() => {
  fetchResources()
})
</script>

<style lang="scss" scoped>
.admin-resource-audit-view {
  padding: 20px;
  background-color: #f8f9fa;
  min-height: 100vh;
}

.page-header {
  margin-bottom: 30px;
  text-align: center;
  padding: 30px 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  color: white;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);

  h1 {
    margin: 0 0 10px 0;
    font-size: 32px;
    font-weight: 600;
    color: white;
  }

  p {
    margin: 0;
    font-size: 16px;
    opacity: 0.9;
  }
}

.filter-card {
  border-radius: 12px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  background-color: white;
  margin-bottom: 20px;
}

.filter-form {
  display: flex;
  align-items: center;
  gap: 15px;
  flex-wrap: wrap;
}

.resource-list-card {
  border-radius: 12px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  background-color: white;
  overflow: hidden;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  font-size: 16px;
  padding: 20px;
  background-color: #fafafa;
  border-bottom: 1px solid #f0f0f0;

  .resource-count {
    font-size: 14px;
    color: #666;
    font-weight: normal;
  }
}

.resource-list {
  padding: 20px;
}

.resource-item {
  display: flex;
  align-items: center;
  padding: 20px;
  border-radius: 12px;
  background-color: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  cursor: pointer;
  margin-bottom: 15px;
  border: 1px solid #f0f0f0;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
    border-color: #e0e0e0;
  }
}

.resource-cover {
  margin-right: 20px;
  flex-shrink: 0;
}

.cover-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  color: white;
  transition: transform 0.3s ease;

  .resource-item:hover & {
    transform: scale(1.05);
  }
}

.resource-content {
  flex: 1;
  min-width: 0;
}

.resource-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.resource-name {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  margin-right: 10px;
}

.resource-meta {
  display: flex;
  gap: 15px;
  margin-bottom: 12px;
  flex-wrap: wrap;
}

.meta-item {
  font-size: 13px;
  color: #909399;
  display: flex;
  align-items: center;
}

.resource-stats {
  display: flex;
  gap: 20px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 13px;
  color: #606266;

  i {
    color: #409EFF;
    font-size: 14px;
  }
}

.resource-actions {
  display: flex;
  gap: 10px;
  flex-shrink: 0;
}

.pagination {
  display: flex;
  justify-content: center;
  margin-top: 30px;
  padding: 20px 0;
  background-color: #fafafa;
  border-top: 1px solid #f0f0f0;
}

/* 资源详情样式 */
.resource-detail {
  padding: 20px 0;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #f0f0f0;

  h2 {
    margin: 0;
    font-size: 24px;
    font-weight: 600;
    color: #303133;
  }
}

.detail-info {
  margin-bottom: 30px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 30px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.info-label {
  font-size: 14px;
  color: #909399;
  font-weight: 500;
}

.info-value {
  font-size: 16px;
  color: #303133;
  font-weight: 600;
}

.detail-description {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #f0f0f0;
}

.description-content {
  font-size: 16px;
  color: #303133;
  line-height: 1.8;
  white-space: pre-wrap;
  background-color: #fafafa;
  padding: 20px;
  border-radius: 8px;
  border: 1px solid #f0f0f0;
}

.detail-actions {
  display: flex;
  gap: 15px;
  justify-content: flex-start;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #f0f0f0;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .info-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .resource-item {
    flex-direction: column;
    align-items: flex-start;
  }

  .resource-cover {
    margin-right: 0;
    margin-bottom: 15px;
  }

  .resource-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }

  .resource-meta {
    gap: 10px;
  }

  .resource-stats {
    gap: 15px;
    margin-bottom: 15px;
  }

  .resource-actions {
    align-self: flex-end;
  }

  .info-grid {
    grid-template-columns: 1fr;
  }
}
</style>
