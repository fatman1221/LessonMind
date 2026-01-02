<template>
  <div class="analysis-container">
    <el-row :gutter="20">
      <!-- 学情分析 -->
      <el-col :span="24">
        <el-card class="analysis-card">
          <template #header>
            <div class="card-header">
              <span>学情分析</span>
              <el-button type="primary" size="small" @click="showStudentDialog = true">
                导入学生数据
              </el-button>
            </div>
          </template>

          <el-form :model="analysisForm" label-width="100px" style="max-width: 500px">
            <el-form-item label="学生ID">
              <el-input v-model="analysisForm.student_id" placeholder="请输入学生ID" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="analyzing" @click="analyzeStudent">
                开始分析
              </el-button>
              <el-button @click="trainModel" :loading="training">训练模型</el-button>
            </el-form-item>
          </el-form>

          <div v-if="analysisResult" class="analysis-result">
            <h3>分析结果</h3>
            <el-descriptions :column="1" border>
              <el-descriptions-item label="掌握水平">
                <el-tag :type="getMasteryTagType(analysisResult.mastery_level)">
                  {{ analysisResult.mastery_level }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="掌握度">
                <el-progress
                  :percentage="Math.round(analysisResult.mastery_score * 100)"
                  :color="getProgressColor(analysisResult.mastery_score)"
                />
              </el-descriptions-item>
              <el-descriptions-item label="学习能力">
                <el-progress
                  :percentage="Math.round(analysisResult.ability_score * 100)"
                  :color="getProgressColor(analysisResult.ability_score)"
                />
              </el-descriptions-item>
              <el-descriptions-item label="学习习惯">
                <el-progress
                  :percentage="Math.round(analysisResult.habit_score * 100)"
                  :color="getProgressColor(analysisResult.habit_score)"
                />
              </el-descriptions-item>
            </el-descriptions>

            <div v-if="analysisResult.recommendations" class="recommendations">
              <h4>学习建议</h4>
              <ul>
                <li v-for="(rec, index) in analysisResult.recommendations" :key="index">
                  {{ rec }}
                </li>
              </ul>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 导入学生数据对话框 -->
    <el-dialog v-model="showStudentDialog" title="导入学生数据" width="600px">
      <el-form :model="studentForm" label-width="120px">
        <el-form-item label="学生ID" required>
          <el-input v-model="studentForm.student_id" />
        </el-form-item>
        <el-form-item label="学生姓名" required>
          <el-input v-model="studentForm.student_name" />
        </el-form-item>
        <el-form-item label="学科" required>
          <el-select v-model="studentForm.subject" style="width: 100%">
            <el-option label="数学" value="数学" />
            <el-option label="语文" value="语文" />
            <el-option label="英语" value="英语" />
          </el-select>
        </el-form-item>
        <el-form-item label="学段" required>
          <el-select v-model="studentForm.grade" style="width: 100%">
            <el-option label="小学" value="小学" />
            <el-option label="初中" value="初中" />
            <el-option label="高中" value="高中" />
          </el-select>
        </el-form-item>
        <el-form-item label="作业成绩">
          <el-input
            v-model="homeworkScoresText"
            type="textarea"
            :rows="3"
            placeholder="格式：作业1:85,作业2:90,作业3:88"
            @blur="parseHomeworkScores"
          />
        </el-form-item>
        <el-form-item label="学习行为">
          <el-input
            v-model="learningBehaviorText"
            type="textarea"
            :rows="3"
            placeholder='格式：{"study_time": 10, "question_count": 5, "participation_rate": 0.8}'
            @blur="parseLearningBehavior"
          />
        </el-form-item>
        <el-form-item label="知识点掌握">
          <el-input
            v-model="knowledgeMasteryText"
            type="textarea"
            :rows="3"
            placeholder='格式：{"知识点1": 0.85, "知识点2": 0.7}'
            @blur="parseKnowledgeMastery"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showStudentDialog = false">取消</el-button>
        <el-button type="primary" :loading="importing" @click="importStudentData">
          导入
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { analysisApi } from '@/api/analysis'

const showStudentDialog = ref(false)
const analyzing = ref(false)
const training = ref(false)
const importing = ref(false)

const analysisForm = ref({
  student_id: ''
})

const studentForm = ref({
  student_id: '',
  student_name: '',
  subject: '',
  grade: '',
  homework_scores: {},
  learning_behavior: {},
  knowledge_mastery: {}
})

const homeworkScoresText = ref('')
const learningBehaviorText = ref('')
const knowledgeMasteryText = ref('')

const analysisResult = ref(null)

const parseHomeworkScores = () => {
  try {
    const scores = {}
    homeworkScoresText.value.split(',').forEach(item => {
      const [key, value] = item.split(':')
      if (key && value) {
        scores[key.trim()] = parseFloat(value.trim())
      }
    })
    studentForm.value.homework_scores = scores
  } catch (e) {
    console.error('解析作业成绩失败', e)
  }
}

const parseLearningBehavior = () => {
  try {
    studentForm.value.learning_behavior = JSON.parse(learningBehaviorText.value || '{}')
  } catch (e) {
    console.error('解析学习行为失败', e)
  }
}

const parseKnowledgeMastery = () => {
  try {
    studentForm.value.knowledge_mastery = JSON.parse(knowledgeMasteryText.value || '{}')
  } catch (e) {
    console.error('解析知识点掌握失败', e)
  }
}

const analyzeStudent = async () => {
  if (!analysisForm.value.student_id) {
    ElMessage.warning('请输入学生ID')
    return
  }

  analyzing.value = true
  try {
    analysisResult.value = await analysisApi.analyzeStudent(analysisForm.value.student_id)
    ElMessage.success('分析完成')
  } catch (error) {
    ElMessage.error('分析失败：' + (error.response?.data?.detail || error.message))
  } finally {
    analyzing.value = false
  }
}

const trainModel = async () => {
  training.value = true
  try {
    const res = await analysisApi.trainModel()
    ElMessage.success(`模型训练成功，使用了${res.training_samples}条数据`)
  } catch (error) {
    ElMessage.error('训练失败：' + (error.response?.data?.detail || error.message))
  } finally {
    training.value = false
  }
}

const generateQuestions = async () => {
  if (!questionForm.value.subject || !questionForm.value.knowledge_point) {
    ElMessage.warning('请填写学科和知识点')
    return
  }

  generatingQuestions.value = true
  try {
    generatedQuestions.value = await analysisApi.generateQuestions({
      subject: questionForm.value.subject,
      knowledge_point: questionForm.value.knowledge_point,
      question_types: questionForm.value.question_types,
      count: questionForm.value.count
    })
    ElMessage.success('题目生成成功')
  } catch (error) {
    ElMessage.error('生成题目失败：' + (error.response?.data?.detail || error.message))
  } finally {
    generatingQuestions.value = false
  }
}

const importStudentData = async () => {
  parseHomeworkScores()
  parseLearningBehavior()
  parseKnowledgeMastery()

  importing.value = true
  try {
    await analysisApi.createStudentData(studentForm.value)
    ElMessage.success('学生数据导入成功')
    showStudentDialog.value = false
    studentForm.value = {
      student_id: '',
      student_name: '',
      subject: '',
      grade: '',
      homework_scores: {},
      learning_behavior: {},
      knowledge_mastery: {}
    }
    homeworkScoresText.value = ''
    learningBehaviorText.value = ''
    knowledgeMasteryText.value = ''
  } catch (error) {
    ElMessage.error('导入失败：' + (error.response?.data?.detail || error.message))
  } finally {
    importing.value = false
  }
}

const getMasteryTagType = (level) => {
  if (level === '掌握') return 'success'
  if (level === '部分掌握') return 'warning'
  return 'danger'
}

const getProgressColor = (score) => {
  if (score >= 0.8) return '#67c23a'
  if (score >= 0.6) return '#e6a23c'
  return '#f56c6c'
}

const getQuestionTypeName = (type) => {
  const map = {
    choice: '选择题',
    fill: '填空题',
    short_answer: '简答题'
  }
  return map[type] || type
}
</script>

<style scoped>
.analysis-container {
  height: 100%;
}

.analysis-card,
.question-card {
  background-color: #ffffff;
  border: none;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.analysis-result {
  margin-top: 20px;
  padding: 20px;
  background-color: #fafafa;
  border-radius: 8px;
}

.analysis-result h3 {
  margin-bottom: 15px;
  color: #333333;
}

.recommendations {
  margin-top: 20px;
}

.recommendations h4 {
  margin-bottom: 10px;
  color: #333333;
}

.recommendations ul {
  margin: 0;
  padding-left: 20px;
}

.recommendations li {
  margin-bottom: 8px;
  line-height: 1.6;
  color: #666666;
}

.questions-list {
  margin-top: 20px;
}

.questions-list h3 {
  margin-bottom: 15px;
  color: #333333;
}

.question-item {
  padding: 15px;
  margin-bottom: 15px;
  background-color: #fafafa;
  border-radius: 8px;
  border-left: 3px solid #409EFF;
}

.question-item p {
  margin: 8px 0;
  line-height: 1.6;
  color: #333333;
}

.options {
  margin: 10px 0;
  padding-left: 20px;
}

.answer {
  color: #67c23a;
  font-weight: 500;
}

.explanation {
  color: #666666;
  font-size: 14px;
}
</style>

