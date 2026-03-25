import { useQuery } from '@tanstack/react-query'
import { getComments } from '../api/comments'

export const useComments = (kremlinId: number) =>
  useQuery({
    queryKey: ['comments', kremlinId],
    queryFn: () => getComments(kremlinId),
    enabled: !!kremlinId,
  })
