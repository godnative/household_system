<template>
  <div v-if="allowed">
    <slot />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

import { useAuthStore } from '../stores/auth'

const props = defineProps<{
  permissions?: string[]
  roles?: string[]
}>()

const authStore = useAuthStore()

const allowed = computed(() => {
  const user = authStore.currentUser
  if (!user) {
    return false
  }

  const permissionsAllowed = !props.permissions?.length || props.permissions.some((permission) => user.permission_names.includes(permission))
  const rolesAllowed = !props.roles?.length || props.roles.some((role) => user.role_names.includes(role))

  return permissionsAllowed && rolesAllowed
})
</script>
