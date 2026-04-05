import { Link, Outlet, useNavigate, useRouterState } from '@tanstack/react-router'
import { Menu, MapPin, Search } from 'lucide-react'
import { useEffect, useRef, useState } from 'react'
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet'
import { Button } from '@/components/ui/button'
import { useAuthStore } from '@/store/authStore'
import { useMapSearchStore } from '@/store/mapSearchStore'
import { useKremlins } from '@/hooks/useKremlins'
import type { KremlinListItem } from '@/types/kremlin'

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

function SearchBar() {
  const [query, setQuery] = useState('')
  const [open, setOpen] = useState(false)
  const [activeIndex, setActiveIndex] = useState(-1)
  const inputRef = useRef<HTMLInputElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)
  const navigate = useNavigate()
  const { setPendingKremlin } = useMapSearchStore()
  const { data: kremlins } = useKremlins()

  const results: KremlinListItem[] =
    query.trim().length > 0 && kremlins
      ? kremlins.filter((k) => k.name.toLowerCase().includes(query.toLowerCase())).slice(0, 6)
      : []

  const resultsRef = useRef<KremlinListItem[]>([])
  resultsRef.current = results
  const activeIndexRef = useRef(-1)
  activeIndexRef.current = activeIndex

  useEffect(() => {
    setActiveIndex(results.length > 0 ? 0 : -1)
  }, [query]) // eslint-disable-line react-hooks/exhaustive-deps

  function selectResult(kremlin: KremlinListItem) {
    setPendingKremlin(kremlin)
    navigate({ to: '/' })
    setQuery(kremlin.name)
    setOpen(false)
    setActiveIndex(-1)
    inputRef.current?.blur()
  }

  useEffect(() => {
    const handleMouseDown = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setOpen(false)
      }
    }

    const handleKeyDown = (e: KeyboardEvent) => {
      const inInput = document.activeElement === inputRef.current

      if (
        e.key === '/' &&
        !inInput &&
        !(e.target instanceof HTMLInputElement) &&
        !(e.target instanceof HTMLTextAreaElement)
      ) {
        e.preventDefault()
        inputRef.current?.focus()
        setOpen(true)
        return
      }

      if (!inInput) return

      switch (e.key) {
        case 'Escape':
          setOpen(false)
          setActiveIndex(-1)
          inputRef.current?.blur()
          break
        case 'ArrowDown':
          e.preventDefault()
          setOpen(true)
          setActiveIndex((i) => (i < resultsRef.current.length - 1 ? i + 1 : 0))
          break
        case 'ArrowUp':
          e.preventDefault()
          setOpen(true)
          setActiveIndex((i) => (i > 0 ? i - 1 : resultsRef.current.length - 1))
          break
        case 'Enter':
          if (activeIndexRef.current >= 0 && resultsRef.current[activeIndexRef.current]) {
            e.preventDefault()
            selectResult(resultsRef.current[activeIndexRef.current])
          }
          break
      }
    }

    document.addEventListener('mousedown', handleMouseDown)
    document.addEventListener('keydown', handleKeyDown)
    return () => {
      document.removeEventListener('mousedown', handleMouseDown)
      document.removeEventListener('keydown', handleKeyDown)
    }
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <div ref={containerRef} className="relative w-full">
      <div className="flex items-center gap-2 rounded-lg border bg-background px-3 py-1.5 shadow-sm transition-shadow focus-within:shadow-md focus-within:ring-1 focus-within:ring-accent/40">
        <Search className="h-4 w-4 shrink-0 text-muted-foreground" />
        <input
          ref={inputRef}
          type="text"
          placeholder="Поиск кремля... (/)"
          value={query}
          onChange={(e) => {
            setQuery(e.target.value)
            setOpen(true)
          }}
          onFocus={() => setOpen(true)}
          className="w-full bg-transparent text-sm placeholder:text-muted-foreground outline-none"
        />
      </div>

      {open && results.length > 0 && (
        <ul className="absolute top-full left-0 right-0 mt-1 overflow-hidden rounded-lg border bg-background shadow-lg z-50">
          {results.map((kremlin, i) => (
            <li key={kremlin.id}>
              <button
                className={`w-full px-3 py-2.5 text-left text-sm transition-colors ${
                  i === activeIndex ? 'bg-accent/10 text-accent' : 'hover:bg-muted'
                }`}
                onMouseDown={(e) => e.preventDefault()}
                onMouseEnter={() => setActiveIndex(i)}
                onClick={() => selectResult(kremlin)}
              >
                <span className="font-medium">{kremlin.name}</span>
                {kremlin.city && (
                  <span className="ml-1.5 text-muted-foreground">{kremlin.city}</span>
                )}
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
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
        <div className="container mx-auto flex h-14 items-center gap-3 px-4">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2 font-semibold text-accent shrink-0">
            <MapPin className="h-5 w-5" />
            <span className="hidden sm:inline">Кремли России</span>
          </Link>

          {/* Search — desktop */}
          <div className="hidden md:block flex-1 max-w-sm">
            <SearchBar />
          </div>

          {/* Spacer — mobile */}
          <div className="flex-1 md:hidden" />

          {/* Desktop nav */}
          <nav className="hidden md:flex items-center gap-6 shrink-0">
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
