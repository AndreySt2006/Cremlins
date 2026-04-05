import { create } from 'zustand'
import type { KremlinListItem } from '@/types/kremlin'

interface MapSearchState {
  pendingKremlin: KremlinListItem | null
  setPendingKremlin: (k: KremlinListItem | null) => void
}

export const useMapSearchStore = create<MapSearchState>()((set) => ({
  pendingKremlin: null,
  setPendingKremlin: (k) => set({ pendingKremlin: k }),
}))
