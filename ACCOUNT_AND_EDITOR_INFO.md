# 账号密码、SQL脚本和在线编辑器说明

## 1. 📝 账号密码信息

### 默认管理员账号

**位置**: `backend/init_admin.py`

**默认账号信息**:
- **用户名**: `admin`
- **密码**: `admin123`
- **邮箱**: `admin@example.com`
- **角色**: `admin`

### 创建管理员账号的方法

```bash
# 进入后端目录
cd backend

# 运行初始化脚本
python init_admin.py
```

**输出示例**:
```
✅ 默认管理员账号创建成功！
========================================
   用户名: admin
   密码: admin123
   邮箱: admin@example.com
========================================
⚠️  请登录后立即修改密码！
```

### 普通用户注册

普通用户可以通过前端注册页面注册，默认角色为 `teacher`。

**注册位置**: 前端登录页面 -> 注册标签页

---

## 2. 📊 SQL脚本位置

### 现有SQL脚本

**位置**: `database/init.sql`

**内容**: 仅包含数据库创建语句
```sql
-- 创建数据库
CREATE DATABASE IF NOT EXISTS teacher_prep_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE teacher_prep_system;

-- 注意：表结构将由SQLAlchemy自动创建，此文件仅作为参考
```

### 新增表的SQL脚本

**重要说明**: 本项目使用 **SQLAlchemy ORM** 自动创建表结构，不需要手动编写SQL脚本。

**新增的 `user_favorites` 表** 会在以下情况自动创建：

1. **首次启动后端服务时**
   - 位置: `backend/main.py` 第11行
   - 代码: `Base.metadata.create_all(bind=engine)`
   - 这会自动创建所有在 `models.py` 中定义的表

2. **手动创建表结构SQL脚本**（可选）

如果需要手动创建 `user_favorites` 表，可以使用以下SQL：

```sql
-- 创建用户收藏表
CREATE TABLE IF NOT EXISTS `user_favorites` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `user_id` INT NOT NULL,
  `title` VARCHAR(200) NOT NULL,
  `content_type` VARCHAR(50) NOT NULL,
  `content` TEXT NOT NULL,
  `tags` VARCHAR(500) NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  INDEX `idx_user_id` (`user_id`),
  CONSTRAINT `fk_user_favorites_user` 
    FOREIGN KEY (`user_id`) 
    REFERENCES `users` (`id`) 
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

**表结构说明**:
- `id`: 主键，自增
- `user_id`: 用户ID，外键关联 `users` 表
- `title`: 收藏标题
- `content_type`: 内容类型（teaching_design, chat, question, custom）
- `content`: 收藏内容（支持HTML富文本）
- `tags`: 标签（逗号分隔）
- `created_at`: 创建时间
- `updated_at`: 更新时间

### 数据库初始化

**自动方式**（推荐）:
```bash
# 启动后端服务，会自动创建所有表
cd backend
python main.py
```

**手动方式**:
1. 先创建数据库（使用 `database/init.sql`）
2. 配置数据库连接（`backend/config.py` 或 `.env` 文件）
3. 启动后端服务，SQLAlchemy会自动创建表结构

---

## 3. ✏️ 在线编辑器实现方案

### 技术方案

**实现方式**: 基于 HTML5 `contenteditable` 属性 + JavaScript Document.execCommand API

**位置**: `frontend/src/views/UserManagement.vue`

### 核心实现代码

#### 1. HTML结构

```vue
<div class="editor-container">
  <!-- 工具栏 -->
  <div class="editor-toolbar">
    <!-- 格式化按钮：粗体、斜体、下划线 -->
    <el-button-group>
      <el-button @click="formatText('bold')">
        <el-icon><Bold /></el-icon>
      </el-button>
      <!-- ... 其他按钮 -->
    </el-button-group>
  </div>
  
  <!-- 可编辑内容区 -->
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
```

**关键点**:
- `contenteditable="true"`: 使div可编辑
- `v-html`: 绑定HTML内容
- `@input`: 监听内容变化

#### 2. 格式化文本功能

```javascript
const formatText = (command) => {
  if (!editorRef.value) return
  editorRef.value.focus()  // 聚焦编辑器
  document.execCommand(command, false, null)  // 执行格式化命令
  updateEditorState()  // 更新工具栏状态
  handleEditorInput()  // 同步内容
}
```

**支持的格式化命令**:
- `bold`: 粗体
- `italic`: 斜体
- `underline`: 下划线

#### 3. 插入结构化内容

```javascript
const insertText = (type) => {
  if (!editorRef.value) return
  editorRef.value.focus()
  const selection = window.getSelection()  // 获取选中区域
  const range = selection.getRangeAt(0)
  
  let text = ''
  switch (type) {
    case 'h1': text = '<h1>标题1</h1>'; break
    case 'h2': text = '<h2>标题2</h2>'; break
    case 'h3': text = '<h3>标题3</h3>'; break
    case 'ul': text = '<ul><li>列表项</li></ul>'; break
    case 'ol': text = '<ol><li>列表项</li></ol>'; break
    case 'code': text = '<pre><code>代码块</code></pre>'; break
    case 'quote': text = '<blockquote>引用内容</blockquote>'; break
  }
  
  range.deleteContents()  // 删除选中内容
  const div = document.createElement('div')
  div.innerHTML = text
  const fragment = document.createDocumentFragment()
  while (div.firstChild) {
    fragment.appendChild(div.firstChild)
  }
  range.insertNode(fragment)  // 插入新内容
  handleEditorInput()
}
```

#### 4. 内容同步

```javascript
const handleEditorInput = () => {
  if (editorRef.value) {
    formData.content = editorRef.value.innerHTML  // 获取HTML内容
    updateEditorState()  // 更新工具栏按钮状态
  }
}
```

#### 5. 工具栏状态更新

```javascript
const updateEditorState = () => {
  if (!editorRef.value) return
  const selection = window.getSelection()
  if (selection.rangeCount > 0) {
    // 检查当前选中文本的格式状态
    editorState.bold = document.queryCommandState('bold')
    editorState.italic = document.queryCommandState('italic')
    editorState.underline = document.queryCommandState('underline')
  }
}
```

### 编辑器功能列表

✅ **已实现的功能**:
1. 文本格式化：粗体、斜体、下划线
2. 标题：H1、H2、H3
3. 列表：有序列表、无序列表
4. 代码块：`<pre><code>`
5. 引用：`<blockquote>`
6. 实时预览：所见即所得
7. 工具栏状态：按钮高亮显示当前格式

### 编辑器样式

**位置**: `frontend/src/views/UserManagement.vue` 第520-601行

```css
.editor-container {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  overflow: hidden;
}

