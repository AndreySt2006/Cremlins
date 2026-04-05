import { createFileRoute, redirect, useNavigate } from '@tanstack/react-router'
import { LogOut } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useAuthStore } from '@/store/authStore'
import { useRoutesStore } from '@/store/routesStore'

export const Route = createFileRoute('/profile')({
  beforeLoad: () => {
    const { isAuthenticated } = useAuthStore.getState()
    if (!isAuthenticated) throw redirect({ to: '/auth' })
  },
  component: ProfilePage,
})

function formatRuDate(iso: string) {
  return new Date(iso).toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  })
}

function ProfilePage() {
  const { user, logout } = useAuthStore()
  const { visited, planned } = useRoutesStore()
  const navigate = useNavigate()

  if (!user) return null

  function handleLogout() {
    logout()
    navigate({ to: '/' })
  }

  const initial = user.username.charAt(0).toUpperCase()

  return (
    <div className="mx-auto max-w-lg px-4 py-10">
      {/* Avatar + name */}
      <div className="flex flex-col items-center gap-3 mb-8">
        {user.avatarUrl ? (
          <img
            src={user.avatarUrl}
            alt={user.username}
            className="h-20 w-20 rounded-full object-cover"
          />
        ) : (
          <div className="flex h-20 w-20 items-center justify-center rounded-full bg-accent text-white text-2xl font-semibold select-none">
            {initial}
          </div>
        )}
        <div className="text-center">
          <h2 className="text-xl font-semibold">{user.username}</h2>
          <p className="text-sm text-muted-foreground">{user.email}</p>
          <p className="mt-1 text-sm text-muted-foreground">
            На сайте с {formatRuDate(user.createdAt)}
          </p>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 gap-4 mb-8">
        <div className="rounded-xl border bg-card p-4 text-center shadow-sm">
          <p className="text-3xl font-bold text-accent">{visited.length}</p>
          <p className="mt-1 text-sm text-muted-foreground">Посещено кремлей</p>
        </div>
        <div className="rounded-xl border bg-card p-4 text-center shadow-sm">
          <p className="text-3xl font-bold text-accent">{planned.length}</p>
          <p className="mt-1 text-sm text-muted-foreground">Запланировано</p>
        </div>
      </div>

      {/* Logout */}
      <Button
        variant="destructive"
        className="w-full"
        onClick={handleLogout}
      >
        <LogOut className="mr-2 h-4 w-4" />
        Выйти
      </Button>
    </div>
  )
}
