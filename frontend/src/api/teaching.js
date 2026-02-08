import api from './index'

export const teachingApi = {
  generateDesign(data) {
    return api.post('/teaching-design/generate', data)
  },
  getDesigns(skip = 0, limit = 20) {
    return api.get('/teaching-design/', { params: { skip, limit } })
  },
  getDesign(id) {
    return api.get(`/teaching-design/${id}`)
  },
  updateDesign(id, content) {
    return api.put(`/teaching-design/${id}`, content)
  },
  exportToWord(id) {
    return api.post(`/teaching-design/${id}/export-word`, {}, {
      responseType: 'blob'
    })
  },
  deleteDesign(id) {
    return api.delete(`/teaching-design/${id}`)
  }
}

