<template>
  <PageContainer title="家庭管理">
    <div class="household-management">
      <div class="left-panel">
        <div class="panel-header">
          <span class="panel-title">家庭列表</span>
          <el-select v-model="filterVillageId" placeholder="选择堂区" clearable size="small" style="width: 150px" @change="loadHouseholds">
            <el-option v-for="v in villages" :key="v.id" :label="v.name" :value="v.id" />
          </el-select>
        </div>
        <div class="panel-toolbar">
          <el-input v-model="searchText" placeholder="搜索地址/户主" clearable size="small" @keyup.enter="loadHouseholds">
            <template #append>
              <el-button @click="loadHouseholds">查询</el-button>
            </template>
          </el-input>
        </div>
        <div class="panel-toolbar">
          <el-button v-if="authStore.hasPermission('household_manage')" type="primary" size="small" @click="handleCreateHousehold">
            新建家庭
          </el-button>
        </div>
        <el-table
          ref="householdTableRef"
          v-loading="householdLoading"
          :data="households"
          stripe
          highlight-current-row
          size="small"
          @current-change="handleHouseholdSelect"
        >
          <el-table-column prop="id" label="ID" width="60" />
          <el-table-column prop="head_of_household" label="户主" width="80">
            <template #default="{ row }">
              {{ row.head_of_household || '未设置' }}
            </template>
          </el-table-column>
          <el-table-column prop="address" label="地址" min-width="120" show-overflow-tooltip />
          <el-table-column label="成员" width="50">
            <template #default="{ row }">
              {{ row.member_count || 0 }}
            </template>
          </el-table-column>
          <el-table-column v-if="authStore.hasPermission('household_manage')" label="操作" width="120" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" @click.stop="handleEditHousehold(row)">编辑</el-button>
              <el-button link type="danger" @click.stop="handleDeleteHousehold(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
        <div class="panel-pagination">
          <el-pagination
            v-model:current-page="householdPage"
            :page-size="20"
            :total="householdTotal"
            layout="prev, pager, next"
            small
            @current-change="loadHouseholds"
          />
        </div>
      </div>

      <div class="right-panel">
        <div class="panel-header">
          <span class="panel-title">成员管理</span>
          <el-button
            v-if="selectedHousehold && authStore.hasPermission('member_manage')"
            type="primary"
            size="small"
            @click="handleCreateMember"
          >
            新建成员
          </el-button>
        </div>

        <div v-if="!selectedHousehold" class="empty-state">
          <el-empty description="请先选择一个家庭" />
        </div>

        <div v-else class="member-tabs-container">
          <div class="selected-household-meta">
            <span>当前家庭：{{ selectedHousehold.address }}</span>
            <span>户主：{{ selectedHousehold.head_of_household || '未设置' }}</span>
          </div>
          <el-tabs v-model="activeMemberTab" type="card" closable @tab-remove="handleRemoveMemberTab">
            <el-tab-pane
              v-for="member in householdMembers"
              :key="member.id"
              :label="member.name"
              :name="String(member.id)"
            >
              <MemberDetailCard
                :member="memberDetail"
                :loading="memberDetailLoading"
                :can-edit="authStore.hasPermission('member_manage')"
                @edit="handleEditMember"
                @set-head="handleSetAsHead"
                @print="handlePrintMember"
              />
            </el-tab-pane>
          </el-tabs>
        </div>
      </div>
    </div>

    <HouseholdFormDialog
      v-model="householdFormVisible"
      :household="editingHousehold"
      :villages="villages"
      @saved="handleHouseholdSaved"
    />

    <MemberFormDialog
      v-model="memberFormVisible"
      :member="editingMember"
      :household-id="selectedHousehold?.id"
      :households="households"
      @saved="handleMemberSaved"
    />
  </PageContainer>
</template>

<script setup lang="ts">
import { nextTick, onMounted, ref, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRouter } from 'vue-router'

