import { useQuery } from '@tanstack/react-query'
import { getKremlin } from '../api/kremlins'

export const useKremlin = (id: number) =>
  useQuery({
    queryKey: ['kremlin', id],
    queryFn: () => getKremlin(id),
    enabled: !!id,
  })
