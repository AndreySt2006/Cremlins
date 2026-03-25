export interface User {
  id: number
  username: string
  email: string
  avatarUrl: string | null
  createdAt: string
}

export interface AuthResponse {
  user: User
  accessToken: string
}
