import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/profile')({
  component: ProfilePage,
})

function ProfilePage() {
  return (
    <div className="container mx-auto p-8">
      <h1 className="text-2xl font-semibold">Профиль</h1>
    </div>
  )
}
