<template>
  <div class="user-list-panel">
    <div class="toolbar">
      <el-button type="primary" @click="handleCreate">新建用户</el-button>
    </div>

    <el-table v-loading="loading" :data="users" stripe>
      <el-table-column prop="username" label="用户名" width="150" />
      <el-table-column label="角色" width="120">
        <template #default="{ row }">
          <el-tag>{{ row.role.description || row.role.name }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="80">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'danger'">
            {{ row.is_active ? '启用' : '停用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="数据范围" min-width="150">
        <template #default="{ row }">
          <span v-if="row.role.name === 'super_admin'">全部堂区</span>
          <span v-else-if="row.role.name === 'data_entry' && row.village_id">
            所属堂区: {{ getVillageName(row.village_id) }}
          </span>
          <span v-else-if="row.role.name === 'observer' && row.accessible_village_ids?.length">
            可访问 {{ row.accessible_village_ids.length }} 个堂区
          </span>
          <el-tag v-else type="warning">未配置</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="handleEdit(row)">编辑</el-button>
          <el-button size="small" @click="handleResetPassword(row)">重置密码</el-button>
        </template>
      </el-table-column>
    </el-table>

    <UserFormDialog
      v-model="formVisible"
      :user="editingUser"
      :roles="roles"
      :villages="villages"
      @success="loadUsers"
    />

    <ResetPasswordDialog
      v-model="resetPasswordVisible"
      :user="resettingUser"
      @success="loadUsers"
    />
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'

import { roleApi } from '../../../api/roles'
import { userApi, type UserListItem, type VillageOption } from '../../../api/users'
import ResetPasswordDialog from './ResetPasswordDialog.vue'
import UserFormDialog from './UserFormDialog.vue'

const loading = ref(false)
const users = ref<UserListItem[]>([])
const roles = ref<{ id: number; name: string; description: string }[]>([])
const villages = ref<VillageOption[]>([])

const formVisible = ref(false)
const editingUser = ref<UserListItem | null>(null)

const resetPasswordVisible = ref(false)
const resettingUser = ref<UserListItem | null>(null)

const loadUsers = async () => {
  loading.value = true
  try {
    const [usersRes, rolesRes, villagesRes] = await Promise.all([
      userApi.list(),
      roleApi.list(),
      userApi.getVillageOptions(),
    ])
    users.value = usersRes.data
    roles.value = rolesRes.data.map((r) => ({ id: r.id, name: r.name, description: r.description }))
    villages.value = villagesRes.data
  } catch (error) {
    console.error('加载用户列表失败:', error)
  } finally {
    loading.value = false
  }
}

const getVillageName = (id: number): string => {
  return villages.value.find((v) => v.id === id)?.name || `ID: ${id}`
}

const handleCreate = () => {
  editingUser.value = null
  formVisible.value = true
}

const handleEdit = (user: UserListItem) => {
  editingUser.value = user
  formVisible.value = true
}

const handleResetPassword = (user: UserListItem) => {
  resettingUser.value = user
  resetPasswordVisible.value = true
}

onMounted(loadUsers)
</script>

<style scoped>
.user-list-panel {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.toolbar {
  margin-bottom: 16px;
}
</style>
