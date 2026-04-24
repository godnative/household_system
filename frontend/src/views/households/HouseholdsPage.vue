<template>
  <PageContainer title="家庭管理">
    <div class="toolbar">
      <el-select v-model="filterVillageId" placeholder="选择堂区" clearable style="width: 200px; margin-right: 12px" @change="loadHouseholds">
        <el-option v-for="v in villages" :key="v.id" :label="v.name" :value="v.id" />
      </el-select>
      <el-input
        v-model="searchText"
        placeholder="搜索地址/户主"
        clearable
        style="width: 200px; margin-right: 12px"
        @keyup.enter="loadHouseholds"
      />
      <el-button type="primary" @click="loadHouseholds">查询</el-button>
      <el-button v-if="authStore.hasPermission('household_manage')" type="primary" @click="handleCreate">
        新建家庭
      </el-button>
    </div>

    <el-table v-loading="loading" :data="households" stripe>
      <el-table-column prop="village_name" label="堂区" width="120" />
      <el-table-column prop="plot_number" label="地块号" width="80" />
      <el-table-column prop="address" label="地址" min-width="200" />
      <el-table-column prop="head_of_household" label="户主" width="100" />
      <el-table-column prop="phone" label="电话" width="120" />
      <el-table-column label="成员数" width="80">
        <template #default="{ row }">
          {{ row.member_count }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="handleView(row)">详情</el-button>
          <el-button v-if="authStore.hasPermission('household_manage')" size="small" @click="handleEdit(row)">
            编辑
          </el-button>
          <el-button
            v-if="authStore.hasPermission('household_manage')"
            size="small"
            type="danger"
            @click="handleDelete(row)"
          >
            删除
          </el-button>
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
        @size-change="loadHouseholds"
        @current-change="loadHouseholds"
      />
    </div>

    <!-- 创建/编辑对话框 -->
    <el-dialog v-model="formVisible" :title="isEdit ? '编辑家庭' : '新建家庭'" width="500px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="堂区" prop="village_id">
          <el-select v-model="form.village_id" placeholder="请选择堂区">
            <el-option v-for="v in villages" :key="v.id" :label="v.name" :value="v.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="地块号" prop="plot_number">
          <el-input-number v-model="form.plot_number" :min="1" />
        </el-form-item>
        <el-form-item label="地址" prop="address">
          <el-input v-model="form.address" placeholder="请输入地址" />
        </el-form-item>
        <el-form-item label="电话">
          <el-input v-model="form.phone" placeholder="请输入电话" />
        </el-form-item>
        <el-form-item label="户主">
          <el-input v-model="form.head_of_household" placeholder="请输入户主姓名" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="formVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 详情对话框 -->
    <el-dialog v-model="detailVisible" title="家庭详情" width="700px">
      <el-descriptions v-if="currentHousehold" :column="2" border>
        <el-descriptions-item label="堂区">{{ currentHousehold.village_name }}</el-descriptions-item>
        <el-descriptions-item label="地块号">{{ currentHousehold.plot_number }}</el-descriptions-item>
        <el-descriptions-item label="地址" :span="2">{{ currentHousehold.address }}</el-descriptions-item>
        <el-descriptions-item label="户主">{{ currentHousehold.head_of_household || '-' }}</el-descriptions-item>
        <el-descriptions-item label="电话">{{ currentHousehold.phone || '-' }}</el-descriptions-item>
      </el-descriptions>

      <h4 style="margin-top: 20px; margin-bottom: 12px">成员列表</h4>
      <el-table :data="currentHousehold?.members || []" stripe size="small">
        <el-table-column prop="name" label="姓名" width="100" />
        <el-table-column prop="gender" label="性别" width="60" />
        <el-table-column prop="relation_to_head" label="与户主关系" width="100" />
        <el-table-column prop="baptismal_name" label="圣名" width="100" />
        <el-table-column label="出生日期" width="120">
          <template #default="{ row }">
            {{ row.birth_date || '-' }}
          </template>
        </el-table-column>
      </el-table>

      <template #footer>
        <el-button @click="detailVisible = false">关闭</el-button>
        <el-button type="primary" @click="handlePrint">打印</el-button>
      </template>
    </el-dialog>
  </PageContainer>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'

import { householdApi, type HouseholdDetail, type HouseholdListItem } from '../../api/households'
import { villageApi, type VillageListItem } from '../../api/villages'
import PageContainer from '../../components/PageContainer.vue'
import { useAuthStore } from '../../stores/auth'

const router = useRouter()

const authStore = useAuthStore()
const loading = ref(false)
const households = ref<HouseholdListItem[]>([])
const villages = ref<VillageListItem[]>([])
const filterVillageId = ref<number | null>(null)
const searchText = ref('')
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)