.editor-toolbar {
  padding: 10px;
  background-color: #f5f7fa;
  border-bottom: 1px solid #dcdfe6;
}

.editor-content {
  min-height: 300px;
  padding: 15px;
  outline: none;
  overflow-y: auto;
  line-height: 1.6;
}
```

### 数据保存

**保存流程**:
1. 用户编辑内容
2. `@input` 事件触发 `handleEditorInput()`
3. 内容同步到 `formData.content`
4. 点击保存按钮
5. 获取 `editorRef.value.innerHTML`（HTML格式）
6. 发送到后端API保存

**代码位置**: `UserManagement.vue` 第319-350行

```javascript
const handleSubmit = async () => {
  // ...
  const content = editorRef.value?.innerHTML || formData.content
  const submitData = {
    title: formData.title,
    content_type: formData.content_type,
    content: content,  // HTML格式的内容
    tags: formData.tags || null
  }
  // 发送到后端...
}
```

### 技术特点

1. **轻量级**: 不需要引入第三方编辑器库（如Quill、TinyMCE等）
2. **原生实现**: 使用浏览器原生API
3. **响应式**: 实时更新工具栏状态
4. **HTML存储**: 内容以HTML格式存储，支持富文本显示

### 扩展建议

如果需要更强大的编辑器功能，可以考虑：

1. **集成第三方编辑器**:
   - Quill.js
   - TinyMCE
   - CKEditor
   - Monaco Editor（代码编辑）

2. **增强当前编辑器**:
   - 添加图片上传
   - 添加链接插入
   - 添加表格支持
   - 添加撤销/重做功能

---

## 📍 文件位置总结

### 账号相关
- **管理员初始化**: `backend/init_admin.py`
- **用户模型**: `backend/models.py` (User类)
- **认证API**: `backend/api/auth.py`

### SQL相关
- **数据库初始化**: `database/init.sql`
- **表结构定义**: `backend/models.py` (所有Model类)
- **自动创建表**: `backend/main.py` 第11行

### 编辑器相关
- **编辑器组件**: `frontend/src/views/UserManagement.vue`
- **编辑器样式**: 同文件，第520-601行
- **编辑器逻辑**: 同文件，第352-427行

---

## 🚀 快速开始

### 1. 创建管理员账号
```bash
cd backend
python init_admin.py
```

### 2. 启动服务
```bash
# 后端
cd backend
python main.py

# 前端
cd frontend
npm run dev
```

### 3. 登录系统
- 访问前端地址（通常是 http://localhost:5173）
- 使用 `admin` / `admin123` 登录
- 进入"我的收藏"页面使用在线编辑器

---

## ⚠️ 注意事项

1. **密码安全**: 生产环境请立即修改默认管理员密码
2. **数据库**: 确保MySQL服务已启动，数据库已创建
3. **编辑器**: 当前编辑器为轻量级实现，如需更强大功能可考虑集成第三方库
4. **HTML安全**: 存储的HTML内容在显示时需要注意XSS防护（当前使用 `v-html`，生产环境建议做HTML清理）

