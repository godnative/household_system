<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-header">
        <h1>天主教教籍管理系统</h1>
        <p>阶段 3：登录骨架与鉴权闭环</p>
      </div>

      <el-alert v-if="errorMessage" :title="errorMessage" type="error" show-icon :closable="false" />

      <el-form label-position="top" @submit.prevent="handleSubmit">
        <el-form-item label="用户名">
          <el-input v-model="form.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="form.password" type="password" placeholder="请输入密码" show-password />
        </el-form-item>
        <el-button type="primary" :loading="loading" class="submit-button" @click="handleSubmit">
          登录
        </el-button>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const router = useRouter()

const loading = ref(false)
const errorMessage = ref('')
const form = reactive({
  username: 'admin',
  password: 'admin123',
})

async function handleSubmit() {
  errorMessage.value = ''
  if (!form.username.trim() || !form.password.trim()) {
    errorMessage.value = '请输入用户名和密码'
    return
  }

  loading.value = true
  try {
    await authStore.login(form)
    await router.push('/dashboard')
  } catch (error) {
    errorMessage.value = '登录失败，请检查用户名或密码'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background: linear-gradient(135deg, #2563eb, #1d4ed8);
}

.login-card {
  width: 100%;
  max-width: 420px;
  padding: 32px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.95);
  box-shadow: 0 24px 48px rgba(15, 23, 42, 0.2);
}

.login-header {
  margin-bottom: 24px;
}

.login-header h1 {
  margin: 0;
  font-size: 28px;
  color: #111827;
}

.login-header p {
  margin: 8px 0 0;
  color: #6b7280;
}

.submit-button {
  width: 100%;
}
</style>
