<template>
  <PageContainer title="系统设置">
    <el-card class="settings-card">
      <template #header>
        <span class="card-title">数据库管理</span>
      </template>

      <el-descriptions v-loading="loading" :column="2" border>
        <el-descriptions-item label="用户数">{{ dbInfo?.user_count || 0 }}</el-descriptions-item>
        <el-descriptions-item label="堂区数">{{ dbInfo?.village_count || 0 }}</el-descriptions-item>
        <el-descriptions-item label="家庭数">{{ dbInfo?.household_count || 0 }}</el-descriptions-item>
        <el-descriptions-item label="成员数">{{ dbInfo?.member_count || 0 }}</el-descriptions-item>
        <el-descriptions-item label="数据库类型">SQLite</el-descriptions-item>
        <el-descriptions-item label="文件大小">
          {{ dbInfo?.file_size_mb ? `${dbInfo.file_size_mb} MB` : '-' }}
        </el-descriptions-item>
      </el-descriptions>

      <div class="actions">
        <el-button type="primary" :loading="downloading" @click="handleBackup">
          下载数据库备份
        </el-button>
        <el-upload
          :show-file-list="false"
          :auto-upload="false"
          accept=".db,.sqlite,.sqlite3"
          :on-change="handleImportChange"
        >
          <el-button type="danger" :loading="importing">
            导入数据库恢复
          </el-button>
        </el-upload>
      </div>

      <el-alert
        type="warning"
        title="高风险操作"
        :closable="false"
        style="margin-top: 16px"
      >
        <p>导入数据库会先自动备份当前数据库，再用所选 SQLite 文件覆盖现有数据。</p>
        <p>导入成功后请立即重启后端服务，并重新登录系统。</p>
      </el-alert>

      <el-alert
        type="info"
        title="提示"
        :closable="false"
        style="margin-top: 16px"
      >
        <p>下载数据库备份将创建当前数据库的完整副本。</p>
        <p>备份文件为 SQLite 格式，可用于数据恢复或迁移。</p>
      </el-alert>
    </el-card>

    <el-card class="settings-card" style="margin-top: 20px">
      <template #header>
        <span class="card-title">系统信息</span>
      </template>

      <el-descriptions :column="1" border>
        <el-descriptions-item label="系统版本">1.0.0</el-descriptions-item>
        <el-descriptions-item label="前端框架">Vue 3 + Element Plus</el-descriptions-item>
        <el-descriptions-item label="后端框架">FastAPI + SQLAlchemy</el-descriptions-item>
      </el-descriptions>
    </el-card>
  </PageContainer>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox, type UploadFile, type UploadFiles } from 'element-plus'

import { settingsApi, type DatabaseInfo } from '../../api/settings'
import PageContainer from '../../components/PageContainer.vue'

const loading = ref(false)
const downloading = ref(false)
const importing = ref(false)
const dbInfo = ref<DatabaseInfo | null>(null)

const loadDatabaseInfo = async () => {
  loading.value = true
  try {
    const res = await settingsApi.getDatabaseInfo()
    dbInfo.value = res.data
  } catch (error) {
    console.error('获取数据库信息失败:', error)
    ElMessage.error('获取数据库信息失败')
  } finally {
    loading.value = false
  }
}

const handleBackup = async () => {
  downloading.value = true
  try {
    const token = localStorage.getItem('token')
    const url = `/api/v1/settings/backup?token=${token}`

    const link = document.createElement('a')
    link.href = url
    link.download = `household_backup_${new Date().toISOString().slice(0, 10)}.db`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)

    ElMessage.success('备份下载已开始')
  } catch (error) {
    console.error('下载备份失败:', error)
    ElMessage.error('下载备份失败')
  } finally {
    downloading.value = false
  }
}

const handleImportChange = async (uploadFile: UploadFile, _uploadFiles: UploadFiles) => {
  const file = uploadFile.raw
  if (!file) {
    ElMessage.error('读取导入文件失败')
    return
  }

  try {
    await ElMessageBox.confirm(
      '导入数据库将覆盖当前所有数据。系统会先自动备份当前数据库。导入成功后需要重启后端服务并重新登录，是否继续？',
      '确认导入数据库',
      {
        type: 'warning',
        confirmButtonText: '继续导入',
        cancelButtonText: '取消',
      },
    )
  } catch {
    return
  }

  importing.value = true
  try {
    const res = await settingsApi.importDatabase(file)
    ElMessage.success(res.data.message)
    await loadDatabaseInfo()
  } catch (error: unknown) {
    console.error('导入数据库失败:', error)
    const err = error as { response?: { data?: { detail?: string } } }
    ElMessage.error(err.response?.data?.detail || '导入数据库失败')
  } finally {
    importing.value = false
  }
}

onMounted(loadDatabaseInfo)
</script>

<style scoped>
.settings-card {
  max-width: 800px;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
}

.actions {
  margin-top: 20px;
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}
</style>
