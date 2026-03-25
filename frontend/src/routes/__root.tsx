import { createRootRoute, useNavigate } from '@tanstack/react-router'
import { useEffect } from 'react'
import { Layout } from '@/components/Layout'
import { useAuthStore } from '@/store/authStore'
import { getMe } from '@/api/auth'

function RootComponent() {
  const { token, setAuth, logout } = useAuthStore()

  useEffect(() => {
    if (!token) return
    getMe()
      .then((user) => setAuth(user, token))
      .catch(() => logout())
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  return <Layout />
}

export const Route = createRootRoute({
  component: RootComponent,
})
