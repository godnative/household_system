<template>
  <div class="print-page">
    <div class="print-toolbar" v-if="!isPrinting">
      <el-button @click="goBack">返回</el-button>
      <el-button type="primary" @click="handlePrint">打印 / 导出 PDF</el-button>
    </div>

    <div v-loading="loading" class="print-content">
      <div v-if="html" v-html="html"></div>
      <el-empty v-else-if="!loading" description="暂无可打印内容" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

import apiClient from '../../api/client'

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const html = ref('')
const isPrinting = ref(false)

const householdId = computed(() => Number(route.query.household_id || 0))
const memberId = computed(() => Number(route.query.member_id || 0))

const goBack = () => {
  router.back()
}

const handlePrint = () => {
  isPrinting.value = true
  window.print()
  setTimeout(() => {
    isPrinting.value = false
  }, 300)
}

const loadPrintHtml = async () => {
  loading.value = true
  try {
    if (memberId.value) {
      const res = await apiClient.get(`/api/v1/members/${memberId.value}/print`)
      html.value = res.data
      return
    }
    if (householdId.value) {
      const res = await apiClient.get(`/api/v1/households/${householdId.value}/print`)
      html.value = res.data
      return
    }
    html.value = ''
  } catch (error) {
    console.error('加载打印数据失败:', error)
    ElMessage.error('加载打印数据失败')
  } finally {
    loading.value = false
  }
}

onMounted(loadPrintHtml)
</script>

<style scoped>
.print-page {
  padding: 20px;
  background: #fff;
  min-height: 100vh;
}

.print-toolbar {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 1000;
  background: #fff;
  padding: 10px;
  border-radius: 4px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.print-content {
  max-width: 900px;
  margin: 0 auto;
}

:deep(table) {
  width: 100%;
  border-collapse: collapse;
}

:deep(td),
:deep(th) {
  border: 1px solid #999;
  padding: 8px;
}

@media print {
  .print-toolbar {
    display: none !important;
  }

  .print-page {
    padding: 0;
  }

  .print-content {
    max-width: none;
  }
}
</style>
