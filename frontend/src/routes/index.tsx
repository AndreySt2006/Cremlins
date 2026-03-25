import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/')({
  component: IndexPage,
})

function IndexPage() {
  return (
    <div className="container mx-auto p-8">
      <h1 className="text-2xl font-semibold">Карта</h1>
    </div>
  )
}
