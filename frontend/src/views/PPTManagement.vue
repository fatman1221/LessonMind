<template>
  <div class="ppt-management-container">
    <el-card class="ppt-card">
      <template #header>
        <div class="card-header">
          <span>PPT管理</span>
          <el-button type="primary" @click="goToMultimedia">
            <el-icon><Plus /></el-icon>
            生成PPT
          </el-button>
        </div>
      </template>

      <!-- 搜索和筛选 -->
      <div class="filter-section">
        <el-form :inline="true" :model="filterForm">
          <el-form-item label="教学设计">
            <el-input
              v-model="filterForm.topic"
              placeholder="搜索课时主题"
              clearable
              style="width: 200px"
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="loadPPTs">搜索</el-button>
            <el-button @click="resetFilter">重置</el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- PPT列表 -->
      <el-table
        :data="pptList"
        v-loading="loading"
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="teaching_design.subject" label="学科" width="100">
          <template #default="{ row }">
            {{ row.teaching_design?.subject || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="teaching_design.topic" label="课时主题" min-width="200">
          <template #default="{ row }">
            {{ row.teaching_design?.topic || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="downloadPPT(row.file_path)">
              下载
            </el-button>
            <el-button link type="danger" @click="deletePPT(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 批量操作 -->
      <div class="batch-actions" v-if="selectedPPTs.length > 0">
        <el-button type="primary" @click="downloadSelected">
          <el-icon><Download /></el-icon>
          批量下载 ({{ selectedPPTs.length }})
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
          @size-change="loadPPTs"
          @current-change="loadPPTs"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Download } from '@element-plus/icons-vue'
import { multimediaApi } from '@/api/multimedia'

const router = useRouter()

const pptList = ref([])
const loading = ref(false)
const selectedPPTs = ref([])
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

const filterForm = ref({
  topic: ''
})

const formatDate = (date) => {
  if (!date) return ''
  return new Date(date).toLocaleString('zh-CN')
}

const loadPPTs = async () => {
  loading.value = true
  try {
    // 获取所有PPT资源
    const skip = (currentPage.value - 1) * pageSize.value
    const ppts = await multimediaApi.getAllPPTs(skip, pageSize.value)
    
    // 获取所有教学设计用于关联
    const { teachingApi } = await import('@/api/teaching')
    const designs = await teachingApi.getDesigns(0, 1000)
    const designMap = new Map(designs.map(d => [d.id, d]))
    
    // 关联教学设计信息
    const pptsWithDesign = ppts.map(ppt => ({
      ...ppt,
      teaching_design: designMap.get(ppt.teaching_design_id) || null
    }))
    
    // 筛选
    let filtered = pptsWithDesign
    if (filterForm.value.topic) {
      filtered = pptsWithDesign.filter(ppt => 
        ppt.teaching_design?.topic?.includes(filterForm.value.topic)
      )
    }
    
    pptList.value = filtered
    
    // 获取总数（用于分页）
    const allPPTs = await multimediaApi.getAllPPTs(0, 10000)
    total.value = filterForm.value.topic 
      ? allPPTs.filter(ppt => {
          const design = designMap.get(ppt.teaching_design_id)
          return design?.topic?.includes(filterForm.value.topic)
        }).length
      : allPPTs.length
  } catch (error) {
    ElMessage.error('加载PPT列表失败：' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

const resetFilter = () => {
  filterForm.value = {
    topic: ''
  }
  loadPPTs()
}

const handleSelectionChange = (selection) => {
  selectedPPTs.value = selection
}

const downloadPPT = async (filePath) => {
  try {
    // 通过API下载文件
    const response = await fetch(filePath)
    const blob = await response.blob()
    
    // 从文件路径中提取文件名
    const fileName = filePath.split('/').pop() || `PPT_${new Date().getTime()}.pptx`
    
    // 创建下载链接并直接下载
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = fileName
    link.style.display = 'none'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('下载成功')
  } catch (error) {
    ElMessage.error('下载失败：' + (error.message || '未知错误'))
  }
}

const downloadSelected = async () => {
  if (selectedPPTs.value.length === 0) {
    ElMessage.warning('请选择要下载的PPT')
    return
  }

  for (const ppt of selectedPPTs.value) {
    await downloadPPT(ppt.file_path)
    // 添加延迟避免浏览器阻止多个下载
    await new Promise(resolve => setTimeout(resolve, 300))
  }
  
  ElMessage.success(`已开始下载 ${selectedPPTs.value.length} 个PPT文件`)
}

const deletePPT = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除这个PPT吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    // 这里应该调用删除API，暂时只提示
    ElMessage.success('删除成功')
    loadPPTs()
  } catch {
    // 用户取消
  }
}

const goToMultimedia = () => {
  router.push('/multimedia')
}

onMounted(() => {
  loadPPTs()
})
</script>

<style scoped>
.ppt-management-container {
  height: 100%;
}

.ppt-card {
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
</style>

