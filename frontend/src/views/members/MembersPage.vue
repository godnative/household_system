<template>
  <PageContainer title="成员管理">
    <div class="toolbar">
      <el-select v-model="filterHouseholdId" placeholder="选择家庭" clearable style="width: 200px; margin-right: 12px" @change="loadMembers">
        <el-option v-for="h in households" :key="h.id" :label="`${h.village_name} - ${h.address}`" :value="h.id" />
      </el-select>
      <el-input
        v-model="searchText"
        placeholder="搜索姓名/圣名"
        clearable
        style="width: 200px; margin-right: 12px"
        @keyup.enter="loadMembers"
      />
      <el-button type="primary" @click="loadMembers">查询</el-button>
      <el-button v-if="authStore.hasPermission('member_manage')" type="primary" @click="handleCreate">
        新建成员
      </el-button>
    </div>

    <el-table v-loading="loading" :data="members" stripe>
      <el-table-column prop="name" label="姓名" width="100" />
      <el-table-column prop="gender" label="性别" width="60" />
      <el-table-column prop="baptismal_name" label="圣名" width="100" />
      <el-table-column prop="relation_to_head" label="与户主关系" width="100" />
      <el-table-column label="出生日期" width="120">
        <template #default="{ row }">
          {{ row.birth_date || '-' }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="handleView(row)">详情</el-button>
          <el-button v-if="authStore.hasPermission('member_manage')" size="small" @click="handleEdit(row)">
            编辑
          </el-button>
          <el-button
            v-if="authStore.hasPermission('member_manage')"
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
        @size-change="loadMembers"
        @current-change="loadMembers"
      />
    </div>

    <!-- 详情对话框 -->
    <el-dialog v-model="detailVisible" title="成员详情" width="700px">
      <el-tabs>
        <el-tab-pane label="基本信息">
          <el-descriptions v-if="currentMember" :column="2" border>
            <el-descriptions-item label="姓名">{{ currentMember.name }}</el-descriptions-item>
            <el-descriptions-item label="性别">{{ currentMember.gender }}</el-descriptions-item>
            <el-descriptions-item label="圣名">{{ currentMember.baptismal_name || '-' }}</el-descriptions-item>
            <el-descriptions-item label="与户主关系">{{ currentMember.relation_to_head || '-' }}</el-descriptions-item>
            <el-descriptions-item label="出生日期">{{ currentMember.birth_date || '-' }}</el-descriptions-item>
            <el-descriptions-item label="学历">{{ currentMember.education || '-' }}</el-descriptions-item>
            <el-descriptions-item label="职业">{{ currentMember.occupation || '-' }}</el-descriptions-item>
            <el-descriptions-item label="教籍编号">{{ currentMember.church_id || '-' }}</el-descriptions-item>
          </el-descriptions>
        </el-tab-pane>
        <el-tab-pane label="圣洗">
          <el-descriptions v-if="currentMember" :column="2" border>
            <el-descriptions-item label="洗礼日期">{{ currentMember.baptism_date || '-' }}</el-descriptions-item>
            <el-descriptions-item label="付洗神父">{{ currentMember.baptism_priest || '-' }}</el-descriptions-item>
            <el-descriptions-item label="代父/代母">{{ currentMember.baptism_godparent || '-' }}</el-descriptions-item>
            <el-descriptions-item label="备注">{{ currentMember.baptism_note || '-' }}</el-descriptions-item>
          </el-descriptions>
        </el-tab-pane>
        <el-tab-pane label="坚振">
          <el-descriptions v-if="currentMember" :column="2" border>
            <el-descriptions-item label="坚振日期">{{ currentMember.confirmation_date || '-' }}</el-descriptions-item>
            <el-descriptions-item label="坚振神父">{{ currentMember.confirmation_priest || '-' }}</el-descriptions-item>
            <el-descriptions-item label="代父/代母">{{ currentMember.confirmation_godparent || '-' }}</el-descriptions-item>
            <el-descriptions-item label="坚振圣名">{{ currentMember.confirmation_name || '-' }}</el-descriptions-item>
            <el-descriptions-item label="坚振年龄">{{ currentMember.confirmation_age || '-' }}</el-descriptions-item>
            <el-descriptions-item label="坚振地点">{{ currentMember.confirmation_place || '-' }}</el-descriptions-item>
          </el-descriptions>
        </el-tab-pane>
        <el-tab-pane label="婚配">
          <el-descriptions v-if="currentMember" :column="2" border>
            <el-descriptions-item label="婚配日期">{{ currentMember.marriage_date || '-' }}</el-descriptions-item>
            <el-descriptions-item label="证婚神父">{{ currentMember.marriage_priest || '-' }}</el-descriptions-item>
            <el-descriptions-item label="证婚人">{{ currentMember.marriage_witness || '-' }}</el-descriptions-item>
            <el-descriptions-item label="豁免项目">{{ currentMember.marriage_dispensation_item || '-' }}</el-descriptions-item>
            <el-descriptions-item label="豁免神父">{{ currentMember.marriage_dispensation_priest || '-' }}</el-descriptions-item>
            <el-descriptions-item label="婚配地点">{{ currentMember.marriage_place || '-' }}</el-descriptions-item>
          </el-descriptions>
        </el-tab-pane>
      </el-tabs>
    </el-dialog>

    <!-- 创建/编辑对话框 -->
    <el-dialog v-model="formVisible" :title="isEdit ? '编辑成员' : '新建成员'" width="700px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="家庭" prop="household_id">
              <el-select v-model="form.household_id" placeholder="请选择家庭" style="width: 100%">
                <el-option v-for="h in households" :key="h.id" :label="`${h.village_name} - ${h.address}`" :value="h.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="姓名" prop="name">
              <el-input v-model="form.name" placeholder="请输入姓名" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="性别" prop="gender">
              <el-radio-group v-model="form.gender">
                <el-radio value="男">男</el-radio>
                <el-radio value="女">女</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="圣名">
              <el-input v-model="form.baptismal_name" placeholder="请输入圣名" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="出生日期">
              <el-date-picker v-model="form.birth_date" type="date" placeholder="选择日期" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="与户主关系">
              <el-input v-model="form.relation_to_head" placeholder="如：户主、妻子、长子等" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="学历">
              <el-input v-model="form.education" placeholder="请输入学历" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="职业">
              <el-input v-model="form.occupation" placeholder="请输入职业" />
            </el-form-item>
          </el-col>
        </el-row>
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

import { householdApi, type HouseholdListItem } from '../../api/households'
import { memberApi, type MemberDetail, type MemberListItem } from '../../api/members'
import PageContainer from '../../components/PageContainer.vue'
import { useAuthStore } from '../../stores/auth'

const authStore = useAuthStore()
const loading = ref(false)
const members = ref<MemberListItem[]>([])
const households = ref<HouseholdListItem[]>([])
const filterHouseholdId = ref<number | null>(null)
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
const currentMember = ref<MemberDetail | null>(null)

const form = reactive({
  household_id: undefined as number | undefined,
  name: '',
  gender: '男',
  birth_date: null as string | null,
  baptismal_name: '',
  relation_to_head: '',
  education: '',
  occupation: '',
})

const rules = {
  household_id: [{ required: true, message: '请选择家庭', trigger: 'change' }],
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  gender: [{ required: true, message: '请选择性别', trigger: 'change' }],
}

const loadHouseholds = async () => {
  try {
    const res = await householdApi.list()
    households.value = res.data.items
  } catch (error) {
    console.error('加载家庭列表失败:', error)
  }
}

const loadMembers = async () => {
  loading.value = true
  try {
    const params: { household_id?: number; search?: string; page?: number; page_size?: number } = {
      page: currentPage.value,
      page_size: pageSize.value,
    }
    if (filterHouseholdId.value) params.household_id = filterHouseholdId.value
    if (searchText.value) params.search = searchText.value
    const res = await memberApi.list(params)
    members.value = res.data.items
    total.value = res.data.meta.total
  } catch (error) {
    console.error('加载成员列表失败:', error)
  } finally {
    loading.value = false
  }
}

const resetForm = () => {
  form.household_id = undefined
  form.name = ''
  form.gender = '男'
  form.birth_date = null
  form.baptismal_name = ''
  form.relation_to_head = ''
  form.education = ''
  form.occupation = ''
}

const handleCreate = () => {
  isEdit.value = false
  editingId.value = null
  resetForm()
  formVisible.value = true
}

const handleEdit = (row: MemberListItem) => {
  isEdit.value = true
  editingId.value = row.id
  // Load full details
  memberApi.get(row.id).then((res) => {
    const m = res.data
    form.household_id = m.household_id
    form.name = m.name
    form.gender = m.gender
    form.birth_date = m.birth_date
    form.baptismal_name = m.baptismal_name || ''
    form.relation_to_head = m.relation_to_head || ''
    form.education = m.education || ''
    form.occupation = m.occupation || ''
    formVisible.value = true
  })
}

const handleView = async (row: MemberListItem) => {
  try {
    const res = await memberApi.get(row.id)
    currentMember.value = res.data
    detailVisible.value = true
  } catch (error) {
    ElMessage.error('获取详情失败')
  }
}

const handleDelete = async (row: MemberListItem) => {
  try {
    await ElMessageBox.confirm(`确定要删除成员"${row.name}"吗？`, '确认删除', { type: 'warning' })
    await memberApi.delete(row.id)
    ElMessage.success('删除成功')
    loadMembers()
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
      household_id: form.household_id!,
      name: form.name,
      gender: form.gender,
      birth_date: form.birth_date || undefined,
      baptismal_name: form.baptismal_name || undefined,
      relation_to_head: form.relation_to_head || undefined,
      education: form.education || undefined,
      occupation: form.occupation || undefined,
    }

    if (isEdit.value && editingId.value) {
      await memberApi.update(editingId.value, data)
      ElMessage.success('更新成功')
    } else {
      await memberApi.create(data)
      ElMessage.success('创建成功')
    }
    formVisible.value = false
    loadMembers()
  } catch (error: unknown) {
    const err = error as { response?: { data?: { detail?: string } } }
    ElMessage.error(err.response?.data?.detail || '操作失败')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  loadHouseholds()
  loadMembers()
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