import { householdApi, type HouseholdDetail, type HouseholdListItem } from '../../api/households'
import { memberApi, type MemberDetail, type MemberListItem } from '../../api/members'
import { villageApi, type VillageListItem } from '../../api/villages'
import PageContainer from '../../components/PageContainer.vue'
import { useAuthStore } from '../../stores/auth'
import HouseholdFormDialog from './components/HouseholdFormDialog.vue'
import MemberFormDialog from './components/MemberFormDialog.vue'
import MemberDetailCard from './components/MemberDetailCard.vue'

const router = useRouter()
const authStore = useAuthStore()
const householdTableRef = ref()

const villages = ref<VillageListItem[]>([])
const filterVillageId = ref<number | null>(null)

const households = ref<HouseholdListItem[]>([])
const householdLoading = ref(false)
const householdPage = ref(1)
const householdTotal = ref(0)
const searchText = ref('')
const selectedHousehold = ref<HouseholdListItem | null>(null)

const householdMembers = ref<MemberListItem[]>([])
const memberDetail = ref<MemberDetail | null>(null)
const memberDetailLoading = ref(false)
const activeMemberTab = ref('')

const householdFormVisible = ref(false)
const memberFormVisible = ref(false)
const editingHousehold = ref<HouseholdListItem | null>(null)
const editingMember = ref<MemberDetail | null>(null)

const loadVillages = async () => {
  try {
    const res = await villageApi.list()
    villages.value = res.data.items
  } catch (error) {
    console.error('加载堂区失败:', error)
  }
}

const loadHouseholds = async () => {
  householdLoading.value = true
  try {
    const params: Record<string, unknown> = {
      page: householdPage.value,
      page_size: 20,
    }
    if (filterVillageId.value) params.village_id = filterVillageId.value
    if (searchText.value) params.search = searchText.value

    const res = await householdApi.list(params as { village_id?: number; search?: string; page?: number; page_size?: number })
    households.value = res.data.items
    householdTotal.value = res.data.meta.total

    const selectedId = selectedHousehold.value?.id
    if (!selectedId) {
      if (households.value.length > 0) {
        await nextTick()
        householdTableRef.value?.setCurrentRow(households.value[0])
      }
      return
    }

    const matched = households.value.find(item => item.id === selectedId)
    if (matched) {
      selectedHousehold.value = matched
      await nextTick()
      householdTableRef.value?.setCurrentRow(matched)
    } else if (households.value.length > 0) {
      selectedHousehold.value = null
      await nextTick()
      householdTableRef.value?.setCurrentRow(households.value[0])
    } else {
      selectedHousehold.value = null
      householdMembers.value = []
      memberDetail.value = null
      activeMemberTab.value = ''
    }
  } catch (error) {
    console.error('加载家庭失败:', error)
  } finally {
    householdLoading.value = false
  }
}

const handleHouseholdSelect = async (row: HouseholdListItem | null) => {
  selectedHousehold.value = row
  if (row) {
    await loadHouseholdMembers(row.id)
  } else {
    householdMembers.value = []
    memberDetail.value = null
    activeMemberTab.value = ''
  }
}

const loadHouseholdMembers = async (householdId: number) => {
  try {
    const res = await memberApi.list({ household_id: householdId, page_size: 100 })
    householdMembers.value = res.data.items

    if (householdMembers.value.length > 0) {
      const currentMemberExists = householdMembers.value.some(item => String(item.id) === activeMemberTab.value)
      const targetId = currentMemberExists ? Number(activeMemberTab.value) : householdMembers.value[0].id
      activeMemberTab.value = String(targetId)
      await loadMemberDetail(targetId)
    } else {
      activeMemberTab.value = ''
      memberDetail.value = null
    }
  } catch (error) {
    console.error('加载成员失败:', error)
    householdMembers.value = []
    activeMemberTab.value = ''
    memberDetail.value = null
  }
}

