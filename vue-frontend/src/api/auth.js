import api from '@/api/client.js'

export const authApi = {
  signup(body) {
    return api.post('/auth/signup', body)
  },
  login(body) {
    return api.post('/auth/login', body)
  }
}
