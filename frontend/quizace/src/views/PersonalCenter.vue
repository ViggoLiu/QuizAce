<template>
  <div class="personal-center">
    <h2>个人中心</h2>
    <div class="personal-info-container">
      <!-- 头像上传部分 -->
      <div class="avatar-section">
        <div class="avatar-container">
          <img :src="userInfo.avatar || defaultAvatar" alt="用户头像" class="avatar">
          <label class="avatar-upload-btn">
            <input type="file" ref="fileInput" accept="image/*" @change="handleAvatarUpload" hidden>
            <span>更换头像</span>
          </label>
        </div>
      </div>

      <!-- 用户信息表单 -->
      <div class="form-section">
        <form @submit.prevent="handleSubmit">
          <!-- 基础信息 -->
          <div class="form-group">
            <label for="username">用户名</label>
            <input type="text" id="username" v-model="userInfo.username" disabled>
          </div>

          <div class="form-group">
            <label for="email">邮箱</label>
            <input type="email" id="email" v-model="userInfo.email" placeholder="请输入邮箱">
          </div>

          <div class="form-group">
            <label for="phone">手机号</label>
            <input type="tel" id="phone" v-model="userInfo.phone" placeholder="请输入手机号">
          </div>

          <div class="form-group">
            <label for="remark">简要描述</label>
            <textarea id="remark" v-model="userInfo.remark" placeholder="请输入简要描述"></textarea>
          </div>

          <!-- 学生特有信息 -->
          <div v-if="userInfo.role === 'student'" class="role-specific-info">
            <h3>学生信息</h3>
            <div class="form-group">
              <label for="student_no">学号</label>
              <input type="text" id="student_no" v-model="studentProfile.student_no" placeholder="请输入学号">
            </div>
            <div class="form-group">
              <label for="college">所属学院</label>
              <input type="text" id="college" v-model="studentProfile.college" placeholder="请输入所属学院">
            </div>
            <div class="form-group">
              <label for="major">所属专业</label>
              <input type="text" id="major" v-model="studentProfile.major" placeholder="请输入所属专业">
            </div>
            <div class="form-group">
              <label for="grade">年级</label>
              <input type="text" id="grade" v-model="studentProfile.grade" placeholder="请输入年级">
            </div>
          </div>

          <!-- 教师特有信息 -->
          <div v-if="userInfo.role === 'teacher'" class="role-specific-info">
            <h3>教师信息</h3>
            <div class="form-group">
              <label for="teacher_no">工号</label>
              <input type="text" id="teacher_no" v-model="teacherProfile.teacher_no" placeholder="请输入工号">
            </div>
            <div class="form-group">
              <label for="teacher_college">所属学院</label>
              <input type="text" id="teacher_college" v-model="teacherProfile.college" placeholder="请输入所属学院">
            </div>
            <div class="form-group">
              <label for="title">职称</label>
              <input type="text" id="title" v-model="teacherProfile.title" placeholder="请输入职称">
            </div>
            <div class="form-group">
              <label for="research_area">研究方向</label>
              <input type="text" id="research_area" v-model="teacherProfile.research_area" placeholder="请输入研究方向">
            </div>
          </div>

          <div class="form-actions">
            <button type="submit" class="save-btn">保存修改</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
// 导入请求工具
import request, { getMediaBaseUrl } from '@/util/request.js'

