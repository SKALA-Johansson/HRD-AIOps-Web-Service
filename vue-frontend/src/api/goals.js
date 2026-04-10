import api from '@/api/client.js'

export const goalsApi = {
  generate(body) {
    return api.post('/goals/generate', body)
  },
  get(goalId) {
    return api.get(`/goals/${goalId}`)
  },
  createHrGoal(body) {
    return api.post('/goals', body)
  }
}
