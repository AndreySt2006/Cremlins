export interface Comment {
  id: number
  kremlinId: number
  authorId: number
  authorName: string
  authorAvatarUrl: string | null
  text: string
  imageUrls: string[]
  createdAt: string
}

export interface CreateCommentPayload {
  text: string
  images?: File[]
}
