<template>
  <div class="student-resource-detail">
    <!-- 页面标题 -->
    <div class="page-header">
      <el-button type="primary" icon="el-icon-arrow-left" @click="goBack">返回列表</el-button>
      <h1>📚 资源详情</h1>
    </div>

    <!-- 资源基本信息 -->
    <el-card class="resource-detail-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>资源信息</span>
        </div>
      </template>
      
      <div class="resource-detail-content">
        <div class="resource-main-info">
          <h2 class="resource-title">{{ resource.name }}</h2>
          <div class="resource-meta">
            <el-tag size="medium" type="info">{{ resource.file_type || '文件' }}</el-tag>
            <el-tag size="medium" v-if="resource.file_size">{{ resource.file_size }}</el-tag>
          </div>
        </div>
        
        <div class="resource-info-grid">
          <div class="info-item">
            <div class="info-label">所属学院</div>
            <div class="info-value">{{ resource.college }}</div>
          </div>
          <div class="info-item">
            <div class="info-label">所属课程</div>
            <div class="info-value">{{ resource.course }}</div>
          </div>
          <div class="info-item">
            <div class="info-label">上传者</div>
            <div class="info-value">{{ resource.uploader_name }}</div>
          </div>
          <div class="info-item">
            <div class="info-label">上传时间</div>
            <div class="info-value">{{ formatDate(resource.create_time) }}</div>
          </div>
          <div class="info-item">
            <div class="info-label">点击数</div>
            <div class="info-value">{{ resource.click_count }}</div>
          </div>
          <div class="info-item">
            <div class="info-label">收藏数</div>
            <div class="info-value">{{ resource.favorite_count }}</div>
          </div>
          <div class="info-item">
            <div class="info-label">下载数</div>
            <div class="info-value">{{ resource.download_count }}</div>
          </div>
        </div>
        
        <div class="resource-description">
          <div class="info-label">资源简介</div>
          <div class="description-content">{{ resource.description || '暂无简介' }}</div>
        </div>
      </div>
    </el-card>

    <!-- 资源操作 -->
    <div class="resource-actions" style="margin-top: 20px;">
      <el-button type="primary" size="large" @click="viewResource">
        <i class="el-icon-view"></i> 查看资源
      </el-button>
      <el-button type="success" size="large" @click="downloadResource">
        <i class="el-icon-download"></i> 下载资源
      </el-button>
      <el-button 
        :type="isFavorite ? 'warning' : 'default'" 
        size="large" 
        @click="toggleFavorite"
      >
        <i :class="isFavorite ? 'el-icon-star-on' : 'el-icon-star-off'"></i> 
        {{ isFavorite ? '取消收藏' : '收藏资源' }}
      </el-button>
    </div>

    <!-- 相关资源推荐 -->
    <el-card class="related-resources-card" shadow="hover" style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>相关资源推荐</span>
        </div>
      </template>
      
      <div class="related-resources">
        <el-empty v-if="relatedResources.length === 0" description="暂无相关资源" />
        <el-row :gutter="20" v-else>
          <el-col :span="6" v-for="item in relatedResources" :key="item.id">
            <el-card class="related-item" shadow="hover" @click="goToDetail(item.id)">
              <h4 class="related-name">{{ item.name }}</h4>
              <div class="related-info">
                <span>{{ item.course }}</span>
                <span class="related-uploader">{{ item.uploader_name }}</span>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watchEffect } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { get, post, del } from '@/util/request.js'

const router = useRouter()
const route = useRoute()

// 资源ID
const resourceId = computed(() => route.params.id)

// 资源详情
const resource = ref({
  id: '',
  name: '',
  college: '',
  course: '',
  description: '',
  file_url: '',
  file_size: '',
  file_type: '',
  uploader_name: '',
  click_count: 0,
  download_count: 0,
  favorite_count: 0,
  create_time: ''
})

// 是否收藏
const isFavorite = ref(false)

// 相关资源
const relatedResources = ref([])

