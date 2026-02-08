import api from './index'

export const multimediaApi = {
  generateImage(data) {
    return api.post('/multimedia/image', data)
  },
  generatePPT(data) {
    return api.post('/multimedia/ppt', data)
  },
  getResources(teachingDesignId) {
    return api.get(`/multimedia/resources/${teachingDesignId}`)
  },
  getAllPPTs(skip = 0, limit = 100) {
    return api.get('/multimedia/ppt/list', { params: { skip, limit } })
  },
  downloadPPT(resourceId) {
    return api.get(`/multimedia/ppt/download/${resourceId}`, {
      responseType: 'blob'
    })
  },
  deletePPT(resourceId) {
    return api.delete(`/multimedia/resources/${resourceId}`)
  }
}

