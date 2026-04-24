import apiClient from './client'
import type { PaginatedResponse, PaginationParams } from './pagination'

export interface HouseholdSearchResult {
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

export interface MemberSearchResult {
  id: number
  household_id: number
  household_address: string
  village_name: string
  name: string
  gender: string
  birth_date: string | null
  baptismal_name: string | null
  relation_to_head: string | null
  photo: string | null
  created_at: string
}

export interface SearchParams extends PaginationParams {
  keyword: string
}

export const searchApi = {
  households: (params: SearchParams) =>
    apiClient.get<PaginatedResponse<HouseholdSearchResult>>('/api/v1/search/households', { params }),

  members: (params: SearchParams) =>
    apiClient.get<PaginatedResponse<MemberSearchResult>>('/api/v1/search/members', { params }),
}
