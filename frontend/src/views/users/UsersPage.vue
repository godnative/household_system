<template>
  <PageContainer title="用户角色管理">
    <el-tabs v-model="activeTab" class="management-tabs">
      <el-tab-pane
        v-if="authStore.canManageUsers"
        label="用户管理"
        name="users"
      >
        <UserListPanel />
      </el-tab-pane>
      <el-tab-pane
        v-if="authStore.canManageRoles"
        label="角色管理"
        name="roles"
      >
        <RoleListPanel />
      </el-tab-pane>
    </el-tabs>
  </PageContainer>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import PageContainer from '../../components/PageContainer.vue'
import { useAuthStore } from '../../stores/auth'
import RoleListPanel from './components/RoleListPanel.vue'
import UserListPanel from './components/UserListPanel.vue'

const authStore = useAuthStore()
const route = useRoute()
const router = useRouter()

const activeTab = ref('users')

// 根据权限设置默认 tab
watch(
  () => authStore.currentUser,
  () => {
    if (!authStore.canManageUsers && authStore.canManageRoles) {
      activeTab.value = 'roles'
    } else if (authStore.canManageUsers) {
      activeTab.value = 'users'
    } else if (!authStore.canAccessUserManagement) {
      router.push('/dashboard')
    }
  },
  { immediate: true },
)

// 如果没有任何管理权限，重定向到首页
if (!authStore.canAccessUserManagement) {
  router.push('/dashboard')
}
</script>

<style scoped>
.management-tabs {
  height: 100%;
}

.management-tabs :deep(.el-tabs__content) {
  height: calc(100% - 40px);
  overflow: auto;
}

.management-tabs :deep(.el-tab-pane) {
  height: 100%;
}
</style>
