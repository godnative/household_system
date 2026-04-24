<template>
  <PageContainer title="系统首页" description="当前阶段已完成前端布局、路由守卫与最小登录闭环骨架。">
    <el-descriptions :column="1" border>
      <el-descriptions-item label="当前用户">
        {{ authStore.currentUser?.username || '未登录' }}
      </el-descriptions-item>
      <el-descriptions-item label="角色">
        {{ authStore.currentUser?.role_names.join('、') || '无' }}
      </el-descriptions-item>
      <el-descriptions-item label="权限数">
        {{ authStore.currentUser?.permission_names.length || 0 }}
      </el-descriptions-item>
      <el-descriptions-item label="受保护接口返回">
        {{ dashboardMessage }}
      </el-descriptions-item>
    </el-descriptions>
  </PageContainer>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'

import apiClient from '../api/client'
import PageContainer from '../components/PageContainer.vue'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const dashboardMessage = ref('加载中...')

onMounted(async () => {
  try {
    const response = await apiClient.get('/api/v1/dashboard')
    dashboardMessage.value = response.data.message
  } catch {
    dashboardMessage.value = '读取失败'
  }
})
</script>
