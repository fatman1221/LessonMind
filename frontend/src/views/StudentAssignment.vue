<template>
  <div class="student-assignment-container">
    <el-card class="assignment-card">
      <template #header>
        <div class="card-header">
          <span>我的作业</span>
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
      </template>

      <!-- 作业列表 -->
      <el-table :data="assignmentList" v-loading="loading" style="width: 100%">
        <el-table-column prop="title" label="作业标题" min-width="200" />
        <el-table-column prop="class_id" label="班级" width="150">
          <template #default="{ row }">
            {{ getClassName(row.class_id) }}
          </template>
        </el-table-column>
        <el-table-column prop="deadline" label="截止时间" width="180">
          <template #default="{ row }">
            <span :class="{ 'deadline-warning': isDeadlineNear(row.deadline) }">
              {{ row.deadline ? formatTime(row.deadline) : '无' }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusTag(row)">{{ getStatusText(row) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button
              link
              type="primary"
              @click="doAssignment(row)"
              :disabled="!row.is_published || isExpired(row.deadline)"
            >
              {{ hasSubmitted(row.id) ? '查看' : '作答' }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 作答对话框 -->
    <el-dialog
      v-model="assignmentDialogVisible"
      :title="currentAssignment?.title"
      width="80%"
      top="5vh"
    >
      <div v-if="currentAssignment" class="assignment-content">
        <div class="assignment-info">
          <p><strong>作业描述：</strong>{{ currentAssignment.description || '无' }}</p>
          <p v-if="currentAssignment.deadline">
            <strong>截止时间：</strong>{{ formatTime(currentAssignment.deadline) }}
          </p>
        </div>

        <div v-if="!mySubmission" class="question-list">
          <div
            v-for="(question, index) in questions"
            :key="question.id"
            class="question-item"
          >
            <div class="question-header">
              <span class="question-number">第 {{ index + 1 }} 题</span>
              <el-tag size="small">{{ getQuestionTypeName(question.type) }}</el-tag>
            </div>
            <div class="question-content">{{ question.question }}</div>
            
            <!-- 选择题 -->
            <div v-if="question.type === 'choice'" class="question-options">
              <el-radio-group v-model="answers[question.id]">
                <el-radio
                  v-for="(option, optIndex) in (question.options || [])"
                  :key="optIndex"
                  :label="String.fromCharCode(65 + optIndex)"
                  style="display: block; margin: 10px 0"
                >
                  {{ String.fromCharCode(65 + optIndex) }}. {{ option }}
                </el-radio>
              </el-radio-group>
              <div v-if="!question.options || question.options.length === 0" class="no-options">
                <el-alert
                  type="warning"
                  :closable="false"
                  show-icon
                >
                  <template #title>
                    此选择题缺少选项，请直接输入答案（A/B/C/D）
                  </template>
                </el-alert>
                <el-input
                  v-model="answers[question.id]"
                  placeholder="请输入答案（A/B/C/D）"
                  style="margin-top: 10px; width: 200px"
                />
              </div>
            </div>
            
            <!-- 填空题 -->
            <div v-else-if="question.type === 'fill'" class="question-answer">
              <el-input
                v-model="answers[question.id]"
                placeholder="请输入答案"
                style="width: 100%"
              />
            </div>
            
            <!-- 简答题 -->
            <div v-else class="question-answer">
              <el-input
                v-model="answers[question.id]"
                type="textarea"
                :rows="4"
                placeholder="请输入答案"
              />
            </div>
          </div>
        </div>

        <!-- 已提交显示结果 -->
        <div v-else class="submission-result">
          <div class="score-summary">
            <h3>得分：{{ mySubmission.score }} / {{ mySubmission.total_score }}</h3>
            <p>正确率：{{ ((mySubmission.score / mySubmission.total_score) * 100).toFixed(1) }}%</p>
          </div>
          <div
            v-for="(question, index) in questions"
            :key="question.id"
            class="question-item"
          >
            <div class="question-header">
              <span class="question-number">第 {{ index + 1 }} 题</span>
              <el-tag
                :type="getResultTag(question.id)"
                size="small"
              >
                {{ getResultText(question.id) }}
              </el-tag>
            </div>
            <div class="question-content">{{ question.question }}</div>
            <div class="answer-comparison">
              <p><strong>您的答案：</strong>{{ getMyAnswer(question.id) }}</p>
              <p><strong>正确答案：</strong>{{ question.answer }}</p>
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="assignmentDialogVisible = false">关闭</el-button>
        <el-button
          v-if="!mySubmission"
          type="primary"
          @click="submitAssignment"
          :loading="submitting"
        >
          提交
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import * as assignmentApi from '@/api/assignment'
import * as classApi from '@/api/class'

const loading = ref(false)
const submitting = ref(false)
const assignmentList = ref([])
const classList = ref([])
const assignmentDialogVisible = ref(false)
const currentAssignment = ref(null)
const mySubmission = ref(null)
const questions = ref([])
const answers = reactive({})
const filterClassId = ref(null)
const submissionMap = ref({})

onMounted(() => {
  loadClasses()
  loadAssignments()
})

const loadClasses = async () => {
  try {
    classList.value = await classApi.getClasses()
  } catch (error) {
    console.error('加载班级列表失败:', error)
  }
}

const loadAssignments = async () => {
  loading.value = true
  try {
    assignmentList.value = await assignmentApi.getAssignments(filterClassId.value)
    // 加载每个作业的提交状态
    for (const assignment of assignmentList.value) {
      if (assignment.is_published) {
        try {
          const submission = await assignmentApi.getMySubmission(assignment.id)
          if (submission) {
            submissionMap.value[assignment.id] = submission
          }
        } catch (error) {
          // 没有提交记录，忽略
        }
      }
    }
  } catch (error) {
    ElMessage.error('加载作业列表失败：' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
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

const hasSubmitted = (assignmentId) => {
  return !!submissionMap.value[assignmentId]
}

const isExpired = (deadline) => {
  if (!deadline) return false
  return new Date(deadline) < new Date()
}

const isDeadlineNear = (deadline) => {
  if (!deadline) return false
  const deadlineDate = new Date(deadline)
  const now = new Date()
  const diff = deadlineDate - now
  return diff > 0 && diff < 24 * 60 * 60 * 1000 // 24小时内
}

const getStatusText = (assignment) => {
  if (!assignment.is_published) return '未发布'
  if (isExpired(assignment.deadline)) return '已过期'
  if (hasSubmitted(assignment.id)) return '已提交'
  return '待完成'
}

const getStatusTag = (assignment) => {
  if (!assignment.is_published) return 'info'
  if (isExpired(assignment.deadline)) return 'danger'
  if (hasSubmitted(assignment.id)) return 'success'
  return 'warning'
}

const doAssignment = async (assignment) => {
  currentAssignment.value = assignment
  try {
    // 加载作业详情
    const detail = await assignmentApi.getAssignment(assignment.id)
    questions.value = detail.questions?.questions || []
    
    // 加载我的提交
    try {
      mySubmission.value = await assignmentApi.getMySubmission(assignment.id)
      if (mySubmission.value) {
        // 已提交，显示结果
        answers.value = mySubmission.value.answers
      } else {
        // 未提交，初始化答案
        questions.value.forEach(q => {
          answers.value[q.id] = ''
        })
      }
    } catch (error) {
      // 没有提交记录
      questions.value.forEach(q => {
        answers.value[q.id] = ''
      })
    }
    
    assignmentDialogVisible.value = true
  } catch (error) {
    ElMessage.error('加载作业失败：' + (error.response?.data?.detail || error.message))
  }
}

const submitAssignment = async () => {
  // 检查是否所有题目都已作答
  const unanswered = questions.value.filter(q => !answers.value[q.id] || answers.value[q.id].trim() === '')
  if (unanswered.length > 0) {
    ElMessage.warning(`还有 ${unanswered.length} 道题目未作答`)
    return
  }

  submitting.value = true
  try {
    const result = await assignmentApi.submitAssignment(
      currentAssignment.value.id,
      answers.value
    )
    mySubmission.value = result
    submissionMap.value[currentAssignment.value.id] = result
    ElMessage.success('提交成功！得分：' + result.score + ' / ' + result.total_score)
    loadAssignments()
  } catch (error) {
    ElMessage.error('提交失败：' + (error.response?.data?.detail || error.message))
  } finally {
    submitting.value = false
  }
}

const getMyAnswer = (questionId) => {
  return mySubmission.value?.answers[questionId] || '未作答'
}

const getResultTag = (questionId) => {
  const result = mySubmission.value?.results?.results?.[questionId]
  return result?.is_correct ? 'success' : 'danger'
}

const getResultText = (questionId) => {
  const result = mySubmission.value?.results?.results?.[questionId]
  return result?.is_correct ? '正确' : '错误'
}

const formatTime = (time) => {
  if (!time) return ''
  const date = new Date(time)
  return date.toLocaleString('zh-CN')
}
</script>

<style scoped>
.student-assignment-container {
  height: 100%;
}

.assignment-card {
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.deadline-warning {
  color: #f56c6c;
  font-weight: bold;
}

.assignment-content {
  padding: 20px;
}

.assignment-info {
  margin-bottom: 20px;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.question-list,
.submission-result {
  margin-top: 20px;
}

.question-item {
  margin-bottom: 30px;
  padding: 20px;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  background-color: #ffffff;
}

.question-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.question-number {
  font-size: 16px;
  font-weight: bold;
  color: #409eff;
}

.question-content {
  margin: 15px 0;
  line-height: 1.8;
  font-size: 15px;
}

.question-options {
  margin-top: 15px;
}

.question-answer {
  margin-top: 15px;
}

.score-summary {
  text-align: center;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 8px;
  margin-bottom: 30px;
}

.score-summary h3 {
  margin: 0 0 10px 0;
  font-size: 28px;
}

.answer-comparison {
  margin-top: 15px;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.answer-comparison p {
  margin: 8px 0;
  line-height: 1.6;
}
</style>

