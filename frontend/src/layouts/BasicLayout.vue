<template>
  <div class="layout-shell">
    <aside class="sidebar">
      <div>
        <h2>教籍管理</h2>
        <p>{{ authStore.currentUser?.username || '未登录' }}</p>
      </div>

      <el-menu router :default-active="route.path" class="menu">
        <el-menu-item index="/dashboard">首页</el-menu-item>
        <el-menu-item index="/search">搜索</el-menu-item>
        <el-menu-item index="/villages">堂区管理</el-menu-item>
        <el-menu-item index="/households">家庭管理</el-menu-item>
        <el-menu-item index="/members">成员管理</el-menu-item>
        <el-menu-item v-if="authStore.canAccessUserManagement" index="/users">
          用户角色管理
        </el-menu-item>
        <el-menu-item index="/settings">系统设置</el-menu-item>
        <el-menu-item index="/profile">我的信息</el-menu-item>
        <el-menu-item index="/change-password">修改密码</el-menu-item>
      </el-menu>
    </aside>

    <div class="main-panel">
      <header class="topbar">
        <span>教籍管理系统</span>
        <el-button link type="danger" @click="handleLogout">退出登录</el-button>
      </header>
      <main class="content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'

import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const route = useRoute()
const router = useRouter()

function handleLogout() {
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.layout-shell {
  min-height: 100vh;
  display: grid;
  grid-template-columns: 240px 1fr;
  background: #f3f4f6;
}

.sidebar {
  padding: 24px 16px;
  background: #111827;
  color: #fff;
}

.sidebar h2 {
  margin: 0;
}

.sidebar p {
  margin: 8px 0 24px;
  color: #d1d5db;
}

.menu {
  border-right: 0;
  background: transparent;
}

:deep(.el-menu-item) {
  color: #e5e7eb;
}

:deep(.el-menu-item.is-active) {
  color: #60a5fa;
}

.main-panel {
  display: flex;
  flex-direction: column;
}

.topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  background: #fff;
  border-bottom: 1px solid #e5e7eb;
}

.content {
  padding: 24px;
}
</style>
