import apiClient from './client'

export interface PermissionOption {
  id: number
  name: string
  description: string
}

export interface RoleListItem {
  id: number
  name: string
  description: string
  permissions: PermissionOption[]
}

export interface RoleDetail extends RoleListItem {}

export interface RoleCreateRequest {
  name: string
  description?: string
  permission_ids: number[]
}

export interface RoleUpdateRequest {
  name: string
  description?: string
  permission_ids: number[]
}

export const roleApi = {
  list: () => apiClient.get<RoleListItem[]>('/api/v1/roles'),

  get: (id: number) => apiClient.get<RoleDetail>(`/api/v1/roles/${id}`),

  create: (data: RoleCreateRequest) => apiClient.post<RoleDetail>('/api/v1/roles', data),

  update: (id: number, data: RoleUpdateRequest) =>
    apiClient.put<RoleDetail>(`/api/v1/roles/${id}`, data),

  delete: (id: number) => apiClient.delete(`/api/v1/roles/${id}`),

  getPermissionOptions: () => apiClient.get<PermissionOption[]>('/api/v1/roles/options/permissions'),
}
