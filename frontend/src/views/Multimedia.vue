<template>
  <div class="multimedia-container">
    <el-card class="multimedia-card">
      <template #header>
        <div class="card-header">
          <span>多媒体资源生成</span>
        </div>
      </template>
      <el-alert
        v-if="designList.length === 0"
        type="warning"
        :closable="false"
        show-icon
        style="margin-bottom: 16px"
        title="当前暂无教学设计，请先在“教学设计”页面创建后再生成图片/PPT。"
      />

      <el-tabs v-model="activeTab">
        <!-- 图片生成 -->
        <el-tab-pane label="图片生成" name="image">
          <el-form :model="imageForm" label-width="120px" style="max-width: 600px">
            <el-form-item label="选择教学设计">
              <el-select
                v-model="imageForm.teaching_design_id"
                placeholder="请选择教学设计"
                style="width: 100%"
                @change="loadDesignDetails"
              >
                <el-option
                  v-for="design in designList"
                  :key="design.id"
                  :label="`${design.subject} - ${design.topic}`"
                  :value="design.id"
                />
              </el-select>
            </el-form-item>
            <el-form-item label="学科">
              <el-input v-model="imageForm.subject" placeholder="例如：数学" />
            </el-form-item>
            <el-form-item label="知识点">
              <el-input
                v-model="imageForm.knowledge_point"
                type="textarea"
                :rows="3"
                placeholder="请输入需要生成图片的知识点"
              />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="generatingImage" :disabled="designList.length === 0" @click="generateImage">
                生成图片
              </el-button>
            </el-form-item>
          </el-form>

          <div v-if="imageResources.length > 0" class="resources-list">
            <h3>生成的图片</h3>
            <el-row :gutter="20">
              <el-col
                v-for="resource in imageResources"
                :key="resource.id"
                :span="8"
                style="margin-bottom: 20px"
              >
                <el-card>
                  <div class="resource-item">
                    <div class="resource-preview">
                      <el-icon :size="60"><Picture /></el-icon>
                      <p>图片资源</p>
                    </div>
                    <p class="resource-desc">{{ resource.description }}</p>
                    <el-button size="small" type="primary" plain @click="previewImage(resource.file_path)">
                      在线预览
                    </el-button>
                    <el-button size="small" @click="downloadResource(resource.file_path)">
                      下载
                    </el-button>
                  </div>
                </el-card>
              </el-col>
            </el-row>
          </div>
        </el-tab-pane>

        <!-- PPT生成 -->
        <el-tab-pane label="PPT生成" name="ppt">
          <el-form :model="pptForm" label-width="120px" style="max-width: 600px">
            <el-form-item label="选择教学设计" required>
              <el-select
                v-model="pptForm.teaching_design_id"
                placeholder="请选择教学设计"
                style="width: 100%"
              >
                <el-option
                  v-for="design in designList"
                  :key="design.id"
                  :label="`${design.subject} - ${design.topic}`"
                  :value="design.id"
                />
              </el-select>
            </el-form-item>
            <el-form-item label="PPT风格">
              <el-select v-model="pptForm.style" style="width: 100%">
                <el-option label="默认风格" value="default" />
                <el-option label="简约风格" value="simple" />
                <el-option label="商务风格" value="business" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="generatingPPT" :disabled="designList.length === 0" @click="generatePPT">
                生成PPT
              </el-button>
            </el-form-item>
          </el-form>

          <div v-if="pptResources.length > 0" class="resources-list">
            <h3>生成的PPT</h3>
            <el-row :gutter="20">
              <el-col
                v-for="resource in pptResources"
                :key="resource.id"
                :span="8"
                style="margin-bottom: 20px"
              >
                <el-card>
                  <div class="resource-item">
                    <div class="resource-preview">
                      <el-icon :size="60"><Document /></el-icon>
                      <p>PPT课件</p>
                    </div>
                    <p class="resource-desc">{{ resource.description }}</p>
                    <el-button size="small" @click="downloadResource(resource.file_path)">
                      下载
                    </el-button>
                  </div>
                </el-card>
              </el-col>
            </el-row>
          </div>
        </el-tab-pane>
      </el-tabs>

      <el-dialog v-model="imagePreviewVisible" title="图片在线预览" width="70%">
        <div class="image-preview-wrap" v-if="previewImageUrl">
          <img :src="previewImageUrl" alt="预览图片" class="preview-image" />
        </div>
        <template #footer>
          <el-button @click="imagePreviewVisible = false">关闭</el-button>
          <el-button type="primary" @click="downloadResource(previewRawPath)">下载原图</el-button>
        </template>
      </el-dialog>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Picture, Document } from '@element-plus/icons-vue'
import { teachingApi } from '@/api/teaching'
import { multimediaApi } from '@/api/multimedia'

const activeTab = ref('image')
const designList = ref([])
const imageResources = ref([])
const pptResources = ref([])
const generatingImage = ref(false)
const generatingPPT = ref(false)
const imagePreviewVisible = ref(false)
const previewImageUrl = ref('')
const previewRawPath = ref('')

