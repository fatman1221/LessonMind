<template>
  <div class="question-bank-container">
    <el-card class="question-card">
      <template #header>
        <div class="card-header">
          <span>题库管理</span>
          <el-button type="primary" @click="showGenerateDialog = true">
            <el-icon><Plus /></el-icon>
            生成题目
          </el-button>
        </div>
      </template>

      <!-- 搜索和筛选 -->
      <div class="filter-section">
        <el-form :inline="true" :model="filterForm">
          <el-form-item label="学科">
            <el-select v-model="filterForm.subject" placeholder="全部" clearable style="width: 120px">
              <el-option label="数学" value="数学" />
              <el-option label="语文" value="语文" />
              <el-option label="英语" value="英语" />
              <el-option label="物理" value="物理" />
              <el-option label="化学" value="化学" />
            </el-select>
          </el-form-item>
          <el-form-item label="题目类型">
            <el-select v-model="filterForm.question_type" placeholder="全部" clearable style="width: 120px">
              <el-option label="选择题" value="choice" />
              <el-option label="填空题" value="fill" />
              <el-option label="简答题" value="short_answer" />
            </el-select>
          </el-form-item>
          <el-form-item label="知识点">
            <el-input v-model="filterForm.knowledge_point" placeholder="搜索知识点" clearable style="width: 200px" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="loadQuestions">搜索</el-button>
            <el-button @click="resetFilter">重置</el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- 题库列表 -->
      <el-table
        :data="questionList"
        v-loading="loading"
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="subject" label="学科" width="100" />
        <el-table-column prop="knowledge_point" label="知识点" min-width="150" />
        <el-table-column prop="question_type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="getQuestionTypeTag(row.question_type)">
              {{ getQuestionTypeName(row.question_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="question_content" label="题目内容" min-width="300" show-overflow-tooltip />
        <el-table-column prop="difficulty" label="难度" width="100">
          <template #default="{ row }">
            <el-tag :type="getDifficultyTag(row.difficulty)">
              {{ getDifficultyName(row.difficulty) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="viewQuestion(row)">查看</el-button>
            <el-button link type="danger" @click="deleteQuestion(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 批量操作 -->
      <div class="batch-actions" v-if="selectedQuestions.length > 0">
        <el-button type="primary" @click="exportSelectedToWord">
          <el-icon><Download /></el-icon>
          导出选中题目 ({{ selectedQuestions.length }})
        </el-button>
        <el-button type="danger" @click="deleteSelectedQuestions">
          <el-icon><Delete /></el-icon>
          删除选中题目 ({{ selectedQuestions.length }})
        </el-button>
      </div>

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="loadQuestions"
          @current-change="loadQuestions"
        />
      </div>
    </el-card>

    <!-- 生成题目对话框 -->
    <el-dialog v-model="showGenerateDialog" title="生成题目" width="600px">
      <el-form :model="generateForm" label-width="100px">
        <el-form-item label="学科" required>
          <el-select v-model="generateForm.subject" placeholder="请选择学科" style="width: 100%">
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
        <el-form-item label="知识点" required>
          <el-input v-model="generateForm.knowledge_point" placeholder="例如：一次函数的图像与性质" />
        </el-form-item>
        <el-form-item label="题目类型" required>
          <el-checkbox-group v-model="generateForm.question_types">
            <el-checkbox label="choice">选择题</el-checkbox>
            <el-checkbox label="fill">填空题</el-checkbox>
            <el-checkbox label="short_answer">简答题</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        <el-form-item label="题目数量" required>
          <el-input-number v-model="generateForm.count" :min="1" :max="20" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showGenerateDialog = false">取消</el-button>
        <el-button type="primary" :loading="generating" @click="handleGenerate">
          生成
        </el-button>
      </template>
    </el-dialog>

    <!-- 查看题目对话框 -->
    <el-dialog v-model="showViewDialog" :title="currentQuestion?.knowledge_point" width="700px">
      <div v-if="currentQuestion" class="question-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="学科">{{ currentQuestion.subject }}</el-descriptions-item>
          <el-descriptions-item label="知识点">{{ currentQuestion.knowledge_point }}</el-descriptions-item>
          <el-descriptions-item label="题目类型">
            <el-tag :type="getQuestionTypeTag(currentQuestion.question_type)">
              {{ getQuestionTypeName(currentQuestion.question_type) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="难度">
            <el-tag :type="getDifficultyTag(currentQuestion.difficulty)">
              {{ getDifficultyName(currentQuestion.difficulty) }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>
        
        <div class="question-content">
          <h4>题目内容：</h4>
          <p>{{ currentQuestion.question_content }}</p>
        </div>
        
        <div class="question-answer">
          <h4>答案：</h4>
          <p>{{ currentQuestion.answer }}</p>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Download, Delete } from '@element-plus/icons-vue'
import { analysisApi } from '@/api/analysis'

const questionList = ref([])
const loading = ref(false)
const generating = ref(false)
const showGenerateDialog = ref(false)
const showViewDialog = ref(false)
const currentQuestion = ref(null)
const selectedQuestions = ref([])
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

const filterForm = ref({
  subject: '',
  question_type: '',
  knowledge_point: ''
})

const generateForm = ref({
  subject: '',
  knowledge_point: '',
  question_types: ['choice', 'fill', 'short_answer'],
  count: 3
})

const formatDate = (date) => {
  if (!date) return ''
  return new Date(date).toLocaleString('zh-CN')
}

const getQuestionTypeName = (type) => {
  const map = {
    choice: '选择题',
    fill: '填空题',
    short_answer: '简答题'
  }
  return map[type] || type
}

const getQuestionTypeTag = (type) => {
  const map = {
    choice: 'primary',
    fill: 'success',
    short_answer: 'warning'
  }
  return map[type] || ''
}

const getDifficultyName = (difficulty) => {
  const map = {
    easy: '简单',
    medium: '中等',
    hard: '困难'
  }
  return map[difficulty] || difficulty
}

const getDifficultyTag = (difficulty) => {
  const map = {
    easy: 'success',
    medium: 'warning',
    hard: 'danger'
  }
  return map[difficulty] || ''
}

const loadQuestions = async () => {
  loading.value = true
  try {
    const skip = (currentPage.value - 1) * pageSize.value
    const questions = await analysisApi.getQuestions({
      subject: filterForm.value.subject || undefined,
      question_type: filterForm.value.question_type || undefined,
      knowledge_point: filterForm.value.knowledge_point || undefined,
      skip,
      limit: pageSize.value
    })
    questionList.value = questions
    // 注意：如果后端返回总数，应该使用总数；这里假设返回所有数据
    total.value = questions.length
  } catch (error) {
    ElMessage.error('加载题库失败：' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

const resetFilter = () => {
  filterForm.value = {
    subject: '',
    question_type: '',
    knowledge_point: ''
  }
  loadQuestions()
}

const handleGenerate = async () => {
  if (!generateForm.value.subject || !generateForm.value.knowledge_point ||
      generateForm.value.question_types.length === 0) {
    ElMessage.warning('请填写完整信息')
    return
  }

  generating.value = true
  try {
    await analysisApi.generateQuestions(generateForm.value)
    ElMessage.success('题目生成成功')
    showGenerateDialog.value = false
    generateForm.value = {
      subject: '',
      knowledge_point: '',
      question_types: ['choice', 'fill', 'short_answer'],
      count: 3
    }
    loadQuestions()
  } catch (error) {
    ElMessage.error('生成失败：' + (error.response?.data?.detail || error.message))
  } finally {
    generating.value = false
  }
}

const viewQuestion = (question) => {
  currentQuestion.value = question
  showViewDialog.value = true
}

const deleteQuestion = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除这道题目吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await analysisApi.deleteQuestion(id)
    ElMessage.success('删除成功')
    loadQuestions()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败：' + (error.response?.data?.detail || error.message))
    }
  }
}

const deleteSelectedQuestions = async () => {
  if (selectedQuestions.value.length === 0) {
    ElMessage.warning('请选择要删除的题目')
    return
  }

  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedQuestions.value.length} 道题目吗？此操作不可恢复！`,
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    await analysisApi.deleteQuestions(selectedQuestions.value)
    ElMessage.success(`成功删除 ${selectedQuestions.value.length} 道题目`)
    selectedQuestions.value = []
    loadQuestions()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败：' + (error.response?.data?.detail || error.message))
    }
  }
}

const handleSelectionChange = (selection) => {
  selectedQuestions.value = selection.map(q => q.id)
}

const exportSelectedToWord = async () => {
  if (selectedQuestions.value.length === 0) {
    ElMessage.warning('请选择要导出的题目')
    return
  }

  try {
    loading.value = true
    const response = await analysisApi.exportQuestionsToWord(selectedQuestions.value)
    
    // 创建下载链接并直接下载
    const blob = new Blob([response], {
      type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `题库_${new Date().getTime()}.docx`
    link.style.display = 'none'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('导出成功')
  } catch (error) {
    console.error('导出错误:', error)
    ElMessage.error('导出失败：' + (error.response?.data?.detail || error.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadQuestions()
})
</script>

<style scoped>
.question-bank-container {
  height: 100%;
}

.question-card {
  background-color: #ffffff;
  border: none;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filter-section {
  margin-bottom: 20px;
  padding: 15px;
  background-color: #fafafa;
  border-radius: 8px;
}

.batch-actions {
  margin-top: 20px;
  padding: 15px;
  background-color: #f0f9ff;
  border-radius: 8px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.question-detail {
  padding: 10px;
}

.question-content,
.question-answer {
  margin-top: 20px;
}

.question-content h4,
.question-answer h4 {
  margin-bottom: 10px;
  color: #333333;
  font-size: 16px;
}

.question-content p,
.question-answer p {
  padding: 10px;
  background-color: #fafafa;
  border-radius: 4px;
  line-height: 1.8;
  white-space: pre-wrap;
}
</style>

