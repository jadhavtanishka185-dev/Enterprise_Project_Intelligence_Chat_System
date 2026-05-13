import api from './api'

export const projectService = {
  list: async () => {
    const { data } = await api.get('/projects')
    return data
  },

  get: async (id) => {
    const { data } = await api.get(`/projects/${id}`)
    return data
  },

  create: async (name, description) => {
    const { data } = await api.post('/projects', { name, description })
    return data
  },

  delete: async (id) => {
    await api.delete(`/projects/${id}`)
  },
}
