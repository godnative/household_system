<template>
  <PageContainer title="搜索">
    <div class="search-bar">
      <el-radio-group v-model="searchType" style="margin-right: 16px">
        <el-radio-button value="household">家庭搜索</el-radio-button>
        <el-radio-button value="member">成员搜索</el-radio-button>
      </el-radio-group>
      <el-input
        v-model="keyword"
        :placeholder="searchType === 'household' ? '输入户主姓名、地址、电话等' : '输入姓名、圣名、教籍编号等'"
        clearable
        style="width: 300px; margin-right: 12px"
        @keyup.enter="handleSearch"
      />
      <el-button type="primary" :loading="loading" @click="handleSearch">搜索</el-button>
      <el-button @click="handleReset">重置</el-button>
    </div>

    <!-- 家庭搜索结果 -->
    <div v-if="searchType === 'household'" class="results-section">
      <el-table v-loading="loading" :data="householdResults" stripe>
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
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="viewHousehold(row)">查看</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 成员搜索结果 -->
    <div v-if="searchType === 'member'" class="results-section">
      <el-table v-loading="loading" :data="memberResults" stripe>
        <el-table-column prop="village_name" label="堂区" width="100" />
        <el-table-column prop="name" label="姓名" width="100" />
        <el-table-column prop="gender" label="性别" width="60" />
        <el-table-column prop="baptismal_name" label="圣名" width="100" />
        <el-table-column prop="household_address" label="所属家庭" min-width="180" />
        <el-table-column prop="relation_to_head" label="与户主关系" width="100" />
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="viewMember(row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <div v-if="total > 0" class="pagination-container">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSearch"
        @current-change="handleSearch"
      />
    </div>

    <!-- 家庭详情对话框 -->
    <el-dialog v-model="householdDetailVisible" title="家庭详情" width="700px">
      <el-descriptions v-if="currentHousehold" :column="2" border>
        <el-descriptions-item label="堂区">{{ currentHousehold.village_name }}</el-descriptions-item>
        <el-descriptions-item label="地块号">{{ currentHousehold.plot_number }}</el-descriptions-item>
        <el-descriptions-item label="地址" :span="2">{{ currentHousehold.address }}</el-descriptions-item>
        <el-descriptions-item label="户主">{{ currentHousehold.head_of_household || '-' }}</el-descriptions-item>
        <el-descriptions-item label="电话">{{ currentHousehold.phone || '-' }}</el-descriptions-item>
      </el-descriptions>

      <h4 style="margin-top: 20px; margin-bottom: 12px">成员列表</h4>
      <el-table v-loading="membersLoading" :data="householdMembers" stripe size="small">
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
    </el-dialog>

    <!-- 成员详情对话框 -->
    <el-dialog v-model="memberDetailVisible" title="成员详情" width="700px">
      <el-tabs v-if="currentMember">
        <el-tab-pane label="基本信息">
          <el-descriptions :column="2" border>
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
          <el-descriptions :column="2" border>
            <el-descriptions-item label="洗礼日期">{{ currentMember.baptism_date || '-' }}</el-descriptions-item>
            <el-descriptions-item label="付洗神父">{{ currentMember.baptism_priest || '-' }}</el-descriptions-item>
            <el-descriptions-item label="代父/代母">{{ currentMember.baptism_godparent || '-' }}</el-descriptions-item>
            <el-descriptions-item label="备注">{{ currentMember.baptism_note || '-' }}</el-descriptions-item>
          </el-descriptions>
        </el-tab-pane>
        <el-tab-pane label="坚振">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="坚振日期">{{ currentMember.confirmation_date || '-' }}</el-descriptions-item>
            <el-descriptions-item label="坚振神父">{{ currentMember.confirmation_priest || '-' }}</el-descriptions-item>
            <el-descriptions-item label="代父/代母">{{ currentMember.confirmation_godparent || '-' }}</el-descriptions-item>
            <el-descriptions-item label="坚振圣名">{{ currentMember.confirmation_name || '-' }}</el-descriptions-item>
          </el-descriptions>
        </el-tab-pane>
      </el-tabs>
    </el-dialog>
  </PageContainer>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

import { householdApi, type HouseholdDetail, type HouseholdListItem } from '../../api/households'
import { memberApi, type MemberDetail, type MemberListItem } from '../../api/members'
import { searchApi, type HouseholdSearchResult, type MemberSearchResult } from '../../api/search'
import PageContainer from '../../components/PageContainer.vue'

const searchType = ref<'household' | 'member'>('household')
const keyword = ref('')
const loading = ref(false)
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)

const householdResults = ref<HouseholdSearchResult[]>([])
const memberResults = ref<MemberSearchResult[]>([])

// Household detail
const householdDetailVisible = ref(false)
const currentHousehold = ref<HouseholdDetail | null>(null)
const householdMembers = ref<MemberListItem[]>([])
const membersLoading = ref(false)

// Member detail
const memberDetailVisible = ref(false)
const currentMember = ref<MemberDetail | null>(null)

const handleSearch = async () => {
  if (!keyword.value.trim()) {
    ElMessage.warning('请输入搜索关键词')
    return
  }

  loading.value = true
  try {
    if (searchType.value === 'household') {
      const res = await searchApi.households({
        keyword: keyword.value.trim(),
        page: currentPage.value,
        page_size: pageSize.value,
      })
      householdResults.value = res.data.items
      total.value = res.data.meta.total
    } else {
      const res = await searchApi.members({
        keyword: keyword.value.trim(),
        page: currentPage.value,
        page_size: pageSize.value,
      })
      memberResults.value = res.data.items
      total.value = res.data.meta.total
    }

    if (total.value === 0) {
      ElMessage.info('未找到匹配的结果')
    }
  } catch (error) {
    console.error('搜索失败:', error)
    ElMessage.error('搜索失败')
  } finally {
    loading.value = false
  }
}

const handleReset = () => {
  keyword.value = ''
  householdResults.value = []
  memberResults.value = []
  total.value = 0
  currentPage.value = 1
}

const viewHousehold = async (row: HouseholdSearchResult) => {
  try {
    const res = await householdApi.get(row.id)
    currentHousehold.value = res.data
    householdMembers.value = res.data.members
    householdDetailVisible.value = true
  } catch (error) {
    ElMessage.error('获取家庭详情失败')
  }
}

const viewMember = async (row: MemberSearchResult) => {
  try {
    const res = await memberApi.get(row.id)
    currentMember.value = res.data
    memberDetailVisible.value = true
  } catch (error) {
    ElMessage.error('获取成员详情失败')
  }
}
</script>

<style scoped>
.search-bar {
  margin-bottom: 16px;
  display: flex;
  align-items: center;
}
.results-section {
  margin-top: 16px;
}
.pagination-container {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}
</style>
