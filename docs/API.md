# API文档

## 基础信息

- Base URL: `http://localhost:8000/api`
- 认证方式: Bearer Token (JWT)

## 认证接口

### 用户注册
```
POST /auth/register
Content-Type: application/json

{
  "username": "string",
  "email": "string",
  "password": "string"
}
```

### 用户登录
```
POST /auth/login
Content-Type: multipart/form-data

username: string
password: string
```

响应：
```json
{
  "access_token": "string",
  "token_type": "bearer"
}
```

### 获取当前用户信息
```
GET /auth/me
Authorization: Bearer {token}
```

## 聊天对话接口

### 发送消息
```
POST /chat/
Authorization: Bearer {token}
Content-Type: application/json

{
  "message": "string"
}
```

### 获取聊天历史
```
GET /chat/history?limit=20
Authorization: Bearer {token}
```

## 教学设计接口

### 生成教学设计
```
POST /teaching-design/generate
Authorization: Bearer {token}
Content-Type: application/json

{
  "subject": "数学",
  "grade": "初中",
  "topic": "一次函数的图像与性质",
  "teaching_objectives": "理解一次函数的概念..."
}
```

### 获取教学设计列表
```
GET /teaching-design/?skip=0&limit=20
Authorization: Bearer {token}
```

### 获取单个教学设计
```
GET /teaching-design/{id}
Authorization: Bearer {token}
```

### 更新教学设计
```
PUT /teaching-design/{id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "content": {...}
}
```

### 导出Word文档
```
POST /teaching-design/{id}/export-word
Authorization: Bearer {token}
```

## 多媒体资源接口

### 生成图片
```
POST /multimedia/image
Authorization: Bearer {token}
Content-Type: application/json

{
  "knowledge_point": "一次函数",
  "subject": "数学",
  "teaching_design_id": 1
}
```

### 生成PPT
```
POST /multimedia/ppt
Authorization: Bearer {token}
Content-Type: application/json

{
  "teaching_design_id": 1,
  "style": "default"
}
```

### 获取资源列表
```
GET /multimedia/resources/{teaching_design_id}
Authorization: Bearer {token}
```

## 学情分析接口

### 导入学生数据
```
POST /analysis/student-data
Authorization: Bearer {token}
Content-Type: application/json

{
  "student_id": "string",
  "student_name": "string",
  "subject": "数学",
  "grade": "初中",
  "homework_scores": {"作业1": 85, "作业2": 90},
  "learning_behavior": {"study_time": 10, "question_count": 5},
  "knowledge_mastery": {"知识点1": 0.85}
}
```

### 分析学生学情
```
POST /analysis/analyze/{student_id}
Authorization: Bearer {token}
```

### 训练分析模型
```
POST /analysis/train-model
Authorization: Bearer {token}
```

### 生成题目
```
POST /analysis/questions/generate
Authorization: Bearer {token}
Content-Type: application/json

{
  "knowledge_point": "一次函数",
  "subject": "数学",
  "question_types": ["choice", "fill"],
  "count": 3
}
```

### 获取题目列表
```
GET /analysis/questions?subject=数学&knowledge_point=一次函数
Authorization: Bearer {token}
```

### 导出题目
```
POST /analysis/questions/export
Authorization: Bearer {token}
Content-Type: application/json

{
  "question_ids": [1, 2, 3],
  "format": "json"
}
```

## 错误响应格式

```json
{
  "detail": "错误信息"
}
```

常见错误码：
- 400: 请求参数错误
- 401: 未授权
- 404: 资源不存在
- 500: 服务器内部错误