const formVisible = ref(false)
const detailVisible = ref(false)
const submitting = ref(false)
const editingId = ref<number | null>(null)
const formRef = ref()
const isEdit = ref(false)
const currentHousehold = ref<HouseholdDetail | null>(null)

const form = reactive({
  village_id: undefined as number | undefined,
  plot_number: 1,
  address: '',
  phone: '',
  head_of_household: '',
})

const rules = {
  village_id: [{ required: true, message: '请选择堂区', trigger: 'change' }],
  plot_number: [{ required: true, message: '请输入地块号', trigger: 'blur' }],
  address: [{ required: true, message: '请输入地址', trigger: 'blur' }],
}

const loadVillages = async () => {
  try {
    const res = await villageApi.list()
    villages.value = res.data.items
  } catch (error) {
    console.error('加载堂区列表失败:', error)
  }
}

const loadHouseholds = async () => {
  loading.value = true
  try {
    const params: { village_id?: number; search?: string; page?: number; page_size?: number } = {
      page: currentPage.value,
      page_size: pageSize.value,
    }
    if (filterVillageId.value) params.village_id = filterVillageId.value
    if (searchText.value) params.search = searchText.value
    const res = await householdApi.list(params)
    households.value = res.data.items
    total.value = res.data.meta.total
  } catch (error) {
    console.error('加载家庭列表失败:', error)
  } finally {
    loading.value = false
  }
}

const resetForm = () => {
  form.village_id = undefined
  form.plot_number = 1
  form.address = ''
  form.phone = ''
  form.head_of_household = ''
}

const handleCreate = () => {
  isEdit.value = false
  editingId.value = null
  resetForm()
  formVisible.value = true
}

const handleEdit = (row: HouseholdListItem) => {
  isEdit.value = true
  editingId.value = row.id
  form.village_id = row.village_id
  form.plot_number = row.plot_number
  form.address = row.address
  form.phone = row.phone || ''
  form.head_of_household = row.head_of_household || ''
  formVisible.value = true
}

const handleView = async (row: HouseholdListItem) => {
  try {
    const res = await householdApi.get(row.id)
    currentHousehold.value = res.data
    detailVisible.value = true
  } catch (error) {
    ElMessage.error('获取详情失败')
  }
}

const handlePrint = () => {
  if (!currentHousehold.value) return
  const memberIds = currentHousehold.value.members.map(m => m.id).join(',')
  router.push({
    path: '/print',
    query: {
      household_id: currentHousehold.value.id,
      member_ids: memberIds,
    },
  })
}

const handleDelete = async (row: HouseholdListItem) => {
  try {
    await ElMessageBox.confirm(`确定要删除该家庭吗？成员也将一并删除。`, '确认删除', { type: 'warning' })
    await householdApi.delete(row.id)
    ElMessage.success('删除成功')
    loadHouseholds()
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
    const data = {
      village_id: form.village_id!,
      plot_number: form.plot_number,
      address: form.address,
      phone: form.phone || undefined,
      head_of_household: form.head_of_household || undefined,
    }

    if (isEdit.value && editingId.value) {
      await householdApi.update(editingId.value, data)
      ElMessage.success('更新成功')
    } else {
      await householdApi.create(data)
      ElMessage.success('创建成功')
    }
    formVisible.value = false
    loadHouseholds()
  } catch (error: unknown) {
    const err = error as { response?: { data?: { detail?: string } } }
    ElMessage.error(err.response?.data?.detail || '操作失败')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  loadVillages()
  loadHouseholds()
})
</script>

<style scoped>
.toolbar {
  margin-bottom: 16px;
  display: flex;
  align-items: center;
}
.pagination-container {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}
</style>
