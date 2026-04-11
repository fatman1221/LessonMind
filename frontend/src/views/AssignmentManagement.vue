<template>
  <div class="assignment-management-container">
    <el-card class="management-card">
      <template #header>
        <div class="card-header">
          <span>作业管理</span>
          <el-button type="primary" @click="handleCreate">
            <el-icon><Plus /></el-icon>
            发布作业
          </el-button>
        </div>
      </template>

      <!-- 筛选 -->
      <div class="filter-bar">
        <el-select
          v-model="filterClassId"
          placeholder="筛选班级"
          clearable
          style="width: 200px"
          @change="loadAssignments"
        >
          <el-option
            v-for="cls in classList"
            :key="cls.id"
            :label="cls.name"
            :value="cls.id"
          />
        </el-select>
      </div>

      <!-- 作业列表 -->
      <el-table :data="assignmentList" v-loading="loading" style="width: 100%">
        <el-table-column prop="title" label="作业标题" min-width="200" />
        <el-table-column prop="class_id" label="班级" width="150">
          <template #default="{ row }">
            {{ getClassName(row.class_id) }}
          </template>
        </el-table-column>
        <el-table-column prop="submission_count" label="提交数" width="100" />
        <el-table-column prop="deadline" label="截止时间" width="180">
          <template #default="{ row }">
            {{ row.deadline ? formatTime(row.deadline) : '无' }}
          </template>
        </el-table-column>
        <el-table-column prop="is_published" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_published ? 'success' : 'warning'">
              {{ row.is_published ? '已发布' : '未发布' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="viewAssignment(row)">查看</el-button>
            <el-button
              v-if="!row.is_published"
              link
              type="success"
              @click="publishAssignment(row.id)"
            >
              发布
            </el-button>
            <el-button link type="primary" @click="viewSubmissions(row)">查看提交</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 创建作业对话框 -->
    <el-dialog
      v-model="dialogVisible"
      title="发布作业"
      width="800px"
    >
      <el-form :model="formData" :rules="formRules" ref="formRef" label-width="100px">
        <el-form-item label="班级" prop="class_id">
          <el-select v-model="formData.class_id" placeholder="请选择班级" style="width: 100%">
            <el-option
              v-for="cls in classList"
              :key="cls.id"
              :label="cls.name"
              :value="cls.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="作业标题" prop="title">
          <el-input v-model="formData.title" placeholder="请输入作业标题" />
        </el-form-item>
        <el-form-item label="作业描述">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="3"
            placeholder="请输入作业描述"
          />
        </el-form-item>
        <el-form-item label="选择题目" prop="question_ids">
          <div class="question-selection">
            <el-button @click="showQuestionDialog = true">从题库选择</el-button>
            <div v-if="selectedQuestions.length > 0" class="selected-questions">
              <el-tag
                v-for="q in selectedQuestions"
                :key="q.id"
                closable
                @close="removeQuestion(q.id)"
                style="margin: 5px"
              >
                {{ q.question_content.substring(0, 30) }}...
              </el-tag>
            </div>
          </div>
        </el-form-item>
        <el-form-item label="截止时间">
          <el-date-picker
            v-model="formData.deadline"
            type="datetime"
            placeholder="选择截止时间"
            style="width: 100%"
            format="YYYY-MM-DD HH:mm"
            value-format="YYYY-MM-DDTHH:mm:ss"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">创建</el-button>
      </template>
    </el-dialog>

    <!-- 选择题目对话框 -->
    <el-dialog
      v-model="showQuestionDialog"
      title="选择题目"
      width="900px"
    >
      <div class="question-dialog">
        <el-table
          :data="questionList"
          @selection-change="handleQuestionSelection"
          style="width: 100%"
        >
          <el-table-column type="selection" width="55" />
          <el-table-column prop="subject" label="学科" width="100" />
          <el-table-column prop="knowledge_point" label="知识点" min-width="150" />
          <el-table-column prop="question_type" label="类型" width="100">
            <template #default="{ row }">
              <el-tag size="small">
                {{ getQuestionTypeName(row.question_type) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="question_content" label="题目" min-width="200" show-overflow-tooltip />
        </el-table>
      </div>
      <template #footer>
        <el-button @click="showQuestionDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmQuestionSelection">确定</el-button>
      </template>
    </el-dialog>

    <!-- 查看提交对话框 -->
    <el-dialog
      v-model="submissionDialogVisible"
      title="学生提交情况"
      width="900px"
    >
      <el-empty v-if="submissionList.length === 0" description="暂无学生提交" />
      <el-table v-else :data="submissionList" style="width: 100%">
        <el-table-column label="学生" min-width="140">
          <template #default="{ row }">
            {{ row.student_username || `学生 #${row.student_id}` }}
          </template>
        </el-table-column>
        <el-table-column prop="student_id" label="学生ID" width="90" />
        <el-table-column prop="score" label="得分" width="100">
          <template #default="{ row }">
            {{ row.score }} / {{ row.total_score }}
          </template>
        </el-table-column>
        <el-table-column prop="submitted_at" label="提交时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.submitted_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button link type="primary" @click="viewSubmissionDetail(row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>

    <!-- 作业详情 -->
    <el-dialog v-model="assignmentDetailVisible" title="作业详情" width="720px">
      <template v-if="assignmentDetail">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="标题">{{ assignmentDetail.title }}</el-descriptions-item>
          <el-descriptions-item label="班级">{{ getClassName(assignmentDetail.class_id) }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="assignmentDetail.is_published ? 'success' : 'warning'">
              {{ assignmentDetail.is_published ? '已发布' : '未发布' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="截止时间">
            {{ assignmentDetail.deadline ? formatTime(assignmentDetail.deadline) : '无' }}
          </el-descriptions-item>
          <el-descriptions-item label="描述">{{ assignmentDetail.description || '—' }}</el-descriptions-item>
        </el-descriptions>
        <h4 style="margin: 16px 0 8px">题目列表</h4>
        <el-table :data="assignmentDetailQuestions" size="small" max-height="360">
          <el-table-column prop="id" label="题号" width="70" />
          <el-table-column label="类型" width="100">
            <template #default="{ row }">
              {{ getQuestionTypeName(row.type) }}
            </template>
          </el-table-column>
          <el-table-column prop="question" label="题干" min-width="200" show-overflow-tooltip />
        </el-table>
      </template>
      <template #footer>
        <el-button type="primary" @click="assignmentDetailVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 单次提交详情 -->
    <el-dialog v-model="submissionDetailVisible" title="提交详情" width="640px">
      <template v-if="currentSubmission">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="学生">
            {{ currentSubmission.student_username || `学生 #${currentSubmission.student_id}` }}
          </el-descriptions-item>
          <el-descriptions-item label="得分">
            {{ currentSubmission.score }} / {{ currentSubmission.total_score }}
          </el-descriptions-item>
          <el-descriptions-item label="提交时间">
            {{ formatTime(currentSubmission.submitted_at) }}
          </el-descriptions-item>
        </el-descriptions>
        <el-table :data="submissionDetailRows" size="small" style="margin-top: 16px" max-height="400">
          <el-table-column prop="qid" label="题号" width="80" />
          <el-table-column prop="student_answer" label="学生答案" min-width="120" show-overflow-tooltip />
          <el-table-column prop="correct_answer" label="参考答案" min-width="120" show-overflow-tooltip />
          <el-table-column label="结果" width="90">
            <template #default="{ row }">
              <el-tag :type="row.is_correct ? 'success' : 'danger'" size="small">
                {{ row.is_correct ? '正确' : '错误' }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
      </template>
      <template #footer>
        <el-button type="primary" @click="submissionDetailVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import * as assignmentApi from '@/api/assignment'
import * as classApi from '@/api/class'
import { analysisApi } from '@/api/analysis'

const loading = ref(false)
const submitting = ref(false)
const assignmentList = ref([])
const classList = ref([])
const questionList = ref([])
const submissionList = ref([])
const dialogVisible = ref(false)
const showQuestionDialog = ref(false)
const submissionDialogVisible = ref(false)
const filterClassId = ref(null)
const selectedQuestions = ref([])
const tempSelectedQuestions = ref([])
const currentAssignment = ref(null)
const formRef = ref(null)
const assignmentDetailVisible = ref(false)
const assignmentDetail = ref(null)
const submissionDetailVisible = ref(false)
const currentSubmission = ref(null)

const assignmentDetailQuestions = computed(() => {
  const q = assignmentDetail.value?.questions
  if (!q) return []
  const list = q.questions ?? q
  return Array.isArray(list) ? list : []
})

const submissionDetailRows = computed(() => {
  const sub = currentSubmission.value
  if (!sub?.results?.results) return []
  return Object.entries(sub.results.results).map(([qid, r]) => ({
    qid,
    student_answer: r.student_answer ?? '—',
    correct_answer: r.correct_answer ?? '—',
    is_correct: !!r.is_correct
  }))
})

const formData = reactive({
  class_id: null,
  title: '',
  description: '',
  question_ids: [],
  deadline: null
})

const formRules = {
  class_id: [{ required: true, message: '请选择班级', trigger: 'change' }],
  title: [{ required: true, message: '请输入作业标题', trigger: 'blur' }],
  question_ids: [{ required: true, message: '请至少选择一道题目', trigger: 'change' }]
}

onMounted(() => {
  loadClasses()
  loadAssignments()
  loadQuestions()
})

const loadClasses = async () => {
  try {
    classList.value = await classApi.getClasses()
  } catch (error) {
    ElMessage.error('加载班级列表失败')
  }
}

const loadAssignments = async () => {
  loading.value = true
  try {
    assignmentList.value = await assignmentApi.getAssignments(filterClassId.value)
  } catch (error) {
    ElMessage.error('加载作业列表失败：' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

const loadQuestions = async () => {
  try {
    questionList.value = await analysisApi.getQuestions({})
  } catch (error) {
    console.error('加载题目列表失败:', error)
  }
}

const getClassName = (classId) => {
  const cls = classList.value.find(c => c.id === classId)
  return cls ? cls.name : '-'
}

const getQuestionTypeName = (type) => {
  const names = {
    choice: '选择题',
    fill: '填空题',
    short_answer: '简答题'
  }
  return names[type] || type
}

const handleCreate = () => {
  formData.class_id = null
  formData.title = ''
  formData.description = ''
  formData.question_ids = []
  formData.deadline = null
  selectedQuestions.value = []
  dialogVisible.value = true
}

const handleQuestionSelection = (selection) => {
  tempSelectedQuestions.value = selection
}

const confirmQuestionSelection = () => {
  selectedQuestions.value = [...tempSelectedQuestions.value]
  formData.question_ids = selectedQuestions.value.map(q => q.id)
  showQuestionDialog.value = false
  ElMessage.success(`已选择 ${selectedQuestions.value.length} 道题目`)
}

const removeQuestion = (questionId) => {
  selectedQuestions.value = selectedQuestions.value.filter(q => q.id !== questionId)
  formData.question_ids = selectedQuestions.value.map(q => q.id)
}

const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (valid) {
      if (formData.question_ids.length === 0) {
        ElMessage.warning('请至少选择一道题目')
        return
      }

      submitting.value = true
      try {
        await assignmentApi.createAssignment(formData)
        ElMessage.success('作业创建成功')
        dialogVisible.value = false
        loadAssignments()
      } catch (error) {
        ElMessage.error('创建失败：' + (error.response?.data?.detail || error.message))
      } finally {
        submitting.value = false
      }
    }
  })
}

const publishAssignment = async (id) => {
  try {
    await assignmentApi.publishAssignment(id)
    ElMessage.success('作业已发布')
    loadAssignments()
  } catch (error) {
    ElMessage.error('发布失败：' + (error.response?.data?.detail || error.message))
  }
}

const viewAssignment = async (assignment) => {
  try {
    assignmentDetail.value = await assignmentApi.getAssignment(assignment.id)
    assignmentDetailVisible.value = true
  } catch (error) {
    ElMessage.error('加载作业详情失败：' + (error.response?.data?.detail || error.message))
  }
}

const viewSubmissions = async (assignment) => {
  currentAssignment.value = assignment
  try {
    submissionList.value = await assignmentApi.getSubmissions(assignment.id)
    submissionDialogVisible.value = true
  } catch (error) {
    ElMessage.error('加载提交列表失败：' + (error.response?.data?.detail || error.message))
  }
}

const viewSubmissionDetail = (submission) => {
  currentSubmission.value = submission
  submissionDetailVisible.value = true
}

const formatTime = (time) => {
  if (!time) return ''
  const date = new Date(time)
  return date.toLocaleString('zh-CN')
}
</script>

<style scoped>
.assignment-management-container {
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

.filter-bar {
  margin-bottom: 20px;
}

.question-selection {
  width: 100%;
}

.selected-questions {
  margin-top: 10px;
  min-height: 40px;
  padding: 10px;
  border: 1px dashed #dcdfe6;
  border-radius: 4px;
}
</style>

