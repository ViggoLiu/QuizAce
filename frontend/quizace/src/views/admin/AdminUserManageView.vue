<template>
  <div class="admin-user-manage-view">
    <div class="page-header">
      <div>
        <h1>👤 用户管理</h1>
        <p>管理员可在此维护学生与教师账号，执行增删改查操作</p>
      </div>
      <el-tag type="info">仅管理员可访问</el-tag>
    </div>

    <el-card class="toolbar-card" shadow="hover">
      <div class="toolbar">
        <el-radio-group v-model="activeRole" size="large">
          <el-radio-button label="student">学生账号</el-radio-button>
          <el-radio-button label="teacher">教师账号</el-radio-button>
          <el-radio-button label="admin">管理员账号</el-radio-button>
        </el-radio-group>
        <div class="toolbar-actions">
          <el-input
            v-model="keyword"
            placeholder="搜索用户名"
            clearable
            @clear="fetchUsers"
            @keyup.enter="fetchUsers"
            class="search-input"
            prefix-icon="el-icon-search"
          >
            <template #append>
              <el-button icon="el-icon-search" @click="fetchUsers" />
            </template>
          </el-input>
          <el-button type="primary" @click="openCreateDialog">
            新增{{ roleLabel }}账号
          </el-button>
        </div>
      </div>
    </el-card>

    <el-card shadow="hover" class="table-card">
      <el-table :data="users" v-loading="tableLoading" border stripe>
        <el-table-column type="index" label="#" width="60" />
        <el-table-column prop="username" label="用户名" min-width="120" />
        <el-table-column prop="email" label="邮箱" min-width="180" />
        <el-table-column prop="phone" label="手机号" min-width="130" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 0 ? 'success' : 'danger'">
              {{ row.status === 0 ? '正常' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column v-if="activeRole === 'student'" label="学院" min-width="140">
          <template #default="{ row }">
            {{ row.student_profile?.college || '—' }}
          </template>
        </el-table-column>
        <el-table-column v-if="activeRole === 'student'" label="专业" min-width="140">
          <template #default="{ row }">
            {{ row.student_profile?.major || '—' }}
          </template>
        </el-table-column>
        <el-table-column v-if="activeRole === 'teacher'" label="学院" min-width="140">
          <template #default="{ row }">
            {{ row.teacher_profile?.college || '—' }}
          </template>
        </el-table-column>
        <el-table-column v-if="activeRole === 'teacher'" label="职称" min-width="120">
          <template #default="{ row }">
            {{ row.teacher_profile?.title || '—' }}
          </template>
        </el-table-column>
        <el-table-column label="创建时间" min-width="170">
          <template #default="{ row }">
            {{ formatDate(row.create_time) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180">
          <template #default="{ row }">
            <el-button size="small" @click="openEditDialog(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!tableLoading && users.length === 0" description="暂无数据" />
    </el-card>

    <el-dialog
      v-model="dialogVisible"
      :title="dialogMode === 'create' ? `新增${roleLabel}账号` : `编辑${currentRoleLabel}账号`"
      width="560px"
      @close="handleDialogClose"
    >
      <el-form ref="userFormRef" :model="userForm" :rules="formRules" label-width="96px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="userForm.username" :disabled="dialogMode === 'edit'" maxlength="50" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="userForm.password" show-password placeholder="不修改请留空" maxlength="50" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="userForm.email" maxlength="100" />
        </el-form-item>
        <el-form-item label="手机号">
          <el-input v-model="userForm.phone" maxlength="20" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="userForm.status">
            <el-option label="正常" :value="0" />
            <el-option label="禁用" :value="1" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="userForm.remark" type="textarea" :rows="2" maxlength="255" />
        </el-form-item>

        <template v-if="currentFormRole !== 'admin'">
          <el-divider content-position="left">{{ currentFormRole === 'student' ? '学生信息' : '教师信息' }}</el-divider>

          <template v-if="currentFormRole === 'student'">
            <el-form-item label="学号">
              <el-input v-model="userForm.student_profile.student_no" maxlength="50" />
            </el-form-item>
            <el-form-item label="学院">
              <el-input v-model="userForm.student_profile.college" maxlength="100" />
            </el-form-item>
            <el-form-item label="专业">
              <el-input v-model="userForm.student_profile.major" maxlength="100" />
            </el-form-item>
            <el-form-item label="年级">
              <el-input v-model="userForm.student_profile.grade" maxlength="20" />
            </el-form-item>
          </template>

          <template v-else-if="currentFormRole === 'teacher'">
            <el-form-item label="工号">
              <el-input v-model="userForm.teacher_profile.teacher_no" maxlength="50" />
            </el-form-item>
            <el-form-item label="学院">
              <el-input v-model="userForm.teacher_profile.college" maxlength="100" />
            </el-form-item>
            <el-form-item label="职称">
              <el-input v-model="userForm.teacher_profile.title" maxlength="50" />
            </el-form-item>
            <el-form-item label="研究方向">
              <el-input v-model="userForm.teacher_profile.research_area" maxlength="200" />
            </el-form-item>
          </template>
        </template>
        <template v-else>
          <el-alert
            title="管理员账号无需填写学院/个人档案信息"
            type="info"
            show-icon
            class="admin-info-tip"
          />
        </template>
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitUserForm">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { get, post, put, del } from '@/util/request.js'

const activeRole = ref('student')
const keyword = ref('')
const users = ref([])
const tableLoading = ref(false)

const dialogVisible = ref(false)
const dialogMode = ref('create')
const userFormRef = ref(null)

const userForm = ref(getEmptyForm('student'))

const roleNameMap = {
  student: '学生',
  teacher: '教师',
  admin: '管理员'
}

const roleLabel = computed(() => roleNameMap[activeRole.value] || '用户')
const currentFormRole = computed(() => userForm.value.role || activeRole.value)
const currentRoleLabel = computed(() => roleNameMap[currentFormRole.value] || '用户')

function validatePassword(value, callback) {
  if (dialogMode.value === 'create' && !value) {
    callback(new Error('请输入密码'))
  } else {
    callback()
  }
}

const formRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '邮箱格式不正确', trigger: ['blur', 'change'] }
  ],
  password: [{ validator: (rule, value, callback) => validatePassword(value, callback), trigger: 'blur' }]
}

function getEmptyForm(role) {
  return {
    id: null,
    username: '',
    password: '',
    role,
    email: '',
    phone: '',
    status: 0,
    remark: '',
    student_profile: {
      student_no: '',
      college: '',
      major: '',
      grade: ''
    },
    teacher_profile: {
      teacher_no: '',
      college: '',
      title: '',
      research_area: ''
    }
  }
}

const formatDate = (value) => {
  if (!value) return '—'
  return new Date(value).toLocaleString('zh-CN')
}

const fetchUsers = async () => {
  tableLoading.value = true
  try {
    const response = await get('/user/admin/users/', {
      role: activeRole.value,
      keyword: keyword.value
    })
    if (response.data.code === 200) {
      users.value = response.data.data || []
    } else {
      ElMessage.error(response.data.info || '获取用户列表失败')
    }
  } catch (error) {
    console.error('获取用户失败: ', error)
    ElMessage.error('获取用户列表失败，请稍后重试')
  } finally {
    tableLoading.value = false
  }
}

const openCreateDialog = () => {
  dialogMode.value = 'create'
  userForm.value = getEmptyForm(activeRole.value)
  dialogVisible.value = true
  nextTick(() => {
    userFormRef.value?.clearValidate()
  })
}

const openEditDialog = (row) => {
  dialogMode.value = 'edit'
  userForm.value = {
    id: row.id,
    username: row.username || '',
    password: '',
    role: row.role,
    email: row.email || '',
    phone: row.phone || '',
    status: row.status ?? 0,
    remark: row.remark || '',
    student_profile: {
      student_no: row.student_profile?.student_no || '',
      college: row.student_profile?.college || '',
      major: row.student_profile?.major || '',
      grade: row.student_profile?.grade || ''
    },
    teacher_profile: {
      teacher_no: row.teacher_profile?.teacher_no || '',
      college: row.teacher_profile?.college || '',
      title: row.teacher_profile?.title || '',
      research_area: row.teacher_profile?.research_area || ''
    }
  }
  dialogVisible.value = true
  nextTick(() => {
    userFormRef.value?.clearValidate()
  })
}

const submitUserForm = async () => {
  if (!userFormRef.value) return
  try {
    await userFormRef.value.validate()
  } catch (error) {
    return
  }

  const payload = {
    role: currentFormRole.value,
    email: userForm.value.email,
    phone: userForm.value.phone,
    status: userForm.value.status,
    remark: userForm.value.remark
  }

  if (dialogMode.value === 'create') {
    payload.username = userForm.value.username
  }

  if (userForm.value.password) {
    payload.password = userForm.value.password
  }

  if (currentFormRole.value === 'student') {
    payload.student_profile = { ...userForm.value.student_profile }
  } else if (currentFormRole.value === 'teacher') {
    payload.teacher_profile = { ...userForm.value.teacher_profile }
  }

  try {
    if (dialogMode.value === 'create') {
      const response = await post('/user/admin/users/', payload)
      if (response.data.code === 200) {
        ElMessage.success('创建成功')
        dialogVisible.value = false
        fetchUsers()
      } else {
        ElMessage.error(response.data.info || '创建失败')
      }
    } else {
      const response = await put(`/user/admin/users/${userForm.value.id}/`, payload)
      if (response.data.code === 200) {
        ElMessage.success('更新成功')
        dialogVisible.value = false
        fetchUsers()
      } else {
        ElMessage.error(response.data.info || '更新失败')
      }
    }
  } catch (error) {
    console.error('提交用户失败: ', error)
    ElMessage.error('操作失败，请稍后重试')
  }
}

const handleDelete = (row) => {
  ElMessageBox.confirm(`确定删除用户【${row.username}】吗？`, '提示', {
    confirmButtonText: '删除',
    cancelButtonText: '取消',
    type: 'warning'
  })
    .then(async () => {
      try {
        const response = await del(`/user/admin/users/${row.id}/`)
        if (response.data.code === 200) {
          ElMessage.success('删除成功')
          fetchUsers()
        } else {
          ElMessage.error(response.data.info || '删除失败')
        }
      } catch (error) {
        console.error('删除用户失败: ', error)
        ElMessage.error('删除失败，请稍后重试')
      }
    })
    .catch(() => {})
}

const handleDialogClose = () => {
  userFormRef.value?.clearValidate()
}

onMounted(fetchUsers)

watch(activeRole, () => {
  keyword.value = ''
  fetchUsers()
})
</script>

<style lang="scss" scoped>
.admin-user-manage-view {
  padding: 20px;
  background: #f5f7fb;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;

  h1 {
    margin: 0;
    font-size: 28px;
    color: #1f2d3d;
  }

  p {
    margin: 6px 0 0;
    color: #606266;
  }
}

.toolbar-card {
  margin-bottom: 20px;
}

.toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  justify-content: space-between;
  align-items: center;
}

.toolbar-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.search-input {
  width: 240px;
  :deep(.el-input__inner) {
    border-width: 2px;
    border-color: #a0c4ff;
    box-shadow: inset 0 0 0 1px rgba(76, 115, 255, 0.2);
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
  }

  :deep(.el-input__inner:hover),
  :deep(.el-input__inner:focus) {
    border-color: #4c73ff;
    box-shadow: 0 0 0 3px rgba(76, 115, 255, 0.15);
  }
}

.table-card {
  border-radius: 12px;
}

.admin-info-tip {
  margin-top: 12px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

@media (max-width: 768px) {
  .toolbar {
    flex-direction: column;
    align-items: flex-start;
  }

  .toolbar-actions {
    width: 100%;
    flex-direction: column;
    align-items: stretch;
  }

  .search-input {
    width: 100%;
  }
}
</style>
