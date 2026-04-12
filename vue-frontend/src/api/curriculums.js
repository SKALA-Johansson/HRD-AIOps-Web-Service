import api from '@/api/client.js'

export const curriculumsApi = {
  /** multipart: 필드 file(PDF) + 선택 name, employeeNo, department, title */
  generateFromPdf(formData) {
    return api.post('/curriculums/generate-from-pdf', formData, { timeout: 120000 })
  },
  generate(body) {
    return api.post('/curriculums/generate', body)
  },
  list(params) {
    return api.get('/curriculums', { params })
  },
  get(curriculumId) {
    return api.get(`/curriculums/${curriculumId}`)
  },
  /** action: 'APPROVE' | 'REJECT', comment: string */
  approve(curriculumId, body) {
    return api.post(`/curriculums/${curriculumId}/approve`, body)
  },
  update(curriculumId, body) {
    return api.put(`/curriculums/${curriculumId}`, body)
  },
  remove(curriculumId) {
    return api.delete(`/curriculums/${curriculumId}`)
  },
  getModule(moduleId) {
    return api.get(`/curriculums/modules/${moduleId}`)
  }
}
