import api from '@/api/client.js'

export const tutorApi = {
  ask(body) {
    return api.post('/tutor/sessions', body, { timeout: 120000 })
  },
  requestGrading(submissionId) {
    return api.post(`/tutor/assignments/${submissionId}/grade`)
  },
  getFeedback(submissionId) {
    return api.get(`/tutor/feedback/${submissionId}`)
  },
  generateQuiz(body) {
    return api.post('/tutor/quizzes/generate', body, { timeout: 60000 })
  },
  submitQuiz(quizId, body) {
    return api.post(`/tutor/quizzes/${quizId}/submit`, body)
  },
  getWeeklyReports(userId, curriculumId) {
    const params = curriculumId ? { curriculum_id: curriculumId } : {}
    return api.get(`/tutor/reports/users/${userId}/weekly`, { params })
  }
}
