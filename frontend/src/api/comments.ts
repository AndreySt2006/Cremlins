import { api } from '../lib/api'
import type { Comment, CreateCommentPayload } from '../types'

export const getComments = (kremlinId: number): Promise<Comment[]> =>
  api.get(`kremlins/${kremlinId}/comments`).json()

export const createComment = (
  kremlinId: number,
  payload: CreateCommentPayload,
): Promise<Comment> => {
  const form = new FormData()
  form.append('text', payload.text)
  payload.images?.forEach((file) => form.append('images', file))

  return api
    .post(`kremlins/${kremlinId}/comments`, { body: form })
    .json()
}
