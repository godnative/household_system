<template>
  <div class="role-list-panel">
    <div class="toolbar">
      <el-button type="primary" @click="handleCreate">新建角色</el-button>
    </div>

    <el-table v-loading="loading" :data="roles" stripe>
      <el-table-column prop="name" label="角色标识" width="120" />
      <el-table-column prop="description" label="角色名称" width="150">
        <template #default="{ row }">
          {{ row.description || row.name }}
        </template>
      </el-table-column>
      <el-table-column label="权限" min-width="300">
        <template #default="{ row }">
          <div class="permission-tags">
            <el-tag
              v-for="permission in row.permissions"
              :key="permission.id"
              size="small"
              class="permission-tag"
            >
              {{ permission.description || permission.name }}
            </el-tag>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="100" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="handleEdit(row)">编辑</el-button>
        </template>
      </el-table-column>
    </el-table>

    <RoleFormDialog
      v-model="formVisible"
      :role="editingRole"
      :permissions="permissions"
      @success="loadRoles"
    />
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'

import { roleApi, type PermissionOption, type RoleListItem } from '../../../api/roles'
import RoleFormDialog from './RoleFormDialog.vue'

const loading = ref(false)
const roles = ref<RoleListItem[]>([])
const permissions = ref<PermissionOption[]>([])

const formVisible = ref(false)
const editingRole = ref<RoleListItem | null>(null)

const loadRoles = async () => {
  loading.value = true
  try {
    const [rolesRes, permissionsRes] = await Promise.all([
      roleApi.list(),
      roleApi.getPermissionOptions(),
    ])
    roles.value = rolesRes.data
    permissions.value = permissionsRes.data
  } catch (error) {
    console.error('加载角色列表失败:', error)
  } finally {
    loading.value = false
  }
}

const handleCreate = () => {
  editingRole.value = null
  formVisible.value = true
}

const handleEdit = (role: RoleListItem) => {
  editingRole.value = role
  formVisible.value = true
}

onMounted(loadRoles)
</script>

<style scoped>
.role-list-panel {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.toolbar {
  margin-bottom: 16px;
}

.permission-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.permission-tag {
  margin: 0;
}
</style>
