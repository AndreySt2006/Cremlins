import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/routes')({
  component: RoutesPage,
})

function RoutesPage() {
  return (
    <div className="container mx-auto p-8">
      <h1 className="text-2xl font-semibold">Маршруты</h1>
    </div>
  )
}
