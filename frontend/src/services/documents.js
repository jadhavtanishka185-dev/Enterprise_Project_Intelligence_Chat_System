import api from './api'

export const documentService = {
  list: async (projectId) => {
    const { data } = await api.get(`/projects/${projectId}/documents`)
    return data
  },

  upload: async (projectId, file, onProgress) => {
    const formData = new FormData()
    formData.append('file', file)
    const { data } = await api.post(`/projects/${projectId}/upload`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (e) => {
        if (onProgress && e.total) {
          onProgress(Math.round((e.loaded * 100) / e.total))
        }
      },
    })
    return data
  },
}
