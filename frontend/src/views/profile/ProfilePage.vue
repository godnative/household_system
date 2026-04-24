<template>
  <PageContainer title="个人信息">
    <el-descriptions v-if="authStore.currentUser" :column="2" border>
      <el-descriptions-item label="用户名">
        {{ authStore.currentUser.username }}
      </el-descriptions-item>
      <el-descriptions-item label="状态">
        <el-tag :type="authStore.currentUser.is_active ? 'success' : 'danger'">
          {{ authStore.currentUser.is_active ? '启用' : '停用' }}
        </el-tag>
      </el-descriptions-item>
      <el-descriptions-item label="角色">
        {{ authStore.currentUser.role.description || authStore.currentUser.role.name }}
      </el-descriptions-item>
      <el-descriptions-item label="创建时间">
        {{ formatDate(authStore.currentUser.created_at) }}
      </el-descriptions-item>
      <el-descriptions-item label="数据范围" :span="2">
        <span v-if="authStore.currentUser.role.name === 'super_admin'">全部堂区</span>
        <span v-else-if="authStore.currentUser.role.name === 'data_entry' && authStore.currentUser.village_id">
          所属堂区 ID: {{ authStore.currentUser.village_id }}
        </span>
        <span v-else-if="authStore.currentUser.role.name === 'observer' && authStore.currentUser.accessible_village_ids?.length">
          可访问 {{ authStore.currentUser.accessible_village_ids.length }} 个堂区
        </span>
        <el-tag v-else type="warning">未配置</el-tag>
      </el-descriptions-item>
      <el-descriptions-item label="权限列表" :span="2">
        <div class="permission-tags">
          <el-tag
            v-for="permission in authStore.currentUser.permission_names"
            :key="permission"
            size="small"
            class="permission-tag"
          >
            {{ getPermissionLabel(permission) }}
          </el-tag>
        </div>
      </el-descriptions-item>
    </el-descriptions>
  </PageContainer>
</template>

<script setup lang="ts">
import { useAuthStore } from '../../stores/auth'
import PageContainer from '../../components/PageContainer.vue'

const authStore = useAuthStore()

const formatDate = (dateStr: string): string => {
  return new Date(dateStr).toLocaleString('zh-CN')
}

const permissionLabels: Record<string, string> = {
  user_manage: '用户管理',
  role_manage: '角色管理',
  village_manage: '堂区管理',
  household_manage: '家庭管理',
  household_view: '家庭查看',
  member_manage: '成员管理',
  member_view: '成员查看',
}

const getPermissionLabel = (name: string): string => {
  return permissionLabels[name] || name
}
</script>

<style scoped>
.permission-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.permission-tag {
  margin: 0;
}
</style>
