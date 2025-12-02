<template>
  <div class="student-resource-view">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>📚 学习资源</h1>
      <p>探索丰富的学习资料，助力你的学习之旅</p>
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
        <el-form-item>
          <el-button type="primary" @click="fetchResources">搜索</el-button>
          <el-button @click="resetFilter">重置</el-button>
        </el-form-item>
        <el-form-item class="upload-button-item">
          <el-button type="success" @click="showUploadDialog">
            <i class="el-icon-upload2"></i> 上传资源
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 上传资源对话框 -->
    <el-dialog
      v-model="uploadDialogVisible"
      title="上传学习资源"
      width="600px"
      center
    >
      <el-form :model="uploadForm" :rules="uploadRules" ref="uploadFormRef" label-width="100px">
        <el-form-item label="资源名称" prop="name">
          <el-input v-model="uploadForm.name" placeholder="请输入资源名称，默认使用文件名" />
        </el-form-item>
        <el-form-item label="所属学院" prop="college">
          <el-select v-model="uploadForm.college" placeholder="请选择所属学院" style="width: 100%">
            <el-option
              v-for="college in colleges"
              :key="college"
              :label="college"
              :value="college"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="所属课程" prop="course">
          <el-select v-model="uploadForm.course" placeholder="请选择所属课程" style="width: 100%">
            <el-option
              v-for="course in courses"
              :key="course"
              :label="course"
              :value="course"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="资源简介" prop="description">
          <el-input
            v-model="uploadForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入资源简介"
          />
        </el-form-item>
        <el-form-item label="上传文件" prop="file">
          <el-upload
            ref="uploadRef"
            :auto-upload="false"
            :on-change="handleFileChange"
            :file-list="fileList"
            accept=".doc,.docx,.pdf,.txt,.jpg,.png,.gif,.zip,.rar,.7z"
            :limit="1"
          >
            <el-button type="primary">点击选择文件</el-button>
            <template #tip>
              <div class="el-upload__tip">
                支持上传 .doc, .docx, .pdf, .txt, .jpg, .png, .gif, .zip, .rar, .7z 格式文件
              </div>
            </template>
          </el-upload>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="uploadDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleUpload">上传</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 资源列表 -->
    <el-card class="resource-list-card" shadow="hover" style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>资源列表</span>
          <span class="resource-count">共 {{ resources.length }} 条资源</span>
        </div>
      </template>
      
      <!-- 资源列表内容 -->
      <div class="resource-list">
        <el-empty v-if="resources.length === 0" description="暂无资源" />
        <div v-else>
          <div class="resource-item" v-for="resource in resources" :key="resource.id" @click="goToDetail(resource.id)">
            <div class="resource-cover">
              <div class="cover-icon" :style="{ backgroundColor: getCoverColor(resource.id) }">
                <i class="el-icon-document"></i>
              </div>
            </div>
            <div class="resource-content">
              <div class="resource-header">
                <h3 class="resource-name">{{ resource.name }}</h3>
                <el-tag size="small" type="info">{{ resource.file_type || '文件' }}</el-tag>
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
                  <i class="el-icon-star-on"></i>
                  <span>{{ resource.favorite_count }} 收藏</span>
                </span>
                <span class="stat-item">
                  <i class="el-icon-download"></i>
                  <span>{{ resource.download_count }} 下载</span>
                </span>
              </div>
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
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { get, post } from '@/util/request.js'

const router = useRouter()

// 筛选表单
const filterForm = ref({
  keyword: '',
  college: '',
  course: ''
})

// 资源列表
const resources = ref([])
const totalResources = ref(0)
const pageSize = ref(9)
const currentPage = ref(1)

// 学院和课程选项（实际项目中可从API获取）
const colleges = ref(['计算机学院', '电子工程学院', '机械工程学院', '经济管理学院', '文学院'])
const courses = ref(['高等数学', '大学英语', '计算机基础', '数据结构', '操作系统', '数据库原理'])

// 格式化日期
const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN')
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

