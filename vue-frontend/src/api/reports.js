import api from '@/api/client.js'

export const reportsApi = {
  /** HR: 수강 중인 신입 목록(서버 지원 시) */
  users(params) {
    return api.get('/reports/users', { params })
  },
  userReport(userId) {
    return api.get(`/reports/users/${userId}`)
  },
  dashboard(params) {
    return api.get('/reports/dashboard', { params })
  }
}
