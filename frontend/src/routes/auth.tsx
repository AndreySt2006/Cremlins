import { createFileRoute, redirect, useNavigate } from '@tanstack/react-router'
import { useState } from 'react'
import { Loader2 } from 'lucide-react'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Button } from '@/components/ui/button'
import { useAuthStore } from '@/store/authStore'
import { login, register } from '@/api/auth'
import type { User } from '@/types'

export const Route = createFileRoute('/auth')({
  beforeLoad: () => {
    const { isAuthenticated } = useAuthStore.getState()
    if (isAuthenticated) throw redirect({ to: '/' })
  },
  component: AuthPage,
})

function AuthPage() {
  const { setAuth } = useAuthStore()
  const navigate = useNavigate()

  return (
    <div className="flex min-h-[calc(100vh-56px)] items-center justify-center p-4">
      <div className="w-full max-w-[400px] rounded-xl border bg-card p-6 shadow-sm">
        <h1 className="mb-6 text-center text-xl font-semibold">Добро пожаловать</h1>
        <Tabs defaultValue="login">
          <TabsList className="mb-6 grid w-full grid-cols-2">
            <TabsTrigger value="login">Вход</TabsTrigger>
            <TabsTrigger value="register">Регистрация</TabsTrigger>
          </TabsList>
          <TabsContent value="login">
            <LoginForm setAuth={setAuth} onSuccess={() => navigate({ to: '/' })} />
          </TabsContent>
          <TabsContent value="register">
            <RegisterForm setAuth={setAuth} onSuccess={() => navigate({ to: '/' })} />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}

type SetAuth = (user: User, token: string) => void

function LoginForm({ setAuth, onSuccess }: { setAuth: SetAuth; onSuccess: () => void }) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const { user, accessToken } = await login(email, password)
      setAuth(user, accessToken)
      onSuccess()
    } catch {
      setError('Неверный email или пароль')
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4">
      <div className="flex flex-col gap-1.5">
        <label htmlFor="login-email" className="text-sm font-medium">
          Email
        </label>
        <input
          id="login-email"
          type="email"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="rounded-md border bg-background px-3 py-2 text-sm outline-none ring-offset-background focus:ring-2 focus:ring-accent focus:ring-offset-2"
          placeholder="you@example.com"
        />
      </div>
      <div className="flex flex-col gap-1.5">
        <label htmlFor="login-password" className="text-sm font-medium">
          Пароль
        </label>
        <input
          id="login-password"
          type="password"
          required
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="rounded-md border bg-background px-3 py-2 text-sm outline-none ring-offset-background focus:ring-2 focus:ring-accent focus:ring-offset-2"
          placeholder="••••••••"
        />
      </div>
      {error && <p className="text-sm text-red-600">{error}</p>}
      <Button type="submit" disabled={loading} className="w-full bg-accent hover:bg-accent/90 text-accent-foreground">
        {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
        Войти
      </Button>
    </form>
  )
}

function RegisterForm({ setAuth, onSuccess }: { setAuth: SetAuth; onSuccess: () => void }) {
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const { user, accessToken } = await register(username, email, password)
      setAuth(user, accessToken)
      onSuccess()
    } catch {
      setError('Email уже занят или данные некорректны')
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4">
      <div className="flex flex-col gap-1.5">
        <label htmlFor="reg-username" className="text-sm font-medium">
          Имя пользователя
        </label>
        <input
          id="reg-username"
          type="text"
          required
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          className="rounded-md border bg-background px-3 py-2 text-sm outline-none ring-offset-background focus:ring-2 focus:ring-accent focus:ring-offset-2"
          placeholder="ivan_petrov"
        />
      </div>
      <div className="flex flex-col gap-1.5">
        <label htmlFor="reg-email" className="text-sm font-medium">
          Email
        </label>
        <input
          id="reg-email"
          type="email"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="rounded-md border bg-background px-3 py-2 text-sm outline-none ring-offset-background focus:ring-2 focus:ring-accent focus:ring-offset-2"
          placeholder="you@example.com"
        />
      </div>
      <div className="flex flex-col gap-1.5">
        <label htmlFor="reg-password" className="text-sm font-medium">
          Пароль
        </label>
        <input
          id="reg-password"
          type="password"
          required
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="rounded-md border bg-background px-3 py-2 text-sm outline-none ring-offset-background focus:ring-2 focus:ring-accent focus:ring-offset-2"
          placeholder="••••••••"
        />
      </div>
      {error && <p className="text-sm text-red-600">{error}</p>}
      <Button type="submit" disabled={loading} className="w-full bg-accent hover:bg-accent/90 text-accent-foreground">
        {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
        Зарегистрироваться
      </Button>
    </form>
  )
}
