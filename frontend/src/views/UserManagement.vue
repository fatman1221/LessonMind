<template>
  <div class="user-management-container">
    <el-card class="management-card">
      <template #header>
        <div class="card-header">
          <span>我的收藏</span>
          <el-button type="primary" @click="handleCreate">
            <el-icon><Plus /></el-icon>
            新建收藏
          </el-button>
        </div>
      </template>

      <!-- 筛选栏 -->
      <div class="filter-bar">
        <el-select
          v-model="filterType"
          placeholder="筛选类型"
          clearable
          style="width: 200px"
          @change="loadFavorites"
        >
          <el-option label="全部" value="" />
          <el-option label="教学设计" value="teaching_design" />
          <el-option label="对话记录" value="chat" />
          <el-option label="题目" value="question" />
          <el-option label="自定义" value="custom" />
        </el-select>
        <el-input
          v-model="searchKeyword"
          placeholder="搜索标题或内容"
          style="width: 300px; margin-left: 10px"
          clearable
          @input="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>

      <!-- 收藏列表 -->
      <div class="favorites-list" v-loading="loading">
        <el-empty v-if="filteredFavorites.length === 0 && !loading" description="暂无收藏" />
        <div
          v-for="favorite in filteredFavorites"
          :key="favorite.id"
          class="favorite-item"
        >
          <div class="favorite-header">
            <div class="favorite-title">
              <el-tag :type="getTypeTagType(favorite.content_type)" size="small">
                {{ getTypeLabel(favorite.content_type) }}
              </el-tag>
              <span class="title-text">{{ favorite.title }}</span>
            </div>
            <div class="favorite-actions">
              <el-button
                type="primary"
                link
                size="small"
                @click="handleEdit(favorite)"
              >
                <el-icon><Edit /></el-icon>
                编辑
              </el-button>
              <el-button
                type="danger"
                link
                size="small"
                @click="handleDelete(favorite)"
              >
                <el-icon><Delete /></el-icon>
                删除
              </el-button>
            </div>
          </div>
          <div class="favorite-content" v-html="formatContent(favorite.content)"></div>
          <div class="favorite-footer">
            <span class="tags" v-if="favorite.tags">
              <el-icon><PriceTag /></el-icon>
              {{ favorite.tags }}
            </span>
            <span class="time">
              {{ formatTime(favorite.updated_at) }}
            </span>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="editingFavorite ? '编辑收藏' : '新建收藏'"
      width="80%"
      :close-on-click-modal="false"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="标题" prop="title">
          <el-input v-model="formData.title" placeholder="请输入标题" />
        </el-form-item>
        <el-form-item label="类型" prop="content_type">
          <el-select v-model="formData.content_type" placeholder="请选择类型" style="width: 100%">
            <el-option label="教学设计" value="teaching_design" />
            <el-option label="对话记录" value="chat" />
            <el-option label="题目" value="question" />
            <el-option label="自定义" value="custom" />
          </el-select>
        </el-form-item>
        <el-form-item label="内容" prop="content">
          <div class="editor-container">
            <div class="editor-toolbar">
              <el-button-group>
                <el-button
                  size="small"
                  @click="formatText('bold')"
                  :type="editorState.bold ? 'primary' : 'default'"
                >
                  <el-icon><Bold /></el-icon>
                </el-button>
                <el-button
                  size="small"
                  @click="formatText('italic')"
                  :type="editorState.italic ? 'primary' : 'default'"
                >
                  <el-icon><Italic /></el-icon>
                </el-button>
                <el-button
                  size="small"
                  @click="formatText('underline')"
                  :type="editorState.underline ? 'primary' : 'default'"
                >
                  <el-icon><Underline /></el-icon>
                </el-button>
              </el-button-group>
              <el-button-group style="margin-left: 10px">
                <el-button size="small" @click="insertText('h1')">
                  <strong>H1</strong>
                </el-button>
                <el-button size="small" @click="insertText('h2')">
                  <strong>H2</strong>
                </el-button>
                <el-button size="small" @click="insertText('h3')">
                  <strong>H3</strong>
                </el-button>
              </el-button-group>
              <el-button-group style="margin-left: 10px">
                <el-button size="small" @click="insertText('ul')">
                  <el-icon><List /></el-icon>
                </el-button>
                <el-button size="small" @click="insertText('ol')">
                  <el-icon><Menu /></el-icon>
                </el-button>
              </el-button-group>
              <el-button-group style="margin-left: 10px">
                <el-button size="small" @click="insertText('code')">
                  <el-icon><DocumentCopy /></el-icon>
                </el-button>
                <el-button size="small" @click="insertText('quote')">
                  <el-icon><ChatLineRound /></el-icon>
                </el-button>
              </el-button-group>
            </div>
            <div
              ref="editorRef"
              class="editor-content"
              contenteditable="true"
              @input="handleEditorInput"
              @focus="handleEditorFocus"
              @blur="handleEditorBlur"
              v-html="formData.content"
            ></div>
          </div>
        </el-form-item>
        <el-form-item label="标签">
          <el-input
            v-model="formData.tags"
            placeholder="多个标签用逗号分隔"
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
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus, Edit, Delete, Search, PriceTag,
  Bold, Italic, Underline, List, Menu, DocumentCopy, ChatLineRound
} from '@element-plus/icons-vue'
import * as userApi from '@/api/user'

