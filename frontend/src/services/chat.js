import api from './api'

export const chatService = {
  sendMessage: async (projectId, question) => {
    const { data } = await api.post(`/chat/${projectId}`, { question })
    return data
  },

  getHistory: async (projectId) => {
    const { data } = await api.get(`/chat/history/${projectId}`)
    return data
  },
}
