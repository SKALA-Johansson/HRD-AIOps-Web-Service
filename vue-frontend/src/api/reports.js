import api from '@/api/client.js'

export const reportsApi = {
  userReport(userId) {
    return api.get(`/reports/users/${userId}`)
  },
  dashboard(params) {
    return api.get('/reports/dashboard', { params })
  }
}
