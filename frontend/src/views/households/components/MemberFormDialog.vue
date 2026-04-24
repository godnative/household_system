<template>
  <el-dialog :model-value="modelValue" :title="isEdit ? '编辑成员' : '新建成员'" width="920px" @update:model-value="emit('update:modelValue', $event)">
    <el-form ref="formRef" :model="form" :rules="rules" label-width="110px">
      <el-tabs>
        <el-tab-pane label="基本信息">
          <el-row :gutter="16">
            <el-col :span="12">
              <el-form-item label="所属家庭" prop="household_id">
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
              <el-form-item label="出生日期">
                <el-date-picker v-model="form.birth_date" type="date" value-format="YYYY-MM-DD" placeholder="请选择出生日期" style="width: 100%" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="圣名">
                <el-input v-model="form.baptismal_name" placeholder="请输入圣名" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="与户主关系">
                <el-input v-model="form.relation_to_head" placeholder="请输入与户主关系" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="文化程度">
                <el-input v-model="form.education" placeholder="请输入文化程度" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="何时迁入">
                <el-date-picker v-model="form.move_in_date" type="date" value-format="YYYY-MM-DD" placeholder="请选择迁入日期" style="width: 100%" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="从事职业">
                <el-input v-model="form.occupation" placeholder="请输入职业" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="教籍证件编号">
                <el-input v-model="form.church_id" placeholder="请输入教籍证件编号" />
              </el-form-item>
            </el-col>
            <el-col :span="24">
              <el-form-item label="成员照片">
                <div class="photo-upload-row">
                  <el-upload
                    :show-file-list="false"
                    :http-request="handlePhotoUpload"
                    accept="image/jpeg,image/png,image/webp"
                  >
                    <el-button :loading="uploadingPhoto">上传照片</el-button>
                  </el-upload>
                  <el-input v-model="form.photo" placeholder="上传后自动回填照片路径" readonly />
                </div>
                <img v-if="form.photo" :src="resolvePhotoUrl(form.photo)" alt="成员照片预览" class="photo-preview" />
              </el-form-item>
            </el-col>
          </el-row>
        </el-tab-pane>

        <el-tab-pane label="圣洗">
          <el-row :gutter="16">
            <el-col :span="12">
              <el-form-item label="施行人">
                <el-input v-model="form.baptism_priest" placeholder="请输入施行人" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="代父/母">
                <el-input v-model="form.baptism_godparent" placeholder="请输入代父/母" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="领洗时间">
                <el-date-picker v-model="form.baptism_date" type="date" value-format="YYYY-MM-DD" placeholder="请选择领洗时间" style="width: 100%" />
              </el-form-item>
            </el-col>
            <el-col :span="24">
              <el-form-item label="备注">
                <el-input v-model="form.baptism_note" type="textarea" :rows="3" placeholder="请输入圣洗备注" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="初领圣体时间">
                <el-date-picker v-model="form.first_communion_date" type="date" value-format="YYYY-MM-DD" placeholder="请选择初领圣体时间" style="width: 100%" />
              </el-form-item>
            </el-col>
          </el-row>
        </el-tab-pane>

        <el-tab-pane label="补礼">
          <el-row :gutter="16">
            <el-col :span="12">
              <el-form-item label="神父">
                <el-input v-model="form.supplementary_priest" placeholder="请输入补礼神父" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="地点">
                <el-input v-model="form.supplementary_place" placeholder="请输入补礼地点" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="日期">
                <el-date-picker v-model="form.supplementary_date" type="date" value-format="YYYY-MM-DD" placeholder="请选择补礼日期" style="width: 100%" />
              </el-form-item>
            </el-col>
          </el-row>
        </el-tab-pane>

        <el-tab-pane label="坚振">
          <el-row :gutter="16">
            <el-col :span="12">
              <el-form-item label="年月日">
                <el-date-picker v-model="form.confirmation_date" type="date" value-format="YYYY-MM-DD" placeholder="请选择坚振日期" style="width: 100%" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="施行人">
                <el-input v-model="form.confirmation_priest" placeholder="请输入坚振施行人" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="代父/母">
                <el-input v-model="form.confirmation_godparent" placeholder="请输入代父/母" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="圣名">
                <el-input v-model="form.confirmation_name" placeholder="请输入坚振圣名" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="年龄">
                <el-input-number v-model="form.confirmation_age" :min="0" style="width: 100%" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="地点">
                <el-input v-model="form.confirmation_place" placeholder="请输入坚振地点" />
              </el-form-item>
            </el-col>
          </el-row>
        </el-tab-pane>

        <el-tab-pane label="婚配">
          <el-row :gutter="16">
            <el-col :span="12">
              <el-form-item label="年月日">
                <el-date-picker v-model="form.marriage_date" type="date" value-format="YYYY-MM-DD" placeholder="请选择婚配日期" style="width: 100%" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="主礼神父">
                <el-input v-model="form.marriage_priest" placeholder="请输入主礼神父" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="证人">
                <el-input v-model="form.marriage_witness" placeholder="请输入证人" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="宽免事项">
                <el-input v-model="form.marriage_dispensation_item" placeholder="请输入宽免事项" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="宽免神父">
                <el-input v-model="form.marriage_dispensation_priest" placeholder="请输入宽免神父" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="地点">
                <el-input v-model="form.marriage_place" placeholder="请输入婚配地点" />
              </el-form-item>
            </el-col>
          </el-row>
        </el-tab-pane>

        <el-tab-pane label="病人傅油与其他">
          <el-row :gutter="16">
            <el-col :span="12">
              <el-form-item label="傅油日期">
                <el-date-picker v-model="form.anointing_date" type="date" value-format="YYYY-MM-DD" placeholder="请选择傅油日期" style="width: 100%" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="施行人">
                <el-input v-model="form.anointing_priest" placeholder="请输入傅油施行人" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="地点">
                <el-input v-model="form.anointing_place" placeholder="请输入傅油地点" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="死亡日期">
                <el-date-picker v-model="form.death_date" type="date" value-format="YYYY-MM-DD" placeholder="请选择死亡日期" style="width: 100%" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="死亡年龄">
                <el-input-number v-model="form.death_age" :min="0" style="width: 100%" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="所属善会">
                <el-input v-model="form.association" placeholder="请输入所属善会" />
              </el-form-item>
            </el-col>
            <el-col :span="24">
              <el-form-item label="备注">
                <el-input v-model="form.note" type="textarea" :rows="4" placeholder="请输入备注" />
              </el-form-item>
            </el-col>
          </el-row>
        </el-tab-pane>
      </el-tabs>
    </el-form>
    <template #footer>
      <el-button @click="emit('update:modelValue', false)">取消</el-button>
      <el-button type="primary" :loading="submitting" @click="handleSubmit">确定</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import type { UploadRequestOptions } from 'element-plus'

