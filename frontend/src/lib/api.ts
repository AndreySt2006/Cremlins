import ky from 'ky'
import { useAuthStore } from '../store/authStore'

const apiUrl = `${import.meta.env.VITE_API_URL as string}/api`

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
