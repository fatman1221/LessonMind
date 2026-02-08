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

