import api from './index'

// 创建班级
export const createClass = (data) => {
  return api.post('/classes', data)
}

// 获取班级列表
export const getClasses = () => {
  return api.get('/classes')
}

// 获取班级详情
export const getClass = (id) => {
  return api.get(`/classes/${id}`)
}

// 更新班级
export const updateClass = (id, data) => {
  return api.put(`/classes/${id}`, data)
}

// 删除班级
export const deleteClass = (id) => {
  return api.delete(`/classes/${id}`)
}

// 添加学生到班级
export const addStudents = (classId, studentIds) => {
  return api.post(`/classes/${classId}/students`, { student_ids: studentIds })
}

// 从班级移除学生
export const removeStudent = (classId, studentId) => {
  return api.delete(`/classes/${classId}/students/${studentId}`)
}

// 获取班级学生列表
export const getClassStudents = (classId) => {
  return api.get(`/classes/${classId}/students`)
}

// 获取可用的学生列表（教师和管理员）
export const getAvailableStudents = () => {
  return api.get('/students/available')
}

