import { createFileRoute, useNavigate } from '@tanstack/react-router'
import { X, Map } from 'lucide-react'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { useKremlins } from '@/hooks/useKremlins'
import { useRoutesStore } from '@/store/routesStore'
import type { KremlinListItem } from '@/types'

export const Route = createFileRoute('/routes')({
  component: RoutesPage,
})

function RoutesPage() {
  const { data: kremlins = [], isLoading } = useKremlins()
  const { planned, visited, togglePlanned, toggleVisited } = useRoutesStore()

  const plannedKremlins = kremlins.filter((k) => planned.includes(k.id))
  const visitedKremlins = kremlins.filter((k) => visited.includes(k.id))

  return (
    <div className="container mx-auto max-w-2xl px-4 py-8">
      <h1 className="mb-6 text-2xl font-bold text-gray-900">Мои маршруты</h1>

      <Tabs defaultValue="planned">
        <TabsList className="mb-6 w-full">
          <TabsTrigger value="planned" className="flex-1">
            Планирую посетить
            {plannedKremlins.length > 0 && (
              <span className="ml-2 rounded-full bg-red-100 px-2 py-0.5 text-xs font-medium text-red-700">
                {plannedKremlins.length}
              </span>
            )}
          </TabsTrigger>
          <TabsTrigger value="visited" className="flex-1">
            Уже посетил
            {visitedKremlins.length > 0 && (
              <span className="ml-2 rounded-full bg-red-100 px-2 py-0.5 text-xs font-medium text-red-700">
                {visitedKremlins.length}
              </span>
            )}
          </TabsTrigger>
        </TabsList>

        <TabsContent value="planned">
          <KremlinList
            items={plannedKremlins}
            isLoading={isLoading}
            onRemove={togglePlanned}
            emptyText="Нет кремлей для посещения"
          />
        </TabsContent>

        <TabsContent value="visited">
          <KremlinList
            items={visitedKremlins}
            isLoading={isLoading}
            onRemove={toggleVisited}
            emptyText="Нет посещённых кремлей"
          />
        </TabsContent>
      </Tabs>
    </div>
  )
}

// ---------------------------------------------------------------------------
// KremlinList
// ---------------------------------------------------------------------------

interface KremlinListProps {
  items: KremlinListItem[]
  isLoading: boolean
  onRemove: (id: number) => void
  emptyText: string
}

function KremlinList({ items, isLoading, onRemove, emptyText }: KremlinListProps) {
  if (isLoading) return <ListSkeleton />
  if (items.length === 0) return <EmptyState text={emptyText} />

  return (
    <ul className="space-y-3">
      {items.map((kremlin) => (
        <KremlinCard key={kremlin.id} kremlin={kremlin} onRemove={onRemove} />
      ))}
    </ul>
  )
}

// ---------------------------------------------------------------------------
// KremlinCard
// ---------------------------------------------------------------------------

function KremlinCard({
  kremlin,
  onRemove,
}: {
  kremlin: KremlinListItem
  onRemove: (id: number) => void
}) {
  const navigate = useNavigate()

  return (
    <li className="flex items-center gap-4 rounded-xl border border-gray-100 bg-white p-3 shadow-sm transition-shadow hover:shadow-md">
      {/* Превью */}
      <button
        onClick={() => navigate({ to: '/kremlins/$kremlinId', params: { kremlinId: String(kremlin.id) } })}
        className="shrink-0 overflow-hidden rounded-lg"
      >
        {kremlin.previewImageUrl ? (
          <img
            src={kremlin.previewImageUrl}
            alt={kremlin.name}
            className="h-20 w-20 object-cover"
          />
        ) : (
          <div className="flex h-20 w-20 items-center justify-center bg-gray-100 text-xs text-gray-400">
            Нет фото
          </div>
        )}
      </button>

      {/* Информация */}
      <button
        onClick={() => navigate({ to: '/kremlins/$kremlinId', params: { kremlinId: String(kremlin.id) } })}
        className="min-w-0 flex-1 text-left"
      >
        <p className="truncate font-semibold text-gray-900">{kremlin.name}</p>
        {kremlin.city && (
          <p className="mt-0.5 truncate text-sm text-gray-500">{kremlin.city}</p>
        )}
      </button>

      {/* Удалить */}
      <button
        onClick={() => onRemove(kremlin.id)}
        title="Убрать из списка"
        className="shrink-0 rounded-lg p-2 text-gray-400 transition-colors hover:bg-red-50 hover:text-red-600"
      >
        <X className="h-4 w-4" />
      </button>
    </li>
  )
}

// ---------------------------------------------------------------------------
// EmptyState
// ---------------------------------------------------------------------------

function EmptyState({ text }: { text: string }) {
  const navigate = useNavigate()

  return (
    <div className="flex flex-col items-center py-16 text-center">
      {/* Иллюстрация */}
      <div className="mb-4 flex h-24 w-24 items-center justify-center rounded-full bg-gray-100">
        <Map className="h-10 w-10 text-gray-300" />
      </div>
      <p className="mb-1 text-base font-medium text-gray-700">Пока ничего нет</p>
      <p className="mb-6 text-sm text-gray-400">{text}</p>
      <button
        onClick={() => navigate({ to: '/' })}
        className="inline-flex items-center gap-2 rounded-lg bg-red-600 px-5 py-2.5 text-sm font-medium text-white transition-colors hover:bg-red-700"
      >
        <Map className="h-4 w-4" />
        Открыть карту
      </button>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Skeleton
// ---------------------------------------------------------------------------

function ListSkeleton() {
  return (
    <ul className="space-y-3 animate-pulse">
      {[1, 2, 3].map((i) => (
        <li key={i} className="flex items-center gap-4 rounded-xl border border-gray-100 p-3">
          <div className="h-20 w-20 shrink-0 rounded-lg bg-gray-200" />
          <div className="flex-1 space-y-2">
            <div className="h-4 w-2/3 rounded bg-gray-200" />
            <div className="h-3 w-1/3 rounded bg-gray-200" />
          </div>
          <div className="h-8 w-8 rounded-lg bg-gray-200" />
        </li>
      ))}
    </ul>
  )
}