import apiClient from '../../../api/client'
import { memberApi, type MemberCreate, type MemberDetail } from '../../../api/members'
import type { HouseholdListItem } from '../../../api/households'

const props = defineProps<{
  modelValue: boolean
  member: MemberDetail | null
  householdId?: number
  households: HouseholdListItem[]
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  saved: []
}>()

const formRef = ref()
const submitting = ref(false)
const uploadingPhoto = ref(false)
const isEdit = computed(() => !!props.member)

const createEmptyForm = (): Required<Omit<MemberCreate, 'confirmation_age' | 'death_age'>> & { confirmation_age: number | null; death_age: number | null } => ({
  household_id: props.householdId || 0,
  name: '',
  gender: '男',
  birth_date: '',
  baptismal_name: '',
  relation_to_head: '',
  education: '',
  move_in_date: '',
  occupation: '',
  church_id: '',
  baptism_priest: '',
  baptism_godparent: '',
  baptism_date: '',
  baptism_note: '',
  first_communion_date: '',
  supplementary_priest: '',
  supplementary_place: '',
  supplementary_date: '',
  photo: '',
  confirmation_date: '',
  confirmation_priest: '',
  confirmation_godparent: '',
  confirmation_name: '',
  confirmation_age: null,
  confirmation_place: '',
  marriage_date: '',
  marriage_priest: '',
  marriage_witness: '',
  marriage_dispensation_item: '',
  marriage_dispensation_priest: '',
  marriage_place: '',
  anointing_date: '',
  anointing_priest: '',
  anointing_place: '',
  death_date: '',
  death_age: null,
  association: '',
  note: '',
})

