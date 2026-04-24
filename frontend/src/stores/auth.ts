import { defineStore } from 'pinia'

import type { CurrentUserResponse } from '../api/auth'
import apiClient from '../api/client'

interface LoginPayload {
  username: string
  password: string
}

interface AuthState {
  token: string
  currentUser: CurrentUserResponse | null
  initialized: boolean
}

const TOKEN_KEY = 'household-system-token'

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    token: localStorage.getItem(TOKEN_KEY) || '',
    currentUser: null,
    initialized: false,
  }),
  getters: {
    isAuthenticated: (state) => Boolean(state.token),
    hasPermission:
      (state) =>
      (permission: string): boolean =>
        state.currentUser?.permission_names.includes(permission) ?? false,
    hasAnyPermission:
      (state) =>
      (permissions: string[]): boolean =>
        permissions.some((p) => state.currentUser?.permission_names.includes(p)) ?? false,
    canManageUsers: (state) => state.currentUser?.permission_names.includes('user_manage') ?? false,
    canManageRoles: (state) =>
      state.currentUser?.permission_names.includes('role_manage') ?? false,
    canAccessUserManagement: (state) =>
      state.currentUser?.permission_names.includes('user_manage') ||
      state.currentUser?.permission_names.includes('role_manage') ||
      false,
  },
  actions: {
    async login(payload: LoginPayload) {
      const response = await apiClient.post('/api/v1/auth/login', payload)
      this.token = response.data.access_token
      localStorage.setItem(TOKEN_KEY, this.token)
      await this.fetchCurrentUser()
    },
    async fetchCurrentUser() {
      if (!this.token) {
        this.currentUser = null
        this.initialized = true
        return
      }

      try {
        const response = await apiClient.get('/api/v1/auth/me')
        this.currentUser = response.data
      } catch {
        this.logout()
      } finally {
        this.initialized = true
      }
    },
    logout() {
      this.token = ''
      this.currentUser = null
      this.initialized = true
      localStorage.removeItem(TOKEN_KEY)
    },
  },
})
