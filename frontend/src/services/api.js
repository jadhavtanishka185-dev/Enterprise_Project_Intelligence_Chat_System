// import axios from 'axios'

// const api = axios.create({
//   baseURL: '/api',
//   timeout: 60000,
// })

// // Attach token on every request
// api.interceptors.request.use((config) => {
//   const token = localStorage.getItem('token')
//   if (token) {
//     config.headers.Authorization = `Bearer ${token}`
//   }
//   return config
// })

// // Handle 401 globally
// api.interceptors.response.use(
//   (response) => response,
//   (error) => {
//     if (error.response?.status === 401) {
//       localStorage.removeItem('token')
//       localStorage.removeItem('user')
//       window.location.href = '/login'
//     }
//     return Promise.reject(error)
//   }
// )

// export default api



import axios from 'axios'

// FastAPI Backend URL
const API_BASE_URL = 'http://127.0.0.1:8000'

// Create Axios Instance
const api = axios.create({
baseURL: API_BASE_URL,
timeout: 60000,

headers: {
'Content-Type': 'application/json',
},
})

// ==============================
// REQUEST INTERCEPTOR
// Attach JWT token automatically
// ==============================
api.interceptors.request.use(
(config) => {
const token = localStorage.getItem('token')


if (token) {
  config.headers.Authorization = `Bearer ${token}`
}

return config


},

(error) => {
return Promise.reject(error)
}
)

// ==============================
// RESPONSE INTERCEPTOR
// Handle Unauthorized Errors
// ==============================
api.interceptors.response.use(
(response) => {
return response
},

(error) => {
// Unauthorized
if (error.response?.status === 401) {
console.log('Unauthorized. Redirecting to login...')


  // Clear local storage
  localStorage.removeItem('token')
  localStorage.removeItem('user')

  // Redirect to login page
  window.location.href = '/login'
}

// Optional: Handle Server Errors
if (error.response?.status === 500) {
  console.error('Internal Server Error')
}

return Promise.reject(error)


}
)

export default api

