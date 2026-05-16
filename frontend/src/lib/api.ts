import ky from 'ky'
import { useAuthStore } from '../store/authStore'

// Защитный fallback: если VITE_API_URL не задан (или vite был не перезапущен),
// используем localhost:8001 — это удобный default для разработки.
const baseApi = (import.meta.env.VITE_API_URL as string) || 'http://localhost:8001'
const apiUrl = `${baseApi}/api`

export const api = ky.create({
  prefixUrl: apiUrl,
  headers: {
    'Content-Type': 'application/json',
  },
  hooks: {
    beforeRequest: [
      (request) => {
        const token = useAuthStore.getState().token
        if (token) {
          request.headers.set('Authorization', `Bearer ${token}`)
        }
      },
    ],
  },
})
