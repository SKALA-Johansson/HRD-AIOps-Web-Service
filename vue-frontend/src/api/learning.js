import api from '@/api/client.js'

export const learningApi = {
  myCurriculums() {
    return api.get('/learning/curriculums/me')
  },
  moduleContents(moduleId) {
    return api.get(`/learning/modules/${moduleId}/contents`)
  },
  submitAssignment(assignmentId, body) {
    return api.post(`/learning/assignments/${assignmentId}/submissions`, body)
  },
  myProgress() {
    return api.get('/learning/progress/me')
  }
}
