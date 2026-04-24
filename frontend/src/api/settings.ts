import apiClient from './client'

export interface DatabaseInfo {
  database_url: string
  file_size?: number
  file_size_mb?: number
  last_modified?: number
  user_count: number
  village_count: number
  household_count: number
  member_count: number
}

export interface ImportDatabaseResponse {
  message: string
  backup_path: string
  requires_restart: boolean
}

export const settingsApi = {
  getDatabaseInfo: () => apiClient.get<DatabaseInfo>('/api/v1/settings/database-info'),

  downloadBackup: () => {
    return '/api/v1/settings/backup'
  },

  importDatabase: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return apiClient.post<ImportDatabaseResponse>('/api/v1/settings/import', formData)
  },
}
