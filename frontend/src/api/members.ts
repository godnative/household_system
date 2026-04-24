import apiClient from './client'
import type { PaginatedResponse, PaginationParams } from './pagination'

export interface MemberListItem {
  id: number
  household_id: number
  name: string
  gender: string
  birth_date: string | null
  baptismal_name: string | null
  relation_to_head: string | null
  photo: string | null
  created_at: string
}

export interface MemberDetail {
  id: number
  household_id: number
  name: string
  gender: string
  birth_date: string | null
  baptismal_name: string | null
  relation_to_head: string | null
  education: string | null
  move_in_date: string | null
  occupation: string | null
  church_id: string | null
  baptism_priest: string | null
  baptism_godparent: string | null
  baptism_date: string | null
  baptism_note: string | null
  first_communion_date: string | null
  supplementary_priest: string | null
  supplementary_place: string | null
  supplementary_date: string | null
  photo: string | null
  confirmation_date: string | null
  confirmation_priest: string | null
  confirmation_godparent: string | null
  confirmation_name: string | null
  confirmation_age: number | null
  confirmation_place: string | null
  marriage_date: string | null
  marriage_priest: string | null
  marriage_witness: string | null
  marriage_dispensation_item: string | null
  marriage_dispensation_priest: string | null
  marriage_place: string | null
  anointing_date: string | null
  anointing_priest: string | null
  anointing_place: string | null
  death_date: string | null
  death_age: number | null
  association: string | null
  note: string | null
  created_at: string
  updated_at: string
}

export interface MemberCreate {
  household_id: number
  name: string
  gender: string
  birth_date?: string
  baptismal_name?: string
  relation_to_head?: string
  education?: string
  move_in_date?: string
  occupation?: string
  church_id?: string
  baptism_priest?: string
  baptism_godparent?: string
  baptism_date?: string
  baptism_note?: string
  first_communion_date?: string
  supplementary_priest?: string
  supplementary_place?: string
  supplementary_date?: string
  photo?: string
  confirmation_date?: string
  confirmation_priest?: string
  confirmation_godparent?: string
  confirmation_name?: string
  confirmation_age?: number
  confirmation_place?: string
  marriage_date?: string
  marriage_priest?: string
  marriage_witness?: string
  marriage_dispensation_item?: string
  marriage_dispensation_priest?: string
  marriage_place?: string
  anointing_date?: string
  anointing_priest?: string
  anointing_place?: string
  death_date?: string
  death_age?: number
  association?: string
  note?: string
}

export type MemberUpdate = Partial<MemberCreate>

export interface MemberListParams extends PaginationParams {
  household_id?: number
  search?: string
}

export const memberApi = {
  list: (params?: MemberListParams) =>
    apiClient.get<PaginatedResponse<MemberListItem>>('/api/v1/members', { params }),

  get: (id: number) => apiClient.get<MemberDetail>(`/api/v1/members/${id}`),

  create: (data: MemberCreate) => apiClient.post<MemberDetail>('/api/v1/members', data),

  update: (id: number, data: MemberUpdate) =>
    apiClient.put<MemberDetail>(`/api/v1/members/${id}`, data),

  delete: (id: number) => apiClient.delete(`/api/v1/members/${id}`),

  setAsHead: (id: number) => apiClient.post<{ message: string }>(`/api/v1/members/${id}/set-head`),
}
