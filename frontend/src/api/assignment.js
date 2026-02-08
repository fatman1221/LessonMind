import api from './index'

// 创建作业
export const createAssignment = (data) => {
  return api.post('/assignments', data)
}

// 发布作业
export const publishAssignment = (id) => {
  return api.post(`/assignments/${id}/publish`)
}

// 获取作业列表
export const getAssignments = (classId = null) => {
  const params = classId ? { class_id: classId } : {}
  return api.get('/assignments', { params })
}

// 获取作业详情
export const getAssignment = (id) => {
  return api.get(`/assignments/${id}`)
}

// 提交作业
export const submitAssignment = (id, answers) => {
  return api.post(`/assignments/${id}/submit`, { answers })
}

// 获取作业提交列表（教师）
export const getSubmissions = (assignmentId) => {
  return api.get(`/assignments/${assignmentId}/submissions`)
}

// 获取我的提交（学生）
export const getMySubmission = (assignmentId) => {
  return api.get(`/assignments/${assignmentId}/my-submission`)
}