const loadMemberDetail = async (memberId: number) => {
  memberDetailLoading.value = true
  try {
    const res = await memberApi.get(memberId)
    memberDetail.value = res.data
  } catch (error) {
    console.error('加载成员详情失败:', error)
    memberDetail.value = null
  } finally {
    memberDetailLoading.value = false
  }
}

watch(activeMemberTab, (newVal) => {
  if (newVal) {
    loadMemberDetail(Number(newVal))
  }
})

const handleRemoveMemberTab = async (tabName: string) => {
  const memberId = Number(tabName)
  const member = householdMembers.value.find(m => m.id === memberId)

  try {
    await ElMessageBox.confirm(`确定要删除成员"${member?.name}"吗？`, '确认删除', { type: 'warning' })
    await memberApi.delete(memberId)
    ElMessage.success('删除成功')
    if (selectedHousehold.value) {
      await loadHouseholdMembers(selectedHousehold.value.id)
      await loadHouseholds()
    }
  } catch {}
}

const handleCreateHousehold = () => {
  editingHousehold.value = null
  householdFormVisible.value = true
}

const handleEditHousehold = (row: HouseholdListItem) => {
  editingHousehold.value = row
  householdFormVisible.value = true
}

const handleDeleteHousehold = async (row: HouseholdListItem) => {
  try {
    await ElMessageBox.confirm(`确定要删除家庭"${row.address}"吗？`, '确认删除', { type: 'warning' })
    await householdApi.delete(row.id)
    ElMessage.success('删除成功')
    if (selectedHousehold.value?.id === row.id) {
      selectedHousehold.value = null
      householdMembers.value = []
      memberDetail.value = null
      activeMemberTab.value = ''
    }
    await loadHouseholds()
  } catch {}
}

const handleHouseholdSaved = async () => {
  await loadHouseholds()
}

const handleCreateMember = () => {
  if (!selectedHousehold.value) return
  editingMember.value = null
  memberFormVisible.value = true
}

const handleEditMember = () => {
  if (!memberDetail.value) return
  editingMember.value = { ...memberDetail.value }
  memberFormVisible.value = true
}

const handleSetAsHead = async () => {
  if (!memberDetail.value || !selectedHousehold.value) return

  try {
    await ElMessageBox.confirm(`确定要将"${memberDetail.value.name}"设为户主吗？`, '确认操作', { type: 'info' })
    await memberApi.setAsHead(memberDetail.value.id)
    ElMessage.success('已设为户主')
    await loadHouseholds()
    await loadHouseholdMembers(selectedHousehold.value.id)
  } catch {}
}

const handlePrintMember = () => {
  if (!memberDetail.value) return
  router.push({
    path: '/print',
    query: { member_id: memberDetail.value.id },
  })
}

const handleMemberSaved = async () => {
  if (selectedHousehold.value) {
    await loadHouseholdMembers(selectedHousehold.value.id)
    await loadHouseholds()
  }
}

onMounted(() => {
  loadVillages()
  loadHouseholds()
})
</script>

<style scoped>
.household-management {
  display: flex;
  height: calc(100vh - 180px);
  gap: 16px;
}

.left-panel {
  width: 460px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  background: #fff;
}

.right-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  background: #fff;
  overflow: hidden;
}

.panel-header {
  padding: 12px 16px;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #f5f7fa;
}

.panel-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.panel-toolbar {
  padding: 8px 16px;
  border-bottom: 1px solid #ebeef5;
}

.panel-pagination {
  padding: 8px 16px;
  border-top: 1px solid #ebeef5;
  display: flex;
  justify-content: center;
}

.empty-state {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.member-tabs-container {
  flex: 1;
  overflow: auto;
  padding: 16px;
}

.selected-household-meta {
  display: flex;
  gap: 24px;
  margin-bottom: 12px;
  color: #606266;
  font-size: 14px;
}

:deep(.el-table) {
  flex: 1;
  overflow: auto;
}

:deep(.el-tabs__content) {
  padding: 0;
}

:deep(.el-tab-pane) {
  height: 100%;
}
</style>
