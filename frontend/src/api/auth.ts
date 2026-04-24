import apiClient from './client'

export interface RoleSummary {
  id: number
  name: string
  description: string
}

export interface CurrentUserResponse {
  id: number
  username: string
  is_active: boolean
  role: RoleSummary
  role_names: string[]
  permission_names: string[]
  village_id: number | null
  accessible_village_ids: number[]
  created_at: string
}

export interface LoginRequest {
  username: string
  password: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
}

export interface ChangePasswordRequest {
  old_password: string
  new_password: string
}

export const authApi = {
  login: (data: LoginRequest) => apiClient.post<TokenResponse>('/api/v1/auth/login', data),

  me: () => apiClient.get<CurrentUserResponse>('/api/v1/auth/me'),

  changePassword: (data: ChangePasswordRequest) =>
    apiClient.post<{ message: string }>('/api/v1/auth/change-password', data),
}
