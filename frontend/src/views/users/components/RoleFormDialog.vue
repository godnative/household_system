<template>
  <el-dialog
    :model-value="modelValue"
    :title="isEdit ? '编辑角色' : '新建角色'"
    width="500px"
    @update:model-value="emit('update:modelValue', $event)"
    @close="handleClose"
  >
    <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
      <el-form-item label="角色标识" prop="name">
        <el-input v-model="form.name" placeholder="请输入角色标识（英文）" :disabled="isEdit" />
      </el-form-item>
      <el-form-item label="角色名称" prop="description">
        <el-input v-model="form.description" placeholder="请输入角色名称（中文）" />
      </el-form-item>
      <el-form-item label="权限" prop="permission_ids">
        <el-checkbox-group v-model="form.permission_ids">
          <el-checkbox
            v-for="permission in permissions"
            :key="permission.id"
            :value="permission.id"
            :label="permission.id"
          >
            {{ permission.description || permission.name }}
          </el-checkbox>
        </el-checkbox-group>
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

import type { PermissionOption, RoleListItem } from '../../../api/roles'
import { roleApi } from '../../../api/roles'

interface Props {
  modelValue: boolean
  role: RoleListItem | null
  permissions: PermissionOption[]
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  success: []
}>()

const formRef = ref()
const submitting = ref(false)

const isEdit = computed(() => !!props.role)

const form = reactive({
  name: '',
  description: '',
  permission_ids: [] as number[],
})

const rules = {
  name: [{ required: true, message: '请输入角色标识', trigger: 'blur' }],
  description: [{ required: true, message: '请输入角色名称', trigger: 'blur' }],
}

watch(
  () => props.modelValue,
  (visible) => {
    if (visible && props.role) {
      form.name = props.role.name
      form.description = props.role.description || ''
      form.permission_ids = props.role.permissions.map((p) => p.id)
    }
  },
)

const handleClose = () => {
  formRef.value?.resetFields()
  form.name = ''
  form.description = ''
  form.permission_ids = []
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
  } catch {
    return
  }

  submitting.value = true
  try {
    if (isEdit.value && props.role) {
      await roleApi.update(props.role.id, {
        name: form.name,
        description: form.description,
        permission_ids: form.permission_ids,
      })
      ElMessage.success('角色更新成功')
    } else {
      await roleApi.create({
        name: form.name,
        description: form.description,
        permission_ids: form.permission_ids,
      })
      ElMessage.success('角色创建成功')
    }
    emit('update:modelValue', false)
    emit('success')
  } catch (error: unknown) {
    const err = error as { response?: { data?: { detail?: string } } }
    ElMessage.error(err.response?.data?.detail || '操作失败')
  } finally {
    submitting.value = false
  }
}
</script>
