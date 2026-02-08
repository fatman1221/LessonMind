import api from './index'

// 创建收藏
export const createFavorite = (data) => {
  return api.post('/user/favorites', data)
}

// 获取所有收藏
export const getFavorites = (contentType = null) => {
  const params = contentType ? { content_type: contentType } : {}
  return api.get('/user/favorites', { params })
}

// 获取单个收藏
export const getFavorite = (id) => {
  return api.get(`/user/favorites/${id}`)
}

// 更新收藏
export const updateFavorite = (id, data) => {
  return api.put(`/user/favorites/${id}`, data)
}

// 删除收藏
export const deleteFavorite = (id) => {
  return api.delete(`/user/favorites/${id}`)
}

// 获取用户资料
export const getUserProfile = () => {
  return api.get('/user/profile')
}

