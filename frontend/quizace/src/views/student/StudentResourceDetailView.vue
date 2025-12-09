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

    <!-- 评论和打分区域 -->
    <el-card class="comments-card" shadow="hover" style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>评论和打分</span>
        </div>
      </template>
      
      <!-- 评分和评论表单 -->
      <div class="comment-form-section">
        <div class="rating-section">
          <h3>总体评分</h3>
          <el-rate
            v-model="ratingForm.rating"
            :max="5"
            allow-half
            show-score
            score-template="{value} 分"
            style="margin-bottom: 20px;"
          ></el-rate>
        </div>
        
        <el-form label-position="top" class="comment-form">
          <el-form-item label="写下你的评论">
            <el-input
              type="textarea"
              v-model="commentForm.content"
              :rows="4"
              placeholder="分享你对这个资源的看法..."
            ></el-input>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="submitComment" :loading="submitting">提交评论</el-button>
          </el-form-item>
        </el-form>
      </div>
      
      <!-- 评论列表 -->
      <div class="comments-list">
        <div class="comments-header">
          <h3>用户评论</h3>
          <div class="filter-controls">
            <el-select v-model="filter.rating" placeholder="按星级筛选" style="width: 120px; margin-right: 10px;">
              <el-option label="全部" value="null" />
              <el-option label="5星" value="5" />
              <el-option label="4星" value="4" />
              <el-option label="3星" value="3" />
              <el-option label="2星" value="2" />
              <el-option label="1星" value="1" />
            </el-select>
            <el-select v-model="filter.sortBy" placeholder="排序方式" style="width: 120px;">
              <el-option label="默认排序" value="default" />
              <el-option label="点赞热度" value="like_count" />
            </el-select>
          </div>
        </div>
        <div v-if="comments.length === 0" class="no-comments">
          <el-empty description="暂无评论，快来发表第一条评论吧！" />
        </div>
        <div v-else>
          <el-card
            v-for="comment in comments"
            :key="comment.id"
            shadow="hover"
            class="comment-item"
          >
            <div class="comment-header">
              <div class="user-info">
                <el-avatar :src="getAvatarUrl(comment.user.avatar)" :size="40" />
                <div class="user-details">
                  <div class="username">{{ comment.user.username }}</div>
                  <div class="role">{{ comment.user.role === 'student' ? '学生' : comment.user.role === 'teacher' ? '老师' : '管理员' }}</div>
                </div>
              </div>
              <div class="comment-time">
                <el-rate
                  v-model="comment.rating"
                  :max="5"
                  disabled
                  show-score
                  score-template="{value} 分"
                ></el-rate>
                <div class="time">{{ formatDate(comment.create_time) }}</div>
              </div>
            </div>
            <div class="comment-content">{{ comment.content }}</div>
            <div class="comment-actions">
              <el-button
                type="text"
                @click="toggleLike(comment)"
                :icon="comment.is_liked ? 'el-icon-thumb' : 'el-icon-thumb'"
                :class="comment.is_liked ? 'liked' : ''"
              >
                {{ comment.is_liked ? '已点赞' : '点赞' }} ({{ comment.like_count || 0 }})
              </el-button>
            </div>
          </el-card>
        </div>
      </div>
    </el-card>

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
import { get, post, del, getMediaBaseUrl } from '@/util/request.js'

const router = useRouter()
const route = useRoute()
const mediaBaseUrl = getMediaBaseUrl()

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

// 评论相关数据
const comments = ref([])
const commentForm = ref({
  content: ''
})
const ratingForm = ref({
  rating: 0
})
const submitting = ref(false)

// 筛选相关数据
const filter = ref({
  rating: null, // 按星级筛选，null表示不筛选
  sortBy: 'default' // 排序方式：default(默认)，like_count(按点赞数排序)
})

// 所有评论（用于筛选）
const allComments = ref([])

