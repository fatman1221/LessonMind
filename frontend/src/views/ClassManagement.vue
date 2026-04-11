<template>
  <div class="class-management-container">
    <el-card class="management-card">
      <template #header>
        <div class="card-header">
          <span>班级管理</span>
          <el-button type="primary" @click="handleCreate">
            <el-icon><Plus /></el-icon>
            新建班级
          </el-button>
        </div>
      </template>

      <!-- 班级列表 -->
      <el-table :data="classList" v-loading="loading" style="width: 100%">
        <el-table-column prop="name" label="班级名称" min-width="150" />
        <el-table-column prop="subject" label="学科" width="100" />
        <el-table-column prop="grade" label="学段" width="100" />
        <el-table-column prop="student_count" label="学生数" width="100" />
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="300" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="viewClass(row)">查看</el-button>
            <el-button link type="primary" @click="manageStudents(row)">管理学生</el-button>
            <el-button link type="primary" @click="editClass(row)">编辑</el-button>
            <el-button link type="danger" @click="deleteClass(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 创建/编辑班级对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="editingClass ? '编辑班级' : '新建班级'"
      width="500px"
    >
      <el-form :model="formData" :rules="formRules" ref="formRef" label-width="100px">
        <el-form-item label="班级名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入班级名称" />
        </el-form-item>
        <el-form-item label="学科">
          <el-select v-model="formData.subject" placeholder="请选择学科" style="width: 100%" clearable>
            <el-option label="数学" value="数学" />
            <el-option label="语文" value="语文" />
            <el-option label="英语" value="英语" />
            <el-option label="物理" value="物理" />
            <el-option label="化学" value="化学" />
            <el-option label="生物" value="生物" />
            <el-option label="历史" value="历史" />
            <el-option label="地理" value="地理" />
          </el-select>
        </el-form-item>
        <el-form-item label="学段">
          <el-select v-model="formData.grade" placeholder="请选择学段" style="width: 100%" clearable>
            <el-option label="小学" value="小学" />
            <el-option label="初中" value="初中" />
            <el-option label="高中" value="高中" />
          </el-select>
        </el-form-item>
        <el-form-item label="班级描述">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="3"
            placeholder="请输入班级描述"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">保存</el-button>
      </template>
    </el-dialog>

    <!-- 管理学生对话框 -->
    <el-dialog
      v-model="studentDialogVisible"
      title="管理学生"
      width="700px"
    >
      <div v-if="currentClass">
        <div class="student-management-header">
          <span>班级：{{ currentClass.name }}</span>
          <el-button type="primary" @click="handleAddStudent">
            <el-icon><Plus /></el-icon>
            添加学生
          </el-button>
        </div>
        <el-table :data="studentList" style="width: 100%; margin-top: 20px">
          <el-table-column prop="username" label="用户名" />
          <el-table-column prop="email" label="邮箱" />
          <el-table-column prop="joined_at" label="加入时间" width="180">
            <template #default="{ row }">
              {{ formatTime(row.joined_at) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100">
            <template #default="{ row }">
              <el-button link type="danger" @click="removeStudent(row.id)">移除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
      <template #footer>
        <el-button @click="studentDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 班级详情 -->
    <el-dialog v-model="classDetailVisible" title="班级详情" width="520px">
      <template v-if="classDetail">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="班级名称">{{ classDetail.name }}</el-descriptions-item>
          <el-descriptions-item label="学科">{{ classDetail.subject || '—' }}</el-descriptions-item>
          <el-descriptions-item label="学段">{{ classDetail.grade || '—' }}</el-descriptions-item>
          <el-descriptions-item label="学生人数">{{ classDetail.student_count ?? 0 }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatTime(classDetail.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="描述">{{ classDetail.description || '—' }}</el-descriptions-item>
        </el-descriptions>
      </template>
      <template #footer>
        <el-button type="primary" @click="classDetailVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 添加学生对话框 -->
    <el-dialog
      v-model="showAddStudentDialog"
      title="添加学生"
      width="500px"
    >
      <el-select
        v-model="selectedStudents"
        multiple
        filterable
        placeholder="搜索并选择学生"
        style="width: 100%"
        :loading="loadingStudents"
      >
        <el-option
          v-for="student in filteredAvailableStudents"
          :key="student.id"
          :label="`${student.username} (${student.email})`"
          :value="student.id"
          :disabled="!student.is_active"
        />
      </el-select>
      <div v-if="filteredAvailableStudents.length === 0" style="margin-top: 10px; color: #909399; font-size: 12px;">
        没有可添加的学生（所有学生都已加入此班级或没有活跃的学生账号）
      </div>
      <template #footer>
        <el-button @click="showAddStudentDialog = false">取消</el-button>
        <el-button type="primary" @click="addStudents" :loading="addingStudents">添加</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import * as classApi from '@/api/class'

const loading = ref(false)
const submitting = ref(false)
const addingStudents = ref(false)
const loadingStudents = ref(false)
const classList = ref([])
const dialogVisible = ref(false)
const studentDialogVisible = ref(false)
const showAddStudentDialog = ref(false)
const editingClass = ref(null)
const currentClass = ref(null)
const studentList = ref([])
const availableStudents = ref([])
const selectedStudents = ref([])
const formRef = ref(null)
const classDetailVisible = ref(false)
const classDetail = ref(null)

const formData = reactive({
  name: '',
  description: '',
  subject: '',
  grade: ''
})

const formRules = {
  name: [{ required: true, message: '请输入班级名称', trigger: 'blur' }]
}

onMounted(() => {
  loadClasses()
  loadAvailableStudents()
})

const loadClasses = async () => {
  loading.value = true
  try {
    classList.value = await classApi.getClasses()
  } catch (error) {
    ElMessage.error('加载班级列表失败：' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

const loadAvailableStudents = async () => {
  loadingStudents.value = true
  try {
    availableStudents.value = await classApi.getAvailableStudents()
  } catch (error) {
    console.error('加载学生列表失败:', error)
    ElMessage.error('加载学生列表失败：' + (error.response?.data?.detail || error.message))
  } finally {
    loadingStudents.value = false
  }
}

// 过滤可用学生：排除已在班级中的学生
const filteredAvailableStudents = computed(() => {
  if (!currentClass.value) return availableStudents.value
  
  const classStudentIds = studentList.value.map(s => s.id)
  return availableStudents.value.filter(student => 
    !classStudentIds.includes(student.id) && student.is_active
  )
})

const handleCreate = () => {
  editingClass.value = null
  formData.name = ''
  formData.description = ''
  formData.subject = ''
  formData.grade = ''
  dialogVisible.value = true
}

const editClass = (cls) => {
  editingClass.value = cls
  formData.name = cls.name
  formData.description = cls.description || ''
  formData.subject = cls.subject || ''
  formData.grade = cls.grade || ''
  dialogVisible.value = true
}

const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        if (editingClass.value) {
          await classApi.updateClass(editingClass.value.id, formData)
          ElMessage.success('更新成功')
        } else {
          await classApi.createClass(formData)
          ElMessage.success('创建成功')
        }
        dialogVisible.value = false
        loadClasses()
      } catch (error) {
        ElMessage.error('保存失败：' + (error.response?.data?.detail || error.message))
      } finally {
        submitting.value = false
      }
    }
  })
}

const deleteClass = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除这个班级吗？删除后相关作业也会被删除！', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await classApi.deleteClass(id)
    ElMessage.success('删除成功')
    loadClasses()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败：' + (error.response?.data?.detail || error.message))
    }
  }
}