export default {
  name: 'PersonalCenter',
  data() {
    return {
      userInfo: {
        id: '',
        username: '',
        role: '',
        avatar: '',
        email: '',
        phone: '',
        remark: ''
      },
      studentProfile: {
        student_no: '',
        college: '',
        major: '',
        grade: ''
      },
      teacherProfile: {
        teacher_no: '',
        college: '',
        title: '',
        research_area: ''
      },
      defaultAvatar: require('@/assets/logo.png'),
      loading: false
    }
  },
  mounted() {
    // 在组件挂载后获取用户信息
    this.fetchUserInfo()
  },
  methods: {
    // 获取用户信息
    async fetchUserInfo() {
      try {
        this.loading = true
        // 调用获取当前用户信息的API
        const response = await request.get('/user/info/')
        const userData = response.data.data
        
        // 设置基础用户信息
        // 处理头像URL，确保是完整的URL
        this.userInfo = {
          id: userData.id,
          username: userData.username,
          role: userData.role,
          avatar: this.resolveAvatarUrl(userData.avatar),
          email: userData.email,
          phone: userData.phone,
          remark: userData.remark
        }
        
        // 根据角色获取相应的用户信息
        if (this.userInfo.role === 'student' && userData.student_profile) {
          this.studentProfile = userData.student_profile
        } else if (this.userInfo.role === 'teacher' && userData.teacher_profile) {
          this.teacherProfile = userData.teacher_profile
        }
      } catch (error) {
        console.error('获取用户信息失败:', error)
        this.$message.error('获取用户信息失败，请稍后重试')
        // 使用模拟数据作为备选
        this.setMockData()
      } finally {
        this.loading = false
      }
    },
    
    // 设置模拟数据（当API调用失败时使用）
    setMockData() {
      this.userInfo = {
        id: '1',
        username: 'testuser',
        role: 'student', // 或者 'teacher'
        avatar: '',
        email: 'test@example.com',
        phone: '13800138000',
        remark: '这是一个测试用户'
      }
      
      if (this.userInfo.role === 'student') {
        this.studentProfile = {
          student_no: '2020001',
          college: '计算机学院',
          major: '软件工程',
          grade: '2020级'
        }
      } else if (this.userInfo.role === 'teacher') {
        this.teacherProfile = {
          teacher_no: 'T1001',
          college: '计算机学院',
          title: '副教授',
          research_area: '人工智能'
        }
      }
    },
    
    // 处理头像上传
    async handleAvatarUpload(event) {
      const file = event.target.files[0]
      if (file) {
        try {
          // 创建FormData对象
          const formData = new FormData()
          formData.append('avatar', file)
          
          // 调用头像上传API
          const response = await request.fileUpload('/user/upload/avatar/', formData)
          
          // 更新头像URL
          if (response.data && response.data.data && response.data.data.avatar) {
            // 确保头像URL是完整的，包含服务器地址
            const avatarUrl = response.data.data.avatar
            this.userInfo.avatar = this.resolveAvatarUrl(avatarUrl)
            this.$message.success('头像上传成功')
          }
        } catch (error) {
          console.error('头像上传失败:', error)
          this.$message.error('头像上传失败，请稍后重试')
          
          // 上传失败时仍然显示本地预览
          const reader = new FileReader()
          reader.onload = (e) => {
            this.userInfo.avatar = e.target.result
          }
          reader.readAsDataURL(file)
        }
        
        // 清空文件输入，以便可以重复上传同一文件
        this.$refs.fileInput.value = ''
      }
    },

    resolveAvatarUrl(path) {
      if (!path) {
        return ''
      }
      if (/^https?:/i.test(path)) {
        return path
      }
      const base = getMediaBaseUrl()
      return path.startsWith('/') ? `${base}${path}` : `${base}/${path}`
    },
    
    // 表单提交
    async handleSubmit() {
      // 表单验证
      if (!this.validateForm()) {
        return
      }
      
      try {
        this.loading = true
        
        // 准备提交数据
        const submitData = {
          email: this.userInfo.email,
          phone: this.userInfo.phone,
          remark: this.userInfo.remark
        }
        
        // 根据角色添加特定信息
        if (this.userInfo.role === 'student') {
          submitData.student_profile = this.studentProfile
        } else if (this.userInfo.role === 'teacher') {
          submitData.teacher_profile = this.teacherProfile
        }
        
        // 调用更新用户信息的API
        const response = await request.post(`/user/update/${this.userInfo.id}/`, submitData)
        
        if (response.status === 200 || response.status === 204) {
          this.$message({
            message: '保存成功',
            type: 'success'
          })
        }
      } catch (error) {
        console.error('保存用户信息失败:', error)
        this.$message.error('保存失败，请稍后重试')
      } finally {
        this.loading = false
      }
    },
    
    // 表单验证
    validateForm() {
      // 简单的验证逻辑
      if (!this.userInfo.email && !this.userInfo.phone) {
        this.$message.error('邮箱和手机号至少填写一项')
        return false
      }
      
      if (this.userInfo.phone && !/^1[3-9]\d{9}$/.test(this.userInfo.phone)) {
        this.$message.error('请输入正确的手机号格式')
        return false
      }
      
      if (this.userInfo.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(this.userInfo.email)) {
        this.$message.error('请输入正确的邮箱格式')
        return false
      }
      
      return true
    }
  }
}
</script>

<style scoped>
.personal-center {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  box-sizing: border-box;
}

 h2 {
  text-align: center;
  margin-bottom: 30px;
  color: #333;
  font-size: 24px;
}

.personal-info-container {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  padding: 30px;
  box-sizing: border-box;
  overflow: hidden;
}

.avatar-section {
  text-align: center;
  margin-bottom: 30px;
}

.avatar-container {
  position: relative;
  display: inline-block;
  margin-bottom: 20px;
}

.avatar {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid #eee;
  transition: transform 0.3s;
}

.avatar:hover {
  transform: scale(1.05);
}

.avatar-upload-btn {
  position: absolute;
  bottom: 0;
  right: 0;
  background: #409EFF;
  color: white;
  border-radius: 50%;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.3s;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.3);
}

.avatar-upload-btn:hover {
  background: #66b1ff;
  transform: scale(1.1);
  box-shadow: 0 3px 12px rgba(64, 158, 255, 0.5);
}

.form-section {
  margin-top: 20px;
}

.form-group {
  margin-bottom: 24px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  display: block;
  color: #606266;
  font-weight: 500;
  font-size: 14px;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  transition: all 0.3s;
  font-size: 14px;
  box-sizing: border-box;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #409EFF;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.1);
}

.form-group textarea {
  min-height: 100px;
  resize: vertical;
  line-height: 1.6;
}

.role-specific-info {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}

.role-specific-info h3 {
  margin-bottom: 20px;
  color: #303133;
  font-size: 18px;
}

.form-actions {
  text-align: center;
  margin-top: 40px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}

.save-btn {
  background: #409EFF;
  color: white;
  border: none;
  padding: 12px 32px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  transition: all 0.3s;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.3);
}

.save-btn:hover {
  background: #66b1ff;
  transform: translateY(-1px);
  box-shadow: 0 3px 12px rgba(64, 158, 255, 0.5);
}

.save-btn:active {
  transform: translateY(0);
}

.form-group input:disabled {
  background: #f5f7fa;
  cursor: not-allowed;
  color: #c0c4cc;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .personal-center {
    padding: 10px;
    max-width: 100%;
  }
  
  .personal-info-container {
    padding: 20px;
  }
  
  .avatar {
    width: 100px;
    height: 100px;
  }
  
  h2 {
    font-size: 20px;
  }
  
  .role-specific-info h3 {
    font-size: 16px;
  }
}
</style>