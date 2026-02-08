<template>
  <div class="teaching-design-container">
    <el-card class="design-card">
      <template #header>
        <div class="card-header">
          <span>教学设计生成</span>
          <el-button type="primary" @click="showGenerateDialog = true">
            <el-icon><Plus /></el-icon>
            新建教学设计
          </el-button>
        </div>
      </template>

      <!-- 教学设计列表 -->
      <el-table :data="designList" v-loading="loading" style="width: 100%">
        <el-table-column prop="subject" label="学科" width="100" />
        <el-table-column prop="grade" label="学段" width="100" />
        <el-table-column prop="topic" label="课时主题" min-width="200" />
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="viewDesign(row)">查看</el-button>
            <el-button link type="primary" @click="exportWord(row.id)">导出Word</el-button>
            <el-button link type="danger" @click="deleteDesign(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 生成对话框 -->
    <el-dialog
      v-model="showGenerateDialog"
      title="生成教学设计"
      width="600px"
    >
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
        <el-form-item label="学段" required>
          <el-select v-model="generateForm.grade" placeholder="请选择学段" style="width: 100%">
            <el-option label="小学" value="小学" />
            <el-option label="初中" value="初中" />
            <el-option label="高中" value="高中" />
          </el-select>
        </el-form-item>
        <el-form-item label="课时主题" required>
          <el-input v-model="generateForm.topic" placeholder="例如：一次函数的图像与性质" />
        </el-form-item>
        <el-form-item label="教学目标" required>
          <el-input
            v-model="generateForm.teaching_objectives"
            type="textarea"
            :rows="4"
            placeholder="请输入教学目标"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showGenerateDialog = false">取消</el-button>
        <el-button type="primary" :loading="generating" @click="handleGenerate">
          生成
        </el-button>
      </template>
    </el-dialog>

    <!-- 查看/编辑对话框 -->
    <el-dialog
      v-model="showViewDialog"
      :title="editingMode ? '编辑教学设计' : currentDesign?.topic"
      width="80%"
      top="5vh"
    >
      <div v-if="currentDesign" class="design-content">
        <div class="edit-toolbar" v-if="!editingMode">
          <el-button type="primary" @click="startEdit">
            <el-icon><Edit /></el-icon>
            编辑
          </el-button>
        </div>
        <el-tabs v-model="activeTab">
          <el-tab-pane label="导入环节" name="import">
            <div class="section-content">
              <p><strong>时间：</strong>
                <span v-if="!editingMode">{{ currentDesign.content?.import?.time || 0 }}分钟</span>
                <el-input-number v-else v-model="editingContent.import.time" :min="0" :max="60" size="small" style="width: 120px" /> 分钟
              </p>
              <p><strong>内容：</strong></p>
              <div v-if="!editingMode" class="content-text">{{ currentDesign.content?.import?.content }}</div>
              <el-input
                v-else
                v-model="editingContent.import.content"
                type="textarea"
                :rows="6"
                placeholder="请输入导入环节内容"
              />
            </div>
          </el-tab-pane>
          <el-tab-pane label="讲授环节" name="teaching">
            <div class="section-content">
              <p><strong>时间：</strong>
                <span v-if="!editingMode">{{ currentDesign.content?.teaching?.time || 0 }}分钟</span>
                <el-input-number v-else v-model="editingContent.teaching.time" :min="0" :max="60" size="small" style="width: 120px" /> 分钟
              </p>
              <p><strong>内容：</strong></p>
              <div v-if="!editingMode" class="content-text">{{ currentDesign.content?.teaching?.content }}</div>
              <el-input
                v-else
                v-model="editingContent.teaching.content"
                type="textarea"
                :rows="8"
                placeholder="请输入讲授环节内容"
              />
              <p v-if="currentDesign.content?.teaching?.key_points || editingMode" style="margin-top: 20px;">
                <strong>重点知识点：</strong>
              </p>
              <ul v-if="!editingMode && currentDesign.content?.teaching?.key_points">
                <li v-for="(point, index) in currentDesign.content.teaching.key_points" :key="index">
                  {{ point }}
                </li>
              </ul>
              <el-input
                v-else-if="editingMode"
                v-model="editingContent.teaching.key_points_text"
                type="textarea"
                :rows="4"
                placeholder="每行一个知识点"
              />
            </div>
          </el-tab-pane>
          <el-tab-pane label="互动环节" name="interaction">
            <div class="section-content">
              <p><strong>时间：</strong>
                <span v-if="!editingMode">{{ currentDesign.content?.interaction?.time || 0 }}分钟</span>
                <el-input-number v-else v-model="editingContent.interaction.time" :min="0" :max="60" size="small" style="width: 120px" /> 分钟
              </p>
              <div v-if="!editingMode && currentDesign.content?.interaction?.activities">
                <div
                  v-for="(activity, index) in currentDesign.content.interaction.activities"
                  :key="index"
                  class="activity-item"
                >
                  <p><strong>{{ activity.type }}：</strong>{{ activity.content }}（{{ activity.time }}分钟）</p>
                </div>
              </div>
              <el-input
                v-else-if="editingMode"
                v-model="editingContent.interaction.activities_text"
                type="textarea"
                :rows="6"
                placeholder="请输入互动环节内容，每行一个活动"
              />
            </div>
          </el-tab-pane>
          <el-tab-pane label="总结环节" name="summary">
            <div class="section-content">
              <p><strong>时间：</strong>
                <span v-if="!editingMode">{{ currentDesign.content?.summary?.time || 0 }}分钟</span>
                <el-input-number v-else v-model="editingContent.summary.time" :min="0" :max="60" size="small" style="width: 120px" /> 分钟
              </p>
              <div v-if="!editingMode" class="content-text">{{ currentDesign.content?.summary?.content }}</div>
              <el-input
                v-else
                v-model="editingContent.summary.content"
                type="textarea"
                :rows="6"
                placeholder="请输入总结环节内容"
              />
            </div>
          </el-tab-pane>
          <el-tab-pane label="预期成果" name="outcomes">
            <div class="section-content">
              <div v-if="!editingMode" class="content-text">{{ currentDesign.content?.expected_outcomes }}</div>
              <el-input
                v-else
                v-model="editingContent.expected_outcomes"
                type="textarea"
                :rows="6"
                placeholder="请输入预期成果"
              />
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
      <template #footer>
        <el-button @click="cancelEdit" v-if="editingMode">取消</el-button>
        <el-button @click="showViewDialog = false" v-else>关闭</el-button>
        <el-button type="primary" @click="saveEdit" v-if="editingMode" :loading="saving">保存</el-button>
        <el-button type="primary" @click="exportWord(currentDesign?.id)" v-else>导出Word</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit } from '@element-plus/icons-vue'