const viewClass = async (cls) => {
  try {
    classDetail.value = await classApi.getClass(cls.id)
    classDetailVisible.value = true
  } catch (error) {
    ElMessage.error('加载班级详情失败：' + (error.response?.data?.detail || error.message))
  }
}

const handleAddStudent = () => {
  selectedStudents.value = []
  showAddStudentDialog.value = true
}

const manageStudents = async (cls) => {
  currentClass.value = cls
  try {
    studentList.value = await classApi.getClassStudents(cls.id)
    studentDialogVisible.value = true
    // 重新加载可用学生列表，排除已在班级中的学生
    await loadAvailableStudents()
  } catch (error) {
    ElMessage.error('加载学生列表失败：' + (error.response?.data?.detail || error.message))
  }
}

const addStudents = async () => {
  if (selectedStudents.value.length === 0) {
    ElMessage.warning('请选择要添加的学生')
    return
  }
  
  addingStudents.value = true
  try {
    await classApi.addStudents(currentClass.value.id, selectedStudents.value)
    ElMessage.success('添加成功')
    showAddStudentDialog.value = false
    selectedStudents.value = []
    // 重新加载学生列表
    studentList.value = await classApi.getClassStudents(currentClass.value.id)
    await loadAvailableStudents()
    loadClasses()
  } catch (error) {
    ElMessage.error('添加失败：' + (error.response?.data?.detail || error.message))
  } finally {
    addingStudents.value = false
  }
}

const removeStudent = async (studentId) => {
  try {
    await ElMessageBox.confirm('确定要移除这名学生吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await classApi.removeStudent(currentClass.value.id, studentId)
    ElMessage.success('移除成功')
    studentList.value = await classApi.getClassStudents(currentClass.value.id)
    await loadAvailableStudents()
    loadClasses()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('移除失败：' + (error.response?.data?.detail || error.message))
    }
  }
}

const formatTime = (time) => {
  if (!time) return ''
  const date = new Date(time)
  return date.toLocaleString('zh-CN')
}
</script>

<style scoped>
.class-management-container {
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

.student-management-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
}
</style>

