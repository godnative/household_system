<template>
  <el-dialog
    :model-value="modelValue"
    :title="isEdit ? '编辑用户' : '新建用户'"
    width="500px"
    @update:model-value="emit('update:modelValue', $event)"
    @close="handleClose"
  >
    <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
      <el-form-item v-if="!isEdit" label="用户名" prop="username">
        <el-input v-model="form.username" placeholder="请输入用户名" />
      </el-form-item>
      <el-form-item v-if="!isEdit" label="密码" prop="password">
        <el-input
          v-model="form.password"
          type="password"
          placeholder="请输入密码"
          show-password
        />
      </el-form-item>
      <el-form-item label="角色" prop="role_id">
        <el-select v-model="form.role_id" placeholder="请选择角色" @change="handleRoleChange">
          <el-option
            v-for="role in roles"
            :key="role.id"
            :label="role.description || role.name"
            :value="role.id"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="状态" prop="is_active">
        <el-switch v-model="form.is_active" active-text="启用" inactive-text="停用" />
      </el-form-item>
      <el-form-item
        v-if="selectedRoleName === 'data_entry'"
        label="所属堂区"
        prop="village_id"
      >
        <el-select v-model="form.village_id" placeholder="请选择所属堂区">
          <el-option
            v-for="village in villages"
            :key="village.id"
            :label="village.name"
            :value="village.id"
          />
        </el-select>
      </el-form-item>
      <el-form-item
        v-if="selectedRoleName === 'observer'"
        label="可访问堂区"
        prop="accessible_village_ids"
      >
        <el-select
          v-model="form.accessible_village_ids"
          multiple
          placeholder="请选择可访问的堂区"
        >
          <el-option
            v-for="village in villages"
            :key="village.id"
            :label="village.name"
            :value="village.id"
          />
        </el-select>
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

import type { UserListItem, VillageOption } from '../../../api/users'
import { userApi } from '../../../api/users'

interface Props {
  modelValue: boolean
  user: UserListItem | null
  roles: { id: number; name: string; description: string }[]
  villages: VillageOption[]
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  success: []
}>()

const formRef = ref()
const submitting = ref(false)

const isEdit = computed(() => !!props.user)

const form = reactive({
  username: '',
  password: '',
  role_id: undefined as number | undefined,
  is_active: true,
  village_id: undefined as number | undefined,
  accessible_village_ids: [] as number[],
})

const selectedRoleName = computed(() => {
  const role = props.roles.find((r) => r.id === form.role_id)
  return role?.name
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
  role_id: [{ required: true, message: '请选择角色', trigger: 'change' }],
  village_id: [
    {
      validator: (_rule: unknown, value: number | undefined, callback: (error?: Error) => void) => {
        if (selectedRoleName.value === 'data_entry' && !value) {
          callback(new Error('录入员必须选择所属堂区'))
        } else {
          callback()
        }
      },
      trigger: 'change',
    },
  ],
}

watch(
  () => props.modelValue,
  (visible) => {
    if (visible && props.user) {
      form.username = props.user.username
      form.role_id = props.user.role.id
      form.is_active = props.user.is_active
      form.village_id = props.user.village_id ?? undefined
      form.accessible_village_ids = props.user.accessible_village_ids || []
    }
  },
)

const handleRoleChange = () => {
  // 切换角色时清空范围字段
  form.village_id = undefined
  form.accessible_village_ids = []
}

const handleClose = () => {
  formRef.value?.resetFields()
  form.username = ''
  form.password = ''
  form.role_id = undefined
  form.is_active = true
  form.village_id = undefined
  form.accessible_village_ids = []
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
  } catch {
    return
  }

  submitting.value = true
  try {
    if (isEdit.value && props.user) {
      await userApi.update(props.user.id, {
        role_id: form.role_id!,
        is_active: form.is_active,
        village_id: form.village_id,
        accessible_village_ids: form.accessible_village_ids,
      })
      ElMessage.success('用户更新成功')
    } else {
      await userApi.create({
        username: form.username,
        password: form.password,
        role_id: form.role_id!,
        is_active: form.is_active,
        village_id: form.village_id,
        accessible_village_ids: form.accessible_village_ids,
      })
      ElMessage.success('用户创建成功')
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
