<template>
  <div class="analysis-container">
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card class="analysis-card">
          <template #header>
            <div class="card-header">
              <span>学情分析</span>
            </div>
          </template>

          <el-form label-width="100px" style="max-width: 520px">
            <el-form-item label="关联学生">
              <el-select
                v-model="selectedStudentId"
                filterable
                clearable
                placeholder="请选择要分析的学生账号"
                style="width: 100%"
                :loading="loadingStudents"
              >
                <el-option
                  v-for="s in studentOptions"
                  :key="s.id"
                  :label="`${s.username}（ID: ${s.id}）`"
                  :value="s.id"
                  :disabled="!s.is_active"
                />
              </el-select>
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
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { analysisApi } from '@/api/analysis'
import * as classApi from '@/api/class'

const selectedStudentId = ref(null)
const studentOptions = ref([])
const loadingStudents = ref(false)
const analyzing = ref(false)
const training = ref(false)
const analysisResult = ref(null)

const loadStudents = async () => {
  loadingStudents.value = true
  try {
    studentOptions.value = await classApi.getAvailableStudents()
  } catch (error) {
    ElMessage.error('加载学生列表失败：' + (error.response?.data?.detail || error.message))
    studentOptions.value = []
  } finally {
    loadingStudents.value = false
  }
}

onMounted(() => {
  loadStudents()
})

const analyzeStudent = async () => {
  if (selectedStudentId.value == null || selectedStudentId.value === '') {
    ElMessage.warning('请先关联并选择一名学生')
    return
  }

  analyzing.value = true
  try {
    analysisResult.value = await analysisApi.analyzeStudent(String(selectedStudentId.value))
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
</script>

<style scoped>
.analysis-container {
  height: 100%;
}

.analysis-card {
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
</style>