const loading = ref(false)
const favorites = ref([])
const filterType = ref('')
const searchKeyword = ref('')
const dialogVisible = ref(false)
const editingFavorite = ref(null)
const submitting = ref(false)
const formRef = ref(null)
const editorRef = ref(null)

const formData = reactive({
  title: '',
  content_type: 'custom',
  content: '',
  tags: ''
})

const editorState = reactive({
  bold: false,
  italic: false,
  underline: false
})

const formRules = {
  title: [{ required: true, message: '请输入标题', trigger: 'blur' }],
  content_type: [{ required: true, message: '请选择类型', trigger: 'change' }],
  content: [{ required: true, message: '请输入内容', trigger: 'blur' }]
}

const filteredFavorites = computed(() => {
  let result = favorites.value

  if (filterType.value) {
    result = result.filter(f => f.content_type === filterType.value)
  }

  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(f =>
      f.title.toLowerCase().includes(keyword) ||
      f.content.toLowerCase().includes(keyword)
    )
  }

  return result
})

onMounted(() => {
  loadFavorites()
})

const loadFavorites = async () => {
  loading.value = true
  try {
    const data = await userApi.getFavorites(filterType.value || null)
    favorites.value = data
  } catch (error) {
    ElMessage.error('加载收藏失败：' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  // 搜索逻辑已在computed中处理
}

const handleCreate = () => {
  editingFavorite.value = null
  formData.title = ''
  formData.content_type = 'custom'
  formData.content = ''
  formData.tags = ''
  dialogVisible.value = true
  nextTick(() => {
    if (editorRef.value) {
      editorRef.value.focus()
    }
  })
}

const handleEdit = (favorite) => {
  editingFavorite.value = favorite
  formData.title = favorite.title
  formData.content_type = favorite.content_type
  formData.content = favorite.content
  formData.tags = favorite.tags || ''
  dialogVisible.value = true
  nextTick(() => {
    if (editorRef.value) {
      editorRef.value.focus()
    }
  })
}

const handleDelete = async (favorite) => {
  try {
    await ElMessageBox.confirm('确定要删除这个收藏吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await userApi.deleteFavorite(favorite.id)
    ElMessage.success('删除成功')
    loadFavorites()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败：' + (error.response?.data?.detail || error.message))
    }
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        const content = editorRef.value?.innerHTML || formData.content
        const submitData = {
          title: formData.title,
          content_type: formData.content_type,
          content: content,
          tags: formData.tags || null
        }

        if (editingFavorite.value) {
          await userApi.updateFavorite(editingFavorite.value.id, submitData)
          ElMessage.success('更新成功')
        } else {
          await userApi.createFavorite(submitData)
          ElMessage.success('创建成功')
        }
        dialogVisible.value = false
        loadFavorites()
      } catch (error) {
        ElMessage.error('保存失败：' + (error.response?.data?.detail || error.message))
      } finally {
        submitting.value = false
      }
    }
  })
}