// 上传资源相关数据
const uploadDialogVisible = ref(false)
const uploadForm = ref({
  name: '',
  college: '',
  course: '',
  description: ''
})
const uploadRules = ref({
  college: [{ required: true, message: '请选择所属学院', trigger: 'change' }],
  course: [{ required: true, message: '请选择所属课程', trigger: 'change' }]
})
const fileList = ref([])
let selectedFile = null
const uploadFormRef = ref(null)
const uploadRef = ref(null)

// 显示上传对话框
const showUploadDialog = () => {
  uploadDialogVisible.value = true
  // 重置表单
  uploadForm.value = {
    name: '',
    college: '',
    course: '',
    description: ''
  }
  fileList.value = []
  selectedFile = null
  if (uploadFormRef.value) {
    uploadFormRef.value.resetFields()
  }
}

// 处理文件选择
const handleFileChange = (file) => {
  selectedFile = file.raw
  fileList.value = [file]
  // 手动触发表单验证
  if (uploadFormRef.value) {
    uploadFormRef.value.validateField('file')
  }
}

// 处理上传
const handleUpload = async () => {
  try {
    // 表单验证
    if (!uploadFormRef.value) return
    await uploadFormRef.value.validate()
    
    // 检查文件是否已选择
    if (!selectedFile) {
      ElMessage.error('请选择上传文件')
      return
    }
    
    // 创建FormData对象
    const formData = new FormData()
    formData.append('name', uploadForm.value.name)
    formData.append('college', uploadForm.value.college)
    formData.append('course', uploadForm.value.course)
    formData.append('description', uploadForm.value.description)
    formData.append('file', selectedFile)
    
    // 调用上传API
    const response = await post('/learning_resource/upload/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    
    if (response.data.code === 200) {
      ElMessage.success(response.data.info)
      // 关闭对话框
      uploadDialogVisible.value = false
      // 刷新资源列表
      fetchResources()
    } else {
      ElMessage.error(response.data.info || '上传失败')
    }
  } catch (error) {
    console.error('上传失败:', error)
    if (error.name === 'Error') {
      // 表单验证失败
      return
    }
    ElMessage.error('上传失败，请稍后重试')
  }
}

// 获取资源列表
const fetchResources = async () => {
  try {
    const response = await get('/learning_resource/list/', {
      keyword: filterForm.value.keyword,
      college: filterForm.value.college,
      course: filterForm.value.course,
      page: currentPage.value,
      page_size: pageSize.value
    })
    
    if (response.data.code === 200) {
      resources.value = response.data.data
      totalResources.value = response.data.data.length // 实际项目中应从API返回total字段
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
    course: ''
  }
  fetchResources()
}

// 分页处理
const handleCurrentChange = (page) => {
  currentPage.value = page
  fetchResources()
}

// 跳转到资源详情
const goToDetail = (resourceId) => {
  router.push(`/student/resource/detail/${resourceId}`)
}

// 查看资源
const viewResource = (resource) => {
  ElMessage.info(`查看资源: ${resource.name}`)
  // 实际项目中应打开资源查看页面或预览
}

// 下载资源
const downloadResource = (resource) => {
  ElMessage.success(`开始下载: ${resource.name}`)
  // 实际项目中应调用下载API
  window.open(resource.file_url, '_blank')
}

// 收藏/取消收藏资源
const toggleFavorite = (resource) => {
  ElMessage.success(`已收藏资源: ${resource.name}`)
  // 实际项目中应调用收藏API
}

// 组件挂载时获取资源列表
onMounted(() => {
  fetchResources()
})
</script>

<style lang="scss" scoped>
.student-resource-view {
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

/* 将上传按钮推到最右侧 */
.filter-form {
  justify-content: space-between;
}

.filter-form > :last-child {
  margin-left: auto;
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

.pagination {
  display: flex;
  justify-content: center;
  margin-top: 30px;
  padding: 20px 0;
  background-color: #fafafa;
  border-top: 1px solid #f0f0f0;
}

// 响应式设计
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
  }
}
</style>