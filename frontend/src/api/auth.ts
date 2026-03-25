import { api } from '../lib/api'
import type { User, AuthResponse } from '../types'

export const login = (email: string, password: string): Promise<AuthResponse> =>
  api.post('auth/login', { json: { email, password } }).json()

export const register = (
  username: string,
  email: string,
  password: string,
): Promise<AuthResponse> =>
  api.post('auth/register', { json: { username, email, password } }).json()

export const getMe = (): Promise<User> =>
  api.get('auth/me').json()
