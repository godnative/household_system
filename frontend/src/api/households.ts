import apiClient from './client'
import type { PaginatedResponse, PaginationParams } from './pagination'

export interface HouseholdListItem {
  id: number
  village_id: number
  village_name: string
  plot_number: number
  address: string
  phone: string | null
  head_of_household: string | null
  member_count: number
  created_at: string
}

export interface MemberSummary {
  id: number
  name: string
  gender: string
  birth_date: string | null
  relation_to_head: string | null
  baptismal_name: string | null
}

export interface HouseholdDetail extends HouseholdListItem {
  updated_at: string
  members: MemberSummary[]
}

export interface HouseholdCreate {
  village_id: number
  plot_number: number
  address: string
  phone?: string
  head_of_household?: string
}

export interface HouseholdUpdate {
  village_id?: number
  plot_number?: number
  address?: string
  phone?: string
  head_of_household?: string
}

export interface HouseholdListParams extends PaginationParams {
  village_id?: number
  search?: string
}

export const householdApi = {
  list: (params?: HouseholdListParams) =>
    apiClient.get<PaginatedResponse<HouseholdListItem>>('/api/v1/households', { params }),

  get: (id: number) => apiClient.get<HouseholdDetail>(`/api/v1/households/${id}`),

  create: (data: HouseholdCreate) => apiClient.post<HouseholdListItem>('/api/v1/households', data),

  update: (id: number, data: HouseholdUpdate) =>
    apiClient.put<HouseholdListItem>(`/api/v1/households/${id}`, data),

  delete: (id: number) => apiClient.delete(`/api/v1/households/${id}`),
}