const imageForm = ref({
  teaching_design_id: null,
  subject: '',
  knowledge_point: ''
})

const pptForm = ref({
  teaching_design_id: null,
  style: 'default'
})

const loadDesigns = async () => {
  try {
    designList.value = await teachingApi.getDesigns(0, 100)
  } catch (error) {
    ElMessage.error('加载教学设计失败')
  }
}

const loadDesignDetails = async () => {
  if (!imageForm.value.teaching_design_id) return
  
  try {
    const design = await teachingApi.getDesign(imageForm.value.teaching_design_id)
    imageForm.value.subject = design.subject
  } catch (error) {
    console.error('加载教学设计详情失败', error)
  }
}

const generateImage = async () => {
  if (!imageForm.value.teaching_design_id) {
    ElMessage.warning('请先选择教学设计')
    return
  }
  if (!imageForm.value.knowledge_point || !imageForm.value.subject) {
    ElMessage.warning('请填写知识点和学科')
    return
  }

  generatingImage.value = true
  try {
    const resource = await multimediaApi.generateImage({
      knowledge_point: imageForm.value.knowledge_point,
      subject: imageForm.value.subject,
      teaching_design_id: imageForm.value.teaching_design_id
    })
    ElMessage.success('图片生成成功')
    loadResources(imageForm.value.teaching_design_id)
  } catch (error) {
    ElMessage.error('生成图片失败：' + (error.response?.data?.detail || error.message))
  } finally {
    generatingImage.value = false
  }
}

const generatePPT = async () => {
  if (!pptForm.value.teaching_design_id) {
    ElMessage.warning('请选择教学设计')
    return
  }

  generatingPPT.value = true
  try {
    const resource = await multimediaApi.generatePPT({
      teaching_design_id: pptForm.value.teaching_design_id,
      style: pptForm.value.style
    })
    ElMessage.success('PPT生成成功')
    loadResources(pptForm.value.teaching_design_id)
  } catch (error) {
    ElMessage.error('生成PPT失败：' + (error.response?.data?.detail || error.message))
  } finally {
    generatingPPT.value = false
  }
}

const loadResources = async (designId) => {
  try {
    const resources = await multimediaApi.getResources(designId)
    imageResources.value = resources.filter(r => r.resource_type === 'image')
    pptResources.value = resources.filter(r => r.resource_type === 'ppt')
  } catch (error) {
    console.error('加载资源失败', error)
  }
}

const resolveResourceUrl = (filePath) => {
  if (!filePath) return ''
  if (filePath.startsWith('http://') || filePath.startsWith('https://')) {
    return filePath
  }
  // 静态资源由后端 8000 端口提供
  const host = window.location.hostname || '127.0.0.1'
  return `${window.location.protocol}//${host}:8000${filePath}`
}

const downloadResource = async (filePath) => {
  try {
    const resourceUrl = resolveResourceUrl(filePath)
    if (!resourceUrl) {
      ElMessage.error('资源地址无效')
      return
    }

    const response = await fetch(resourceUrl)
    if (!response.ok) {
      throw new Error(`下载失败，状态码 ${response.status}`)
    }

    const contentType = response.headers.get('content-type') || ''
    if (contentType.includes('text/html')) {
      throw new Error('返回内容不是文件，可能是资源地址错误')
    }

    const blob = await response.blob()
    if (!blob || blob.size === 0) {
      throw new Error('文件为空')
    }
    
    // 从文件路径中提取文件名
    const fileName = filePath.split('/').pop() || `资源_${new Date().getTime()}`
    
    // 创建下载链接并直接下载
    const objectUrl = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = objectUrl
    link.download = fileName
    link.style.display = 'none'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(objectUrl)
    
    ElMessage.success('下载成功')
  } catch (error) {
    ElMessage.error('下载失败：' + (error.message || '未知错误'))
  }
}

const previewImage = (filePath) => {
  const url = resolveResourceUrl(filePath)
  if (!url) {
    ElMessage.error('预览地址无效')
    return
  }
  previewRawPath.value = filePath
  previewImageUrl.value = url
  imagePreviewVisible.value = true
}

onMounted(() => {
  loadDesigns()
})
</script>

<style scoped>
.multimedia-container {
  height: 100%;
}

.multimedia-card {
  background-color: #ffffff;
  border: none;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.resources-list {
  margin-top: 30px;
}

.resources-list h3 {
  margin-bottom: 20px;
  color: #333333;
  font-size: 16px;
}

.resource-item {
  text-align: center;
}

.resource-preview {
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 8px;
  margin-bottom: 10px;
}

.resource-preview .el-icon {
  color: #409EFF;
}

.resource-preview p {
  margin-top: 10px;
  color: #666666;
  font-size: 14px;
}

.resource-desc {
  margin: 10px 0;
  font-size: 12px;
  color: #909399;
  min-height: 40px;
}

.image-preview-wrap {
  min-height: 400px;
  max-height: 70vh;
  overflow: auto;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  background: #f5f7fa;
  padding: 12px;
}

.preview-image {
  max-width: 100%;
  height: auto;
  border-radius: 6px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
}
</style>

