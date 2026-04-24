<template>
  <PageContainer title="文件上传验证" description="阶段 3 已接入真实上传接口，可用于验证登录态与图片上传链路。">
    <el-upload
      :show-file-list="false"
      :http-request="handleUpload"
      accept="image/png,image/jpeg,image/webp"
    >
      <el-button type="primary">选择并上传图片</el-button>
    </el-upload>

    <el-alert v-if="successMessage" :title="successMessage" type="success" show-icon :closable="false" />
    <el-alert v-if="errorMessage" :title="errorMessage" type="error" show-icon :closable="false" />

    <el-card v-if="uploadedFile" class="result-card">
      <p><strong>文件名：</strong>{{ uploadedFile.filename }}</p>
      <p><strong>大小：</strong>{{ uploadedFile.size }} bytes</p>
      <p><strong>类型：</strong>{{ uploadedFile.content_type }}</p>
      <p><strong>URL：</strong><a :href="uploadedFile.url" target="_blank">{{ uploadedFile.url }}</a></p>
    </el-card>
  </PageContainer>
</template>

<script setup lang="ts">
import { ref } from 'vue'

import apiClient from '../api/client'
import PageContainer from '../components/PageContainer.vue'

interface UploadedFile {
  filename: string
  size: number
  content_type: string
  url: string
}

const uploadedFile = ref<UploadedFile | null>(null)
const successMessage = ref('')
const errorMessage = ref('')

async function handleUpload(option: { file: File }) {
  successMessage.value = ''
  errorMessage.value = ''

  const formData = new FormData()
  formData.append('file', option.file)

  try {
    const response = await apiClient.post('/api/v1/uploads', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    uploadedFile.value = response.data
    successMessage.value = '图片上传成功'
  } catch (error: any) {
    errorMessage.value = error.response?.data?.detail || '图片上传失败'
  }
}
</script>

<style scoped>
.result-card {
  margin-top: 16px;
}
</style>
