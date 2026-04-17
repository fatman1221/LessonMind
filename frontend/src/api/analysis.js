import api from './index'

export const analysisApi = {
  createStudentData(data) {
    return api.post('/analysis/student-data', data)
  },
  analyzeStudent(studentId) {
    return api.post(`/analysis/analyze/${studentId}`)
  },
  trainModel() {
    return api.post('/analysis/train-model')
  },
  getClassOverview() {
    return api.get('/analysis/class-overview')
  },
  getTeachingReport() {
    return api.get('/analysis/teaching-report')
  },
  getStudentRecommendations(studentId) {
    return api.get(`/analysis/student-recommendations/${studentId}`)
  },
  getTeachingAlerts() {
    return api.get('/analysis/teaching-alerts')
  },
  getIgnoredTeachingAlerts() {
    return api.get('/analysis/teaching-alerts/ignored')
  },
  updateTeachingAlertState(alertKey, ignored = true) {
    return api.post('/analysis/teaching-alerts/state', { alert_key: alertKey, ignored })
  },
  clearIgnoredTeachingAlerts() {
    return api.delete('/analysis/teaching-alerts/ignored')
  },
  generateQuestions(data) {
    return api.post('/analysis/questions/generate', data)
  },
  getQuestions(params) {
    return api.get('/analysis/questions', { params })
  },
  exportQuestions(questionIds, format = 'json') {
    return api.post('/analysis/questions/export', { question_ids: questionIds, format })
  },
  exportQuestionsToWord(questionIds) {
    return api.post('/analysis/questions/export-word', questionIds, {
      responseType: 'blob'
    })
  },
  deleteQuestion(id) {
    return api.delete(`/analysis/questions/${id}`)
  },
  deleteQuestions(ids) {
    return api.post('/analysis/questions/delete-batch', ids)
  }
}

