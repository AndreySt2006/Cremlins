import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface RoutesState {
  visited: number[]
  planned: number[]
  toggleVisited: (id: number) => void
  togglePlanned: (id: number) => void
  isVisited: (id: number) => boolean
  isPlanned: (id: number) => boolean
}

export const useRoutesStore = create<RoutesState>()(
  persist(
    (set, get) => ({
      visited: [],
      planned: [],
      toggleVisited: (id) =>
        set((s) =>
          s.visited.includes(id)
            ? { visited: s.visited.filter((x) => x !== id) }
            : { visited: [...s.visited, id] },
        ),
      togglePlanned: (id) =>
        set((s) =>
          s.planned.includes(id)
            ? { planned: s.planned.filter((x) => x !== id) }
            : { planned: [...s.planned, id] },
        ),
      isVisited: (id) => get().visited.includes(id),
      isPlanned: (id) => get().planned.includes(id),
    }),
    { name: 'routes' },
  ),
)
