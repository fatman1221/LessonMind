import api from './index'

// 获取所有用户
export const getAllUsers = (params = {}) => {
  return api.get('/admin/users', { params })
}

// 获取单个用户
export const getUser = (id) => {
  return api.get(`/admin/users/${id}`)
}

// 创建用户
export const createUser = (data) => {
  return api.post('/admin/users', data)
}

// 更新用户
export const updateUser = (id, data) => {
  return api.put(`/admin/users/${id}`, data)
}

// 删除用户
export const deleteUser = (id) => {
  return api.delete(`/admin/users/${id}`)
}

// 获取用户统计
export const getUserStats = () => {
  return api.get('/admin/stats')
}