// 格式化日期
const formatDate = (dateString) => {
  const date = new Date(dateString)
  const options = { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' }
  return date.toLocaleDateString('zh-CN', options)
}

// 检查用户是否已收藏资源
const checkFavoriteStatus = async () => {
  try {
    // 调用检查收藏状态的API
    const response = await get(`/learning_resource/check_favorite/${resourceId.value}/`)
    if (response.data.code === 200) {
      isFavorite.value = response.data.data.is_favorite
    }
  } catch (error) {
    console.error('检查收藏状态失败:', error)
    // 如果API调用失败，默认设为未收藏
    isFavorite.value = false
  }
}

// 获取资源详情
const fetchResourceDetail = async () => {
  try {
    const response = await get(`/learning_resource/detail/${resourceId.value}/`)
    
    if (response.data.code === 200) {
      resource.value = response.data.data
      
      // 检查用户是否已收藏该资源
      await checkFavoriteStatus()
    } else {
      ElMessage.error(response.data.info || '获取资源详情失败')
      goBack()
    }
  } catch (error) {
    console.error('获取资源详情失败:', error)
    ElMessage.error('获取资源详情失败，请稍后重试')
    goBack()
  }
}

// 获取相关资源
const fetchRelatedResources = async () => {
  try {
    const response = await get('/learning_resource/list/', {
      course: resource.value.course,
      page_size: 4
    })
    
    if (response.data.code === 200) {
      // 过滤掉当前资源
      relatedResources.value = response.data.data.filter(item => item.id !== resource.value.id)
    }
  } catch (error) {
    console.error('获取相关资源失败:', error)
  }
}

// 返回列表
const goBack = () => {
  router.push('/student/resource')
}

// 跳转到其他资源详情
const goToDetail = (id) => {
  router.push(`/student/resource/detail/${id}`)
}

// 查看资源
const viewResource = () => {
  ElMessage.info(`查看资源: ${resource.value.name}`)
  // 实际项目中应打开资源查看页面或预览
  window.open(resource.value.file_url, '_blank')
}

// 下载资源
const downloadResource = async () => {
  try {
    ElMessage.success(`开始下载: ${resource.value.name}`);
    // 使用get方法调用下载API，带上Authorization请求头
    const response = await get(`/learning_resource/download/${resource.value.id}/`);
    
    // 处理文件下载
    if (response.status === 200) {
      // 创建Blob对象
      const blob = new Blob([response.data]);
      
      // 创建下载链接
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      
      // 设置文件名
      const filename = resource.value.name;
      link.download = filename;
      
      // 触发下载
      document.body.appendChild(link);
      link.click();
      
      // 清理
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      // 更新本地下载计数
      resource.value.download_count++;
    } else {
      ElMessage.error('下载资源失败，请稍后重试');
    }
  } catch (error) {
    console.error('下载资源失败:', error);
    ElMessage.error('下载资源失败，请稍后重试');
  }
}

// 收藏/取消收藏资源
const toggleFavorite = async () => {
  try {
    if (!isFavorite.value) {
      // 调用收藏API
      await post(`/learning_resource/favorite/${resource.value.id}/`)
      isFavorite.value = true
      ElMessage.success(`已收藏资源: ${resource.value.name}`)
      // 更新本地收藏计数
      resource.value.favorite_count++
    } else {
      // 调用取消收藏API
      await del(`/learning_resource/favorite/${resource.value.id}/`)
      isFavorite.value = false
      ElMessage.success(`已取消收藏资源: ${resource.value.name}`)
      // 更新本地收藏计数
      resource.value.favorite_count--
    }
  } catch (error) {
    console.error('操作失败:', error)
    ElMessage.error('操作失败，请稍后重试')
  }
}

// 组件挂载时获取资源详情
onMounted(() => {
  fetchResourceDetail()
})

// 监听资源变化，获取相关资源
watchEffect(() => {
  if (resource.value.course) {
    fetchRelatedResources()
  }
})
</script>

<style lang="scss" scoped>
.student-resource-detail {
  padding: 20px;
}

.page-header {
  margin-bottom: 30px;
  display: flex;
  align-items: center;
  gap: 20px;

  h1 {
    margin: 0;
    font-size: 28px;
    font-weight: 600;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
}

.resource-detail-card {
  border-radius: 12px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
}

.card-header {
  font-weight: 600;
  font-size: 16px;
}

.resource-detail-content {
  padding: 20px 0;
}

.resource-main-info {
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #f0f0f0;

  .resource-title {
    margin: 0 0 15px 0;
    font-size: 24px;
    font-weight: 600;
    line-height: 1.4;
  }

  .resource-meta {
    display: flex;
    gap: 10px;
  }
}

.resource-info-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 30px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 8px;

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
}

.resource-description {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #f0f0f0;

  .info-label {
    font-size: 14px;
    color: #909399;
    font-weight: 500;
    margin-bottom: 15px;
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
}

.resource-actions {
  display: flex;
  gap: 15px;
  margin-top: 20px;
  justify-content: flex-start;
}

.related-resources-card {
  border-radius: 12px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
}

.related-resources {
  margin-top: 20px;
}

.related-item {
  height: 100%;
  border-radius: 8px;
  transition: all 0.3s ease;
  cursor: pointer;

  &:hover {
    transform: translateY(-3px);
    box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.1);
  }
}

.related-name {
  margin: 0 0 10px 0;
  font-size: 14px;
  font-weight: 600;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.related-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: #666;

  .related-uploader {
    color: #409EFF;
  }
}
</style>