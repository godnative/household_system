import { createRouter, createWebHistory } from 'vue-router'

import BasicLayout from '../layouts/BasicLayout.vue'
import ChangePasswordPage from '../views/profile/ChangePasswordPage.vue'
import ProfilePage from '../views/profile/ProfilePage.vue'
import DashboardView from '../views/DashboardView.vue'
import HouseholdManagementPage from '../views/households/HouseholdManagementPage.vue'
import LoginView from '../views/LoginView.vue'
import MembersPage from '../views/members/MembersPage.vue'
import PrintPage from '../views/print/PrintPage.vue'
import SearchPage from '../views/search/SearchPage.vue'
import SettingsPage from '../views/settings/SettingsPage.vue'
import UsersPage from '../views/users/UsersPage.vue'
import VillagesPage from '../views/villages/VillagesPage.vue'
import { useAuthStore } from '../stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: LoginView,
      meta: { public: true },
    },
    {
      path: '/print',
      name: 'print',
      component: PrintPage,
    },
    {
      path: '/',
      component: BasicLayout,
      children: [
        {
          path: '',
          redirect: '/dashboard',
        },
        {
          path: 'dashboard',
          name: 'dashboard',
          component: DashboardView,
        },
        {
          path: 'villages',
          name: 'villages',
          component: VillagesPage,
        },
        {
          path: 'households',
          name: 'households',
          component: HouseholdManagementPage,
        },
        {
          path: 'members',
          name: 'members',
          component: MembersPage,
        },
        {
          path: 'search',
          name: 'search',
          component: SearchPage,
        },
        {
          path: 'settings',
          name: 'settings',
          component: SettingsPage,
        },
        {
          path: 'users',
          name: 'users',
          component: UsersPage,
          meta: { permissions: ['user_manage', 'role_manage'] },
        },
        {
          path: 'profile',
          name: 'profile',
          component: ProfilePage,
        },
        {
          path: 'change-password',
          name: 'change-password',
          component: ChangePasswordPage,
        },
      ],
    },
    {
      path: '/:pathMatch(.*)*',
      redirect: '/dashboard',
    },
  ],
})

router.beforeEach(async (to) => {
  const authStore = useAuthStore()

  if (!authStore.initialized) {
    await authStore.fetchCurrentUser()
  }

  if (to.meta.public) {
    if (to.path === '/login' && authStore.isAuthenticated) {
      return '/dashboard'
    }
    return true
  }

  if (!authStore.isAuthenticated) {
    return '/login'
  }

  // 检查权限
  const requiredPermissions = to.meta.permissions as string[] | undefined
  if (requiredPermissions && requiredPermissions.length > 0) {
    const hasPermission = requiredPermissions.some((p) => authStore.hasPermission(p))
    if (!hasPermission) {
      return '/dashboard'
    }
  }

  return true
})

export default router
