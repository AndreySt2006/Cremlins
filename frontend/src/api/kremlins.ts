import { api } from '../lib/api'
import type { KremlinListItem, KremlinDetail } from '../types'

export const getKremlins = (): Promise<KremlinListItem[]> =>
  api.get('kremlins').json()

export const getKremlin = (id: number): Promise<KremlinDetail> =>
  api.get(`kremlins/${id}`).json()
