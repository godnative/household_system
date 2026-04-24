<template>
  <PageContainer title="堂区管理">
    <div class="toolbar">
      <el-button v-if="authStore.hasPermission('village_manage')" type="primary" @click="handleCreate">
        新建堂区
      </el-button>
    </div>

    <el-table v-loading="loading" :data="villages" stripe>
      <el-table-column prop="code" label="编码" width="120" />
      <el-table-column prop="name" label="名称" min-width="150" />
      <el-table-column label="家庭数" width="100">
        <template #default="{ row }">
          {{ row.household_count }}
        </template>
      </el-table-column>
      <el-table-column label="创建时间" width="180">
        <template #default="{ row }">
          {{ formatDate(row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column v-if="authStore.hasPermission('village_manage')" label="操作" width="150" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="handleEdit(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination-container">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="loadVillages"
        @current-change="loadVillages"
      />
    </div>

    <el-dialog v-model="formVisible" :title="isEdit ? '编辑堂区' : '新建堂区'" width="400px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="编码" prop="code">
          <el-input v-model="form.code" placeholder="请输入堂区编码" />
        </el-form-item>
        <el-form-item label="名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入堂区名称" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="formVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </PageContainer>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

import { villageApi, type VillageListItem } from '../../api/villages'
import PageContainer from '../../components/PageContainer.vue'
import { useAuthStore } from '../../stores/auth'

const authStore = useAuthStore()
const loading = ref(false)
const villages = ref<VillageListItem[]>([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const formVisible = ref(false)
const submitting = ref(false)
const editingId = ref<number | null>(null)
const formRef = ref()

const form = reactive({ code: '', name: '' })
const rules = {
  code: [{ required: true, message: '请输入堂区编码', trigger: 'blur' }],
  name: [{ required: true, message: '请输入堂区名称', trigger: 'blur' }],
}

const isEdit = ref(false)

const loadVillages = async () => {
  loading.value = true
  try {
    const res = await villageApi.list({ page: currentPage.value, page_size: pageSize.value })
    villages.value = res.data.items
    total.value = res.data.meta.total
  } catch (error) {
    console.error('加载堂区列表失败:', error)
  } finally {
    loading.value = false
  }
}

const formatDate = (dateStr: string) => new Date(dateStr).toLocaleString('zh-CN')

const handleCreate = () => {
  isEdit.value = false
  editingId.value = null
  form.code = ''
  form.name = ''
  formVisible.value = true
}

const handleEdit = (row: VillageListItem) => {
  isEdit.value = true
  editingId.value = row.id
  form.code = row.code
  form.name = row.name
  formVisible.value = true
}

const handleDelete = async (row: VillageListItem) => {
  try {
    await ElMessageBox.confirm(`确定要删除堂区"${row.name}"吗？`, '确认删除', { type: 'warning' })
    await villageApi.delete(row.id)
    ElMessage.success('删除成功')
    loadVillages()
  } catch {}
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
  } catch {
    return
  }

  submitting.value = true
  try {
    if (isEdit.value && editingId.value) {
      await villageApi.update(editingId.value, form)
      ElMessage.success('更新成功')
    } else {
      await villageApi.create(form)
      ElMessage.success('创建成功')
    }
    formVisible.value = false
    loadVillages()
  } catch (error: unknown) {
    const err = error as { response?: { data?: { detail?: string } } }
    ElMessage.error(err.response?.data?.detail || '操作失败')
  } finally {
    submitting.value = false
  }
}

onMounted(loadVillages)
</script>

<style scoped>
.toolbar {
  margin-bottom: 16px;
}
.pagination-container {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}
</style>
