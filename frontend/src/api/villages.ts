import apiClient from './client'
import type { PaginatedResponse, PaginationParams } from './pagination'

export interface VillageListItem {
  id: number
  name: string
  code: string
  created_at: string
  household_count: number
}

export interface VillageDetail extends VillageListItem {
  member_count: number
}

export interface VillageCreate {
  name: string
  code: string
}

export interface VillageUpdate {
  name?: string
  code?: string
}

export const villageApi = {
  list: (params?: PaginationParams) =>
    apiClient.get<PaginatedResponse<VillageListItem>>('/api/v1/villages', { params }),

  get: (id: number) => apiClient.get<VillageDetail>(`/api/v1/villages/${id}`),

  create: (data: VillageCreate) => apiClient.post<VillageListItem>('/api/v1/villages', data),

  update: (id: number, data: VillageUpdate) =>
    apiClient.put<VillageListItem>(`/api/v1/villages/${id}`, data),

  delete: (id: number) => apiClient.delete(`/api/v1/villages/${id}`),
}