const form = reactive(createEmptyForm())

const rules = {
  household_id: [{ required: true, message: '请选择家庭', trigger: 'change' }],
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  gender: [{ required: true, message: '请选择性别', trigger: 'change' }],
}

const resolvePhotoUrl = (photo: string) => {
  if (photo.startsWith('http://') || photo.startsWith('https://')) return photo
  if (photo.startsWith('/')) {
    const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'
    return `${baseUrl}${photo}`
  }
  return photo
}

const assignForm = (member: MemberDetail | null) => {
  const base = createEmptyForm()
  const source = member
    ? {
        ...base,
        ...member,
        household_id: member.household_id,
        birth_date: member.birth_date || '',
        baptismal_name: member.baptismal_name || '',
        relation_to_head: member.relation_to_head || '',
        education: member.education || '',
        move_in_date: member.move_in_date || '',
        occupation: member.occupation || '',
        church_id: member.church_id || '',
        baptism_priest: member.baptism_priest || '',
        baptism_godparent: member.baptism_godparent || '',
        baptism_date: member.baptism_date || '',
        baptism_note: member.baptism_note || '',
        first_communion_date: member.first_communion_date || '',
        supplementary_priest: member.supplementary_priest || '',
        supplementary_place: member.supplementary_place || '',
        supplementary_date: member.supplementary_date || '',
        photo: member.photo || '',
        confirmation_date: member.confirmation_date || '',
        confirmation_priest: member.confirmation_priest || '',
        confirmation_godparent: member.confirmation_godparent || '',
        confirmation_name: member.confirmation_name || '',
        confirmation_age: member.confirmation_age,
        confirmation_place: member.confirmation_place || '',
        marriage_date: member.marriage_date || '',
        marriage_priest: member.marriage_priest || '',
        marriage_witness: member.marriage_witness || '',
        marriage_dispensation_item: member.marriage_dispensation_item || '',
        marriage_dispensation_priest: member.marriage_dispensation_priest || '',
        marriage_place: member.marriage_place || '',
        anointing_date: member.anointing_date || '',
        anointing_priest: member.anointing_priest || '',
        anointing_place: member.anointing_place || '',
        death_date: member.death_date || '',
        death_age: member.death_age,
        association: member.association || '',
        note: member.note || '',
      }
    : { ...base, household_id: props.householdId || 0 }

  Object.assign(form, source)
}

watch(() => props.modelValue, (val) => {
  if (val) {
    assignForm(props.member)
  }
})

watch(() => props.householdId, (val) => {
  if (!props.member && val) {
    form.household_id = val
  }
})

const toPayload = (): MemberCreate => {
  const entries = Object.entries(form).filter(([, value]) => value !== '' && value !== null)
  return Object.fromEntries(entries) as MemberCreate
}

const handlePhotoUpload = async (options: UploadRequestOptions) => {
  const uploadFile = options.file as File
  const formData = new FormData()
  formData.append('file', uploadFile)
  formData.append('category', 'member-photo')

  uploadingPhoto.value = true
  try {
    const res = await apiClient.post('/api/v1/uploads', formData)
    form.photo = res.data.url
    ElMessage.success('照片上传成功')
    options.onSuccess?.(res.data)
  } catch (error: unknown) {
    const err = error as { response?: { data?: { detail?: string } } }
    ElMessage.error(err.response?.data?.detail || '照片上传失败')
    options.onError?.(error as Error)
  } finally {
    uploadingPhoto.value = false
  }
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
  } catch {
    return
  }

  submitting.value = true
  try {
    const payload = toPayload()
    if (isEdit.value && props.member) {
      await memberApi.update(props.member.id, payload)
      ElMessage.success('更新成功')
    } else {
      await memberApi.create(payload)
      ElMessage.success('创建成功')
    }
    emit('update:modelValue', false)
    emit('saved')
  } catch (error: unknown) {
    const err = error as { response?: { data?: { detail?: string } } }
    ElMessage.error(err.response?.data?.detail || '操作失败')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.photo-upload-row {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
}

.photo-upload-row :deep(.el-input) {
  flex: 1;
}

.photo-preview {
  margin-top: 12px;
  width: 120px;
  height: 160px;
  object-fit: cover;
  border: 1px solid #dcdfe6;
}
</style>
