import api from '@/api/client.js'

export const curriculumsApi = {
  /** multipart: 필드 file(PDF) + 선택 company, jobFamily, title */
  generateFromPdf(formData) {
    return api.post('/curriculums/generate-from-pdf', formData, { timeout: 120000 })
  },
  generate(body) {
    return api.post('/curriculums/generate', body)
  },
  /** 예: { status: 'PENDING_APPROVAL' } — 게이트웨이 스펙에 맞게 조정 */
  list(params) {
    return api.get('/curriculums', { params })
  },
  get(curriculumId) {
    return api.get(`/curriculums/${curriculumId}`)
  },
  update(curriculumId, body) {
    return api.put(`/curriculums/${curriculumId}`, body)
  },
  remove(curriculumId) {
    return api.delete(`/curriculums/${curriculumId}`)
  }
}
