import api from '@/api/client.js'

export const tutorApi = {
  ask(body) {
    return api.post('/tutor/sessions', body)
  },
  requestGrading(submissionId) {
    return api.post(`/tutor/assignments/${submissionId}/grade`)
  },
  getFeedback(submissionId) {
    return api.get(`/tutor/feedback/${submissionId}`)
  }
}
