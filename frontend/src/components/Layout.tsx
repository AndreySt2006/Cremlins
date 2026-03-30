import { Link, Outlet, useRouterState } from '@tanstack/react-router'
import { Menu, MapPin } from 'lucide-react'
import { useState } from 'react'
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet'
import { Button } from '@/components/ui/button'
import { useAuthStore } from '@/store/authStore'

const baseNavLinks = [
  { to: '/' as const, label: 'Карта' },
  { to: '/routes' as const, label: 'Маршруты' },
]

function NavLink({
  to,
  label,
  onClick,
}: {
  to: string
  label: string
  onClick?: () => void
}) {
  const pathname = useRouterState({ select: (s) => s.location.pathname })
  const isActive = to === '/' ? pathname === '/' : pathname.startsWith(to)
  return (
    <Link
      to={to}
      onClick={onClick}
      className={`text-sm font-medium transition-colors hover:text-accent ${
        isActive ? 'text-accent' : 'text-foreground/70'
      }`}
    >
      {label}
    </Link>
  )
}

export function Layout() {
  const [mobileOpen, setMobileOpen] = useState(false)
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated)

  const navLinks = [
    ...baseNavLinks,
    isAuthenticated
      ? { to: '/profile' as const, label: 'Профиль' }
      : { to: '/auth' as const, label: 'Войти' },
  ]

  return (
    <div className="min-h-screen flex flex-col">
      <header className="sticky top-0 z-40 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container mx-auto flex h-14 items-center justify-between px-4">
          <Link to="/" className="flex items-center gap-2 font-semibold text-accent">
            <MapPin className="h-5 w-5" />
            <span>Кремли России</span>
          </Link>

          {/* Desktop nav */}
          <nav className="hidden md:flex items-center gap-6">
            {navLinks.map((link) => (
              <NavLink key={link.to} {...link} />
            ))}
          </nav>

          {/* Mobile hamburger */}
          <Sheet open={mobileOpen} onOpenChange={setMobileOpen}>
            <SheetTrigger asChild>
              <Button variant="ghost" size="icon" className="md:hidden">
                <Menu className="h-5 w-5" />
                <span className="sr-only">Меню</span>
              </Button>
            </SheetTrigger>
            <SheetContent side="right" className="w-64">
              <nav className="flex flex-col gap-4 pt-6">
                {navLinks.map((link) => (
                  <NavLink
                    key={link.to}
                    {...link}
                    onClick={() => setMobileOpen(false)}
                  />
                ))}
              </nav>
            </SheetContent>
          </Sheet>
        </div>
      </header>

      <main className="flex-1">
        <Outlet />
      </main>
    </div>
  )
}