// 格式化日期
const formatDate = (dateString) => {
  const date = new Date(dateString)
  const options = { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' }
  return date.toLocaleDateString('zh-CN', options)
}

// 处理用户头像URL
const getAvatarUrl = (avatar) => {
  if (!avatar) {
    return 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'
  }
  // 如果头像URL已经是完整的URL，直接返回
  if (avatar.startsWith('http://') || avatar.startsWith('https://')) {
    return avatar
  }
  // 如果是相对路径，拼接完整的URL
  return avatar.startsWith('/') ? `${mediaBaseUrl}${avatar}` : `${mediaBaseUrl}/${avatar}`
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

const trackResourceView = async () => {
  try {
    const response = await post(`/learning_resource/view/${resource.value.id}/`)
    if (response.data.code === 200) {
      resource.value.click_count = response.data.data.click_count
    }
  } catch (error) {
    console.error('记录资源浏览失败:', error)
  }
}

// 查看资源
const viewResource = () => {
  trackResourceView()
  if (!resource.value.file_url) {
    ElMessage.warning('暂无资源文件可查看')
    return
  }
  ElMessage.info(`查看资源: ${resource.value.name}`)
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

// 加载评论列表
const loadComments = async () => {
  try {
    const response = await get(`/forum/resources/${resourceId.value}/comments/`)
    allComments.value = response.data.results || response.data
    // 应用筛选和排序
    applyFilter()
  } catch (error) {
    console.error('加载评论失败:', error)
  }
}

// 应用筛选和排序
const applyFilter = () => {
  let filteredComments = [...allComments.value]
  
  // 按星级筛选
  if (filter.value.rating && filter.value.rating !== 'null') {
    const rating = parseInt(filter.value.rating)
    filteredComments = filteredComments.filter(comment => Math.round(comment.rating) === rating)
  }
  
  // 按点赞热度排序
  if (filter.value.sortBy === 'like_count') {
    filteredComments.sort((a, b) => (b.like_count || 0) - (a.like_count || 0))
  }
  
  comments.value = filteredComments
}

// 监听筛选条件变化，重新应用筛选
watchEffect(() => {
  if (allComments.value.length > 0) {
    applyFilter()
  }
})

// 点赞功能
const toggleLike = async (comment) => {
  try {
    const response = await post(`/forum/resources/${resourceId.value}/comments/${comment.id}/like/`)
    comment.is_liked = !comment.is_liked
    comment.like_count = response.data.like_count
  } catch (error) {
    console.error('点赞失败:', error)
    ElMessage.error('点赞失败，请稍后重试')
  }
}

// 提交评论和打分
const submitComment = async () => {
  if (!commentForm.value.content.trim()) {
    ElMessage.warning('评论内容不能为空')
    return
  }

  if (ratingForm.value.rating === 0) {
    ElMessage.warning('请先评分')
    return
  }

  submitting.value = true
  try {
    const response = await post(`/forum/resources/${resourceId.value}/comments/`, {
      content: commentForm.value.content,
      rating: ratingForm.value.rating
    })
    comments.value.unshift(response.data)
    commentForm.value.content = ''
    ratingForm.value.rating = 0
    ElMessage.success('评论提交成功')
  } catch (error) {
    console.error('提交评论失败:', error)
    ElMessage.error('提交评论失败，请稍后重试')
  } finally {
    submitting.value = false
  }
}

// 监听资源变化，获取相关资源和评论
watchEffect(() => {
  if (resource.value.course) {
    fetchRelatedResources()
  }
  if (resourceId.value) {
    loadComments()
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

/* 评论区域样式 */
.comments-card {
  border-radius: 12px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
}

.comment-form-section {
  padding: 20px 0;
  border-bottom: 1px solid #f0f0f0;
}

.rating-section h3 {
  margin: 0 0 15px 0;
  font-size: 16px;
  font-weight: 600;
}

.comment-form {
  margin-top: 20px;
}

.comments-list {
  margin-top: 20px;
}

.comments-list h3 {
  margin: 0 0 20px 0;
  font-size: 16px;
  font-weight: 600;
}

.no-comments {
  text-align: center;
  padding: 50px 0;
}

.comment-item {
  margin-bottom: 15px;
  border-radius: 8px;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15px;
}

.user-info {
  display: flex;
  align-items: center;
}

.user-details {
  margin-left: 15px;
}

.username {
  font-weight: bold;
  margin-bottom: 5px;
}

.role {
  font-size: 12px;
  color: #1884f2;
}

.comment-time {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 10px;
}

.comment-time .time {
  font-size: 12px;
  color: #909090;
}

.comment-content {
  line-height: 1.6;
  color: #303133;
  margin-bottom: 10px;
}

.comment-actions {
  display: flex;
  gap: 15px;
  padding-top: 10px;
  border-top: 1px solid #f0f0f0;
}

.liked {
  color: #f56c6c;
}

/* 评论筛选控件样式 */
.comments-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.filter-controls {
  display: flex;
  gap: 10px;
}

/* 调整评论列表标题样式 */
.comments-list h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

</style>