import api from '@/api/client.js'

export const contentsApi = {
  create(body) {
    return api.post('/contents', body)
  },
  list(params) {
    return api.get('/contents', { params })
  },
  update(contentId, body) {
    return api.put(`/contents/${contentId}`, body)
  },
  remove(contentId) {
    return api.delete(`/contents/${contentId}`)
  }
}
