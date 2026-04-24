<template>
  <PageContainer :title="title" :description="description">
    <el-empty description="阶段 3 占位页面，阶段 4 开始迁移真实业务能力。" />

    <template #actions>
      <PermissionGate :permissions="['user_manage']">
        <el-tag type="danger">需要 user_manage 权限</el-tag>
      </PermissionGate>
      <PermissionGate :permissions="['member_view']">
        <el-tag type="success">当前账号具备 member_view 权限</el-tag>
      </PermissionGate>
    </template>

    <el-alert type="info" :closable="false" show-icon>
      <template #title>权限门控示例</template>
      <div class="permission-demo">
        <PermissionGate :permissions="['member_view']">
          <div>你当前可以看到 member_view 区块。</div>
        </PermissionGate>
        <PermissionGate :permissions="['user_manage']">
          <div>你当前可以看到 user_manage 区块。</div>
        </PermissionGate>
        <PermissionGate :roles="['observer']">
          <div>只有 observer 角色可以看到这个区块。</div>
        </PermissionGate>
      </div>
    </el-alert>
  </PageContainer>
</template>

<script setup lang="ts">
import PageContainer from '../components/PageContainer.vue'
import PermissionGate from '../components/PermissionGate.vue'

defineProps<{
  title: string
  description: string
}>()
</script>

<style scoped>
.permission-demo {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
</style>