import { teachingApi } from '@/api/teaching'

const designList = ref([])
const loading = ref(false)
const generating = ref(false)
const saving = ref(false)
const showGenerateDialog = ref(false)
const showViewDialog = ref(false)
const currentDesign = ref(null)
const activeTab = ref('import')
const editingMode = ref(false)
const editingContent = reactive({
  import: { time: 0, content: '' },
  teaching: { time: 0, content: '', key_points_text: '' },
  interaction: { time: 0, activities_text: '' },
  summary: { time: 0, content: '' },
  expected_outcomes: ''
})

const generateForm = ref({
  subject: '',
  grade: '',
  topic: '',
  teaching_objectives: ''
})

const formatDate = (date) => {
  if (!date) return ''
  return new Date(date).toLocaleString('zh-CN')
}

const loadDesigns = async () => {
  loading.value = true
  try {
    designList.value = await teachingApi.getDesigns()
  } catch (error) {
    ElMessage.error('加载教学设计失败')
  } finally {
    loading.value = false
  }
}

const handleGenerate = async () => {
  if (!generateForm.value.subject || !generateForm.value.grade ||
      !generateForm.value.topic || !generateForm.value.teaching_objectives) {
    ElMessage.warning('请填写完整信息')
    return
  }

  generating.value = true
  try {
    await teachingApi.generateDesign(generateForm.value)
    ElMessage.success('教学设计生成成功')
    showGenerateDialog.value = false
    generateForm.value = { subject: '', grade: '', topic: '', teaching_objectives: '' }
    loadDesigns()
  } catch (error) {
    ElMessage.error('生成失败：' + (error.response?.data?.detail || error.message))
  } finally {
    generating.value = false
  }
}

