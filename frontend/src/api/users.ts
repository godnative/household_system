import apiClient from './client'

export interface UserListItem {
  id: number
  username: string
  is_active: boolean
  role: {
    id: number
    name: string
    description: string
  }
  village_id: number | null
  accessible_village_ids: number[]
}

export interface UserDetail extends UserListItem {
  created_at: string
}

export interface UserCreateRequest {
  username: string
  password: string
  role_id: number
  is_active: boolean
  village_id?: number
  accessible_village_ids?: number[]
}

export interface UserUpdateRequest {
  role_id: number
  is_active: boolean
  village_id?: number
  accessible_village_ids?: number[]
}

export interface VillageOption {
  id: number
  name: string
}

export const userApi = {
  list: () => apiClient.get<UserListItem[]>('/api/v1/users'),

  get: (id: number) => apiClient.get<UserDetail>(`/api/v1/users/${id}`),

  create: (data: UserCreateRequest) => apiClient.post<UserDetail>('/api/v1/users', data),

  update: (id: number, data: UserUpdateRequest) =>
    apiClient.put<UserDetail>(`/api/v1/users/${id}`, data),

  resetPassword: (id: number, new_password: string) =>
    apiClient.put<{ message: string }>(`/api/v1/users/${id}/password`, { new_password }),

  getVillageOptions: () => apiClient.get<VillageOption[]>('/api/v1/users/options/villages'),
}