const handleEditorInput = () => {
  if (editorRef.value) {
    formData.content = editorRef.value.innerHTML
    updateEditorState()
  }
}

const handleEditorFocus = () => {
  updateEditorState()
}

const handleEditorBlur = () => {
  // 可以在这里保存状态
}

const updateEditorState = () => {
  if (!editorRef.value) return
  const selection = window.getSelection()
  if (selection.rangeCount > 0) {
    const range = selection.getRangeAt(0)
    const parent = range.commonAncestorContainer.parentElement
    editorState.bold = document.queryCommandState('bold')
    editorState.italic = document.queryCommandState('italic')
    editorState.underline = document.queryCommandState('underline')
  }
}

const formatText = (command) => {
  if (!editorRef.value) return
  editorRef.value.focus()
  document.execCommand(command, false, null)
  updateEditorState()
  handleEditorInput()
}

const insertText = (type) => {
  if (!editorRef.value) return
  editorRef.value.focus()
  const selection = window.getSelection()
  const range = selection.getRangeAt(0)
  
  let text = ''
  switch (type) {
    case 'h1':
      text = '<h1>标题1</h1>'
      break
    case 'h2':
      text = '<h2>标题2</h2>'
      break
    case 'h3':
      text = '<h3>标题3</h3>'
      break
    case 'ul':
      text = '<ul><li>列表项</li></ul>'
      break
    case 'ol':
      text = '<ol><li>列表项</li></ol>'
      break
    case 'code':
      text = '<pre><code>代码块</code></pre>'
      break
    case 'quote':
      text = '<blockquote>引用内容</blockquote>'
      break
  }
  
  range.deleteContents()
  const div = document.createElement('div')
  div.innerHTML = text
  const fragment = document.createDocumentFragment()
  while (div.firstChild) {
    fragment.appendChild(div.firstChild)
  }
  range.insertNode(fragment)
  handleEditorInput()
}

const formatContent = (content) => {
  if (!content) return ''
  // 简单的HTML转义和格式化
  return content.replace(/\n/g, '<br>')
}

const formatTime = (time) => {
  if (!time) return ''
  const date = new Date(time)
  return date.toLocaleString('zh-CN')
}

const getTypeLabel = (type) => {
  const labels = {
    teaching_design: '教学设计',
    chat: '对话记录',
    question: '题目',
    custom: '自定义'
  }
  return labels[type] || type
}

const getTypeTagType = (type) => {
  const types = {
    teaching_design: 'primary',
    chat: 'success',
    question: 'warning',
    custom: 'info'
  }
  return types[type] || 'info'
}
</script>

<style scoped>
.user-management-container {
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
  display: flex;
  align-items: center;
}

.favorites-list {
  min-height: 400px;
}

.favorite-item {
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 15px;
  margin-bottom: 15px;
  background-color: #ffffff;
  transition: all 0.3s;
}

.favorite-item:hover {
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.favorite-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.favorite-title {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
}

.title-text {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
}

.favorite-actions {
  display: flex;
  gap: 10px;
}

.favorite-content {
  color: #606266;
  line-height: 1.6;
  margin-bottom: 10px;
  max-height: 150px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.favorite-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: #909399;
}

.tags {
  display: flex;
  align-items: center;
  gap: 5px;
}

.editor-container {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  overflow: hidden;
}

.editor-toolbar {
  padding: 10px;
  background-color: #f5f7fa;
  border-bottom: 1px solid #dcdfe6;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
}

.editor-content {
  min-height: 300px;
  padding: 15px;
  outline: none;
  overflow-y: auto;
  line-height: 1.6;
  font-size: 14px;
}

.editor-content:focus {
  background-color: #ffffff;
}

.editor-content h1,
.editor-content h2,
.editor-content h3 {
  margin: 10px 0;
  font-weight: bold;
}

.editor-content ul,
.editor-content ol {
  margin: 10px 0;
  padding-left: 30px;
}

.editor-content pre {
  background-color: #f5f7fa;
  padding: 10px;
  border-radius: 4px;
  overflow-x: auto;
}

.editor-content blockquote {
  border-left: 4px solid #409eff;
  padding-left: 15px;
  margin: 10px 0;
  color: #606266;
}
</style>