const viewDesign = async (design) => {
  try {
    currentDesign.value = await teachingApi.getDesign(design.id)
    showViewDialog.value = true
    activeTab.value = 'import'
    editingMode.value = false
  } catch (error) {
    ElMessage.error('加载教学设计失败')
  }
}

const startEdit = () => {
  editingMode.value = true
  // 初始化编辑内容
  const content = currentDesign.value.content || {}
  editingContent.import = {
    time: content.import?.time || 5,
    content: content.import?.content || ''
  }
  editingContent.teaching = {
    time: content.teaching?.time || 25,
    content: content.teaching?.content || '',
    key_points_text: content.teaching?.key_points?.join('\n') || ''
  }
  editingContent.interaction = {
    time: content.interaction?.time || 10,
    activities_text: content.interaction?.activities?.map(a => `${a.type}：${a.content}（${a.time}分钟）`).join('\n') || ''
  }
  editingContent.summary = {
    time: content.summary?.time || 5,
    content: content.summary?.content || ''
  }
  editingContent.expected_outcomes = content.expected_outcomes || ''
}

const cancelEdit = () => {
  editingMode.value = false
}

const saveEdit = async () => {
  saving.value = true
  try {
    // 构建保存的内容
    const content = {
      import: {
        title: "导入环节",
        time: editingContent.import.time,
        content: editingContent.import.content,
        method: ""
      },
      teaching: {
        title: "讲授环节",
        time: editingContent.teaching.time,
        content: editingContent.teaching.content,
        key_points: editingContent.teaching.key_points_text.split('\n').filter(p => p.trim())
      },
      interaction: {
        title: "互动环节",
        time: editingContent.interaction.time,
        activities: editingContent.interaction.activities_text.split('\n').filter(a => a.trim()).map((line, idx) => {
          const match = line.match(/(.+?)：(.+?)（(\d+)分钟）/)
          if (match) {
            return { type: match[1], content: match[2], time: parseInt(match[3]) }
          }
          return { type: "活动", content: line, time: 3 }
        })
      },
      summary: {
        title: "总结环节",
        time: editingContent.summary.time,
        content: editingContent.summary.content
      },
      expected_outcomes: editingContent.expected_outcomes
    }
    
    await teachingApi.updateDesign(currentDesign.value.id, content)
    ElMessage.success('保存成功')
    editingMode.value = false
    // 重新加载数据
    currentDesign.value = await teachingApi.getDesign(currentDesign.value.id)
  } catch (error) {
    ElMessage.error('保存失败：' + (error.response?.data?.detail || error.message))
  } finally {
    saving.value = false
  }
}

const exportWord = async (id) => {
  try {
    const response = await teachingApi.exportToWord(id)
    
    // 创建下载链接并直接下载
    const blob = new Blob([response], {
      type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `教学设计_${id}_${new Date().getTime()}.docx`
    link.style.display = 'none'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('Word文档导出成功')
  } catch (error) {
    ElMessage.error('导出失败：' + (error.response?.data?.detail || error.message))
  }
}

const deleteDesign = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除这个教学设计吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await teachingApi.deleteDesign(id)
    ElMessage.success('删除成功')
    loadDesigns()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败：' + (error.response?.data?.detail || error.message))
    }
  }
}

onMounted(() => {
  loadDesigns()
})
</script>

<style scoped>
.teaching-design-container {
  height: 100%;
}

.design-card {
  background-color: #ffffff;
  border: none;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.design-content {
  padding: 20px;
}

.section-content {
  padding: 20px;
  background-color: #fafafa;
  border-radius: 8px;
}

.content-text {
  margin-top: 10px;
  line-height: 1.8;
  color: #333333;
  white-space: pre-wrap;
}

.activity-item {
  margin-bottom: 15px;
  padding: 10px;
  background-color: #ffffff;
  border-radius: 4px;
}

.activity-item p {
  margin: 0;
  line-height: 1.6;
}

.edit-toolbar {
  margin-bottom: 20px;
  text-align: right;
}

ul {
  margin-top: 10px;
  padding-left: 20px;
}

li {
  margin-bottom: 8px;
  line-height: 1.6;
}
</style>

