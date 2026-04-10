import api from '@/api/client.js'

export const contentsApi = {
  create(body) {
    return api.post('/contents', body)
  },
  /** 부서별 필수 교육 자료(PDF) 업로드 — 백엔드 연결 전까지는 404일 수 있음 */
  uploadDepartmentRequiredPdf(formData) {
    return api.post('/contents/department-required-pdf', formData, { timeout: 120000 })
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
