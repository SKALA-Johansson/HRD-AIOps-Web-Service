import api from '@/api/client.js'

export const profilesApi = {
  getMe() {
    return api.get('/profiles/me')
  },
  updateMe(body) {
    return api.put('/profiles/me', body)
  }
}
