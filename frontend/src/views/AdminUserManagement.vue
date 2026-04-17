<template>
  <div class="admin-user-management-container">
    <el-card class="management-card">
      <template #header>
        <div class="card-header">
          <span>用户管理</span>
          <div>
            <el-button type="primary" @click="handleCreate">
              <el-icon><Plus /></el-icon>
              新建用户
            </el-button>
            <el-button @click="loadUsers">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </div>
      </template>

      <!-- 统计信息 -->
      <div class="stats-bar" v-if="stats">
        <el-statistic title="总用户数" :value="stats.total_users" />
        <el-statistic title="活跃用户" :value="stats.active_users" />
        <el-statistic title="教师" :value="stats.teacher_count" />
        <el-statistic title="学生" :value="stats.student_count || 0" />
        <el-statistic title="系统管理员" :value="stats.admin_count" />
      </div>

      <!-- 用户列表 -->
      <el-table
        :data="users"
        v-loading="loading"
        stripe
        style="width: 100%"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" width="150" />
        <el-table-column prop="email" label="邮箱" width="200" />
        <el-table-column prop="role" label="角色" width="100">
          <template #default="{ row }">
            <el-tag :type="getRoleTagType(row.role)">
              {{ getRoleName(row.role) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              link
              size="small"
              @click="handleEdit(row)"
            >
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-button
              type="danger"
              link
              size="small"
              @click="handleDelete(row)"
              :disabled="row.id === currentUserId"
            >
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 编辑/创建对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="editingUser ? '编辑用户' : '新建用户'"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="formData.username"
            placeholder="请输入用户名"
            :disabled="!!editingUser"
          />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input
            v-model="formData.email"
            type="email"
            placeholder="请输入邮箱"
          />
        </el-form-item>
        <el-form-item label="密码" prop="password" v-if="!editingUser">
          <el-input
            v-model="formData.password"
            type="password"
            placeholder="请输入密码"
            show-password
          />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="formData.role" placeholder="请选择角色" style="width: 100%">
            <el-option label="教师" value="teacher" />
            <el-option label="学生" value="student" />
            <el-option label="系统管理员" value="admin" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态" prop="is_active">
          <el-switch
            v-model="formData.is_active"
            active-text="启用"
            inactive-text="禁用"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          保存
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete, Refresh } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import * as adminApi from '@/api/admin'

const authStore = useAuthStore()
const loading = ref(false)
const users = ref([])
const stats = ref(null)
const dialogVisible = ref(false)
const editingUser = ref(null)
const submitting = ref(false)
const formRef = ref(null)

const currentUserId = computed(() => authStore.user?.id)

const formData = reactive({
  username: '',
  email: '',
  password: '',
  role: 'teacher',
  is_active: true
})

const formRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6位', trigger: 'blur' }
  ],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }]
}

onMounted(() => {
  loadUsers()
  loadStats()
})

const loadUsers = async () => {
  loading.value = true
  try {
    const data = await adminApi.getAllUsers()
    users.value = data
  } catch (error) {
    ElMessage.error('加载用户列表失败：' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

const loadStats = async () => {
  try {
    const data = await adminApi.getUserStats()
    stats.value = data
  } catch (error) {
    console.error('加载统计信息失败:', error)
  }
}

const handleCreate = () => {
  editingUser.value = null
  formData.username = ''
  formData.email = ''
  formData.password = ''
  formData.role = 'teacher'
  formData.is_active = true
  dialogVisible.value = true
}

const handleEdit = (user) => {
  editingUser.value = user
  formData.username = user.username
  formData.email = user.email
  formData.password = ''
  formData.role = user.role
  formData.is_active = user.is_active
  dialogVisible.value = true
}

const handleDelete = async (user) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除用户 "${user.username}" 吗？此操作不可恢复！`,
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    await adminApi.deleteUser(user.id)
    ElMessage.success('删除成功')
    loadUsers()
    loadStats()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败：' + (error.response?.data?.detail || error.message))
    }
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return

  // 编辑时不需要验证密码
  const rules = editingUser.value
    ? { ...formRules, password: [] }
    : formRules

  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        if (editingUser.value) {
          const updateData = {
            email: formData.email,
            role: formData.role,
            is_active: formData.is_active
          }
          // 如果提供了新密码，则更新密码
          if (formData.password) {
            // 注意：这里需要后端支持密码更新，当前API可能不支持
            // 可以先不更新密码，或者添加单独的密码更新接口
          }
          await adminApi.updateUser(editingUser.value.id, updateData)
          ElMessage.success('更新成功')
        } else {
          await adminApi.createUser({
            username: formData.username,
            email: formData.email,
            password: formData.password,
            role: formData.role,
            is_active: formData.is_active
          })
          ElMessage.success('创建成功')
        }
        dialogVisible.value = false
        loadUsers()
        loadStats()
      } catch (error) {
        ElMessage.error('保存失败：' + (error.response?.data?.detail || error.message))
      } finally {
        submitting.value = false
      }
    }
  })
}

const getRoleName = (role) => {
  const roleMap = {
    'admin': '系统管理员',
    'teacher': '教师',
    'student': '学生'
  }
  return roleMap[role] || role
}

const getRoleTagType = (role) => {
  const typeMap = {
    'admin': 'danger',
    'teacher': 'primary',
    'student': 'success'
  }
  return typeMap[role] || ''
}

const formatTime = (time) => {
  if (!time) return ''
  const date = new Date(time)
  return date.toLocaleString('zh-CN')
}
</script>

<style scoped>
.admin-user-management-container {
  height: 100%;
}

.management-card {
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stats-bar {
  display: flex;
  gap: 30px;
  margin-bottom: 20px;
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.stats-bar .el-statistic {
  flex: 1;
}
</style>
