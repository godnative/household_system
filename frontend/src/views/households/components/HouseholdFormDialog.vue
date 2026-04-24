<template>
  <el-dialog :model-value="modelValue" :title="isEdit ? '编辑家庭' : '新建家庭'" width="500px" @update:model-value="emit('update:modelValue', $event)">
    <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
      <el-form-item label="堂区" prop="village_id">
        <el-select v-model="form.village_id" placeholder="请选择堂区" style="width: 100%">
          <el-option v-for="v in villages" :key="v.id" :label="v.name" :value="v.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="地块号" prop="plot_number">
        <el-input-number v-model="form.plot_number" :min="1" style="width: 100%" />
      </el-form-item>
      <el-form-item label="地址" prop="address">
        <el-input v-model="form.address" placeholder="请输入地址" />
      </el-form-item>
      <el-form-item label="电话">
        <el-input v-model="form.phone" placeholder="请输入电话" />
      </el-form-item>
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

import { householdApi } from '../../../api/households'
import type { VillageListItem } from '../../../api/villages'
import type { HouseholdListItem } from '../../../api/households'

const props = defineProps<{
  modelValue: boolean
  household: HouseholdListItem | null
  villages: VillageListItem[]
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  saved: []
}>()

const formRef = ref()
const submitting = ref(false)

const isEdit = computed(() => !!props.household)

const form = reactive({
  village_id: undefined as number | undefined,
  plot_number: 1,
  address: '',
  phone: '',
})

const rules = {
  village_id: [{ required: true, message: '请选择堂区', trigger: 'change' }],
  plot_number: [{ required: true, message: '请输入地块号', trigger: 'blur' }],
  address: [{ required: true, message: '请输入地址', trigger: 'blur' }],
}

watch(() => props.modelValue, (val) => {
  if (val) {
    if (props.household) {
      form.village_id = props.household.village_id
      form.plot_number = props.household.plot_number
      form.address = props.household.address
      form.phone = props.household.phone || ''
    } else {
      form.village_id = undefined
      form.plot_number = 1
      form.address = ''
      form.phone = ''
    }
  }
})

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
    }

    if (isEdit.value && props.household) {
      await householdApi.update(props.household.id, data)
      ElMessage.success('更新成功')
    } else {
      await householdApi.create(data)
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
