<template>
  <div v-loading="loading" class="member-detail-card">
    <el-empty v-if="!member && !loading" description="请选择成员" />
    <template v-else-if="member">
      <div class="card-actions">
        <el-button v-if="canEdit" type="primary" @click="$emit('edit')">编辑</el-button>
        <el-button v-if="canEdit" @click="$emit('set-head')">设为户主</el-button>
        <el-button @click="$emit('print')">打印</el-button>
      </div>

      <el-row :gutter="16" class="basic-header">
        <el-col :span="6">
          <div class="photo-wrapper">
            <img v-if="resolvedPhotoUrl" :src="resolvedPhotoUrl" alt="成员照片" class="member-photo" />
            <div v-else class="photo-placeholder">暂无照片</div>
          </div>
        </el-col>
        <el-col :span="18">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="姓名">{{ member.name }}</el-descriptions-item>
            <el-descriptions-item label="性别">{{ member.gender }}</el-descriptions-item>
            <el-descriptions-item label="圣名">{{ member.baptismal_name || '-' }}</el-descriptions-item>
            <el-descriptions-item label="与户主关系">{{ member.relation_to_head || '-' }}</el-descriptions-item>
            <el-descriptions-item label="出生日期">{{ member.birth_date || '-' }}</el-descriptions-item>
            <el-descriptions-item label="文化程度">{{ member.education || '-' }}</el-descriptions-item>
            <el-descriptions-item label="何时迁入">{{ member.move_in_date || '-' }}</el-descriptions-item>
            <el-descriptions-item label="从事职业">{{ member.occupation || '-' }}</el-descriptions-item>
            <el-descriptions-item label="教籍证件编号">{{ member.church_id || '-' }}</el-descriptions-item>
            <el-descriptions-item label="所属善会">{{ member.association || '-' }}</el-descriptions-item>
          </el-descriptions>
        </el-col>
      </el-row>

      <el-tabs>
        <el-tab-pane label="圣洗">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="施行人">{{ member.baptism_priest || '-' }}</el-descriptions-item>
            <el-descriptions-item label="代父/母">{{ member.baptism_godparent || '-' }}</el-descriptions-item>
            <el-descriptions-item label="领洗时间">{{ member.baptism_date || '-' }}</el-descriptions-item>
            <el-descriptions-item label="初领圣体时间">{{ member.first_communion_date || '-' }}</el-descriptions-item>
            <el-descriptions-item label="备注" :span="2">{{ member.baptism_note || '-' }}</el-descriptions-item>
          </el-descriptions>
        </el-tab-pane>
        <el-tab-pane label="补礼">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="神父">{{ member.supplementary_priest || '-' }}</el-descriptions-item>
            <el-descriptions-item label="地点">{{ member.supplementary_place || '-' }}</el-descriptions-item>
            <el-descriptions-item label="日期">{{ member.supplementary_date || '-' }}</el-descriptions-item>
          </el-descriptions>
        </el-tab-pane>
        <el-tab-pane label="坚振">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="年月日">{{ member.confirmation_date || '-' }}</el-descriptions-item>
            <el-descriptions-item label="施行人">{{ member.confirmation_priest || '-' }}</el-descriptions-item>
            <el-descriptions-item label="代父/母">{{ member.confirmation_godparent || '-' }}</el-descriptions-item>
            <el-descriptions-item label="圣名">{{ member.confirmation_name || '-' }}</el-descriptions-item>
            <el-descriptions-item label="年龄">{{ member.confirmation_age || '-' }}</el-descriptions-item>
            <el-descriptions-item label="地点">{{ member.confirmation_place || '-' }}</el-descriptions-item>
          </el-descriptions>
        </el-tab-pane>
        <el-tab-pane label="婚配">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="年月日">{{ member.marriage_date || '-' }}</el-descriptions-item>
            <el-descriptions-item label="主礼神父">{{ member.marriage_priest || '-' }}</el-descriptions-item>
            <el-descriptions-item label="证人">{{ member.marriage_witness || '-' }}</el-descriptions-item>
            <el-descriptions-item label="宽免事项">{{ member.marriage_dispensation_item || '-' }}</el-descriptions-item>
            <el-descriptions-item label="宽免神父">{{ member.marriage_dispensation_priest || '-' }}</el-descriptions-item>
            <el-descriptions-item label="地点">{{ member.marriage_place || '-' }}</el-descriptions-item>
          </el-descriptions>
        </el-tab-pane>
        <el-tab-pane label="病人傅油与其他">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="傅油日期">{{ member.anointing_date || '-' }}</el-descriptions-item>
            <el-descriptions-item label="施行人">{{ member.anointing_priest || '-' }}</el-descriptions-item>
            <el-descriptions-item label="地点">{{ member.anointing_place || '-' }}</el-descriptions-item>
            <el-descriptions-item label="死亡日期">{{ member.death_date || '-' }}</el-descriptions-item>
            <el-descriptions-item label="死亡年龄">{{ member.death_age || '-' }}</el-descriptions-item>
            <el-descriptions-item label="备注" :span="2">{{ member.note || '-' }}</el-descriptions-item>
          </el-descriptions>
        </el-tab-pane>
      </el-tabs>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

import type { MemberDetail } from '../../../api/members'

const props = defineProps<{
  member: MemberDetail | null
  loading: boolean
  canEdit: boolean
}>()

defineEmits<{
  edit: []
  'set-head': []
  print: []
}>()

const resolvedPhotoUrl = computed(() => {
  if (!props.member?.photo) return ''
  if (props.member.photo.startsWith('http://') || props.member.photo.startsWith('https://')) return props.member.photo
  if (props.member.photo.startsWith('/')) {
    const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'
    return `${baseUrl}${props.member.photo}`
  }
  return props.member.photo
})
</script>

<style scoped>
.member-detail-card {
  min-height: 420px;
}

.card-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-bottom: 16px;
}

.basic-header {
  margin-bottom: 16px;
}

.photo-wrapper {
  width: 140px;
  height: 186px;
  border: 1px solid #dcdfe6;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fafafa;
}

.member-photo {
  width: 120px;
  height: 160px;
  object-fit: cover;
}

.photo-placeholder {
  color: #909399;
  font-size: 14px;
}
</style>
