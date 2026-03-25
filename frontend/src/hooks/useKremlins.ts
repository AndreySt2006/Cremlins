import { useQuery } from '@tanstack/react-query'
import { getKremlins } from '../api/kremlins'

export const useKremlins = () =>
  useQuery({
    queryKey: ['kremlins'],
    queryFn: getKremlins,
  })
