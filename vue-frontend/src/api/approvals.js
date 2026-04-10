import api from '@/api/client.js'

export const approvalsApi = {
  approveGoal(goalId, body) {
    return api.post(`/approvals/goals/${goalId}`, body)
  },
  approveCurriculum(curriculumId, body) {
    return api.post(`/approvals/curriculums/${curriculumId}`, body)
  },
  list(params) {
    return api.get('/approvals', { params })
  }
}
