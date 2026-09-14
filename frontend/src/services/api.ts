import axios from 'axios'

// In dev, default to /api so Vite proxies to Flask (see vite.config.ts).
const API_URL =
  import.meta.env.VITE_API_URL ||
  (import.meta.env.DEV ? '/api' : 'http://localhost:5000/api')

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 15000,
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.code === 'ERR_NETWORK' || !error.response) {
      return Promise.reject(
        new Error(
          'Cannot reach the API server. Start the Flask backend with: cd backend && python run.py',
        ),
      )
    }
    const message =
      error.response?.data?.error ||
      error.message ||
      'An unexpected error occurred'
    return Promise.reject(new Error(message))
  },
)

export default api
