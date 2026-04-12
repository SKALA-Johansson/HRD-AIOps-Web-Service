import api from '@/api/client.js'

export const profilesApi = {
  /** multipart: name, username, department, birthDate, file */
  register(formData) {
    return api.post('/profiles/register', formData, { timeout: 60000 })
  },
  getMe() {
    return api.get('/profiles/me')
  },
  updateMe(body) {
    return api.put('/profiles/me', body)
  }
}
