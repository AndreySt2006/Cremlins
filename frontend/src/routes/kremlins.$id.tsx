import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/kremlins/$id')({
  component: KremlinDetailPage,
})

function KremlinDetailPage() {
  const { id } = Route.useParams()
  return (
    <div className="container mx-auto p-8">
      <h1 className="text-2xl font-semibold">Кремль #{id}</h1>
    </div>
  )
}
