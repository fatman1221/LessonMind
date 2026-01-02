import api from './index'

export const chatApi = {
  sendMessage(message) {
    return api.post('/chat/', { message })
  },
  getHistory(limit = 20) {
    return api.get('/chat/history', { params: { limit } })
  }
}

