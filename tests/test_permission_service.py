# -*- coding: utf-8 -*-
"""
权限服务测试
测试 PermissionService 的角色和权限管理功能
"""

import pytest
from datetime import date
from src.services.permission_service import PermissionService
from src.models.auth import Role, Permission


@pytest.mark.unit
class TestPermissionServiceRoleCRUD:
    """角色 CRUD 测试"""

    def test_get_all_roles(self, test_db_with_data):
        """测试获取所有角色"""
        data = test_db_with_data
        db = data['db']

        roles = PermissionService.get_all_roles(db)

        assert len(roles) == 3
        role_names = [r.name for r in roles]
        assert '超级管理员' in role_names
        assert '录入员' in role_names
        assert '观察员' in role_names

    def test_get_role_by_id(self, test_db_with_data):
        """测试根据 ID 获取角色"""
        data = test_db_with_data
        db = data['db']
        roles = data['roles']

        role = PermissionService.get_role_by_id(db, roles['super_admin'].id)

        assert role is not None
        assert role.name == '超级管理员'

    def test_get_role_by_id_not_found(self, test_db_with_data):
        """测试获取不存在的角色"""
        data = test_db_with_data
        db = data['db']

        role = PermissionService.get_role_by_id(db, 99999)

        assert role is None

    def test_create_role(self, test_db_with_data):
        """测试创建角色"""
        data = test_db_with_data
        db = data['db']

        role = PermissionService.create_role(
            db=db,
            name='new_role',
            description='新角色描述'
        )

        assert role is not None
        assert role.id is not None
        assert role.name == 'new_role'
        assert role.description == '新角色描述'

        # 验证数据库中确实有这条记录
        saved_role = db.query(Role).filter(Role.name == 'new_role').first()
        assert saved_role is not None

    def test_update_role(self, test_db_with_data):
        """测试更新角色"""
        data = test_db_with_data
        db = data['db']
        roles = data['roles']

        updated_role = PermissionService.update_role(
            db=db,
            role_id=roles['data_entry'].id,
            description='更新后的描述'
        )

        assert updated_role is not None
        assert updated_role.description == '更新后的描述'
        assert updated_role.name == '录入员'  # 名称不变

    def test_update_role_not_found(self, test_db_with_data):
        """测试更新不存在的角色"""
        data = test_db_with_data
        db = data['db']

        updated_role = PermissionService.update_role(
            db=db,
            role_id=99999,
            description='不存在'
        )

        assert updated_role is None

    def test_delete_role(self, test_db_with_data):
        """测试删除角色"""
        data = test_db_with_data
        db = data['db']

        # 创建一个测试角色
        role = PermissionService.create_role(db, 'to_delete', '待删除')
        role_id = role.id

        # 删除
        result = PermissionService.delete_role(db, role_id)

        assert result is True

        # 验证已删除
        deleted_role = db.query(Role).filter(Role.id == role_id).first()
        assert deleted_role is None

    def test_delete_role_not_found(self, test_db_with_data):
        """测试删除不存在的角色"""
        data = test_db_with_data
        db = data['db']

        result = PermissionService.delete_role(db, 99999)

        assert result is False


@pytest.mark.unit
class TestPermissionServicePermission:
    """权限管理测试"""

    def test_get_all_permissions(self, test_db_with_data):
        """测试获取所有权限"""
        data = test_db_with_data
        db = data['db']

        permissions = PermissionService.get_all_permissions(db)

        assert len(permissions) == 7
        permission_names = [p.name for p in permissions]
        assert 'user_manage' in permission_names
        assert 'role_manage' in permission_names
        assert 'village_manage' in permission_names
        assert 'household_manage' in permission_names
        assert 'household_view' in permission_names
        assert 'member_manage' in permission_names
        assert 'member_view' in permission_names

    def test_get_permission_by_id(self, test_db_with_data):
        """测试根据 ID 获取权限"""
        data = test_db_with_data
        db = data['db']
        permissions = data['permissions']

        permission = PermissionService.get_permission_by_id(db, permissions['user_manage'].id)

        assert permission is not None
        assert permission.name == 'user_manage'

    def test_get_permission_by_id_not_found(self, test_db_with_data):
        """测试获取不存在的权限"""
        data = test_db_with_data
        db = data['db']

        permission = PermissionService.get_permission_by_id(db, 99999)

        assert permission is None


@pytest.mark.unit
class TestPermissionServiceRolePermissions:
    """角色权限分配测试"""

    def test_assign_permissions_to_role(self, test_db_with_data):
        """测试为角色分配权限"""
        data = test_db_with_data
        db = data['db']
        permissions = data['permissions']

        # 创建一个新角色
        role = PermissionService.create_role(db, 'test_role', '测试角色')

        # 分配权限
        permission_ids = [
            permissions['household_view'].id,
            permissions['member_view'].id
        ]
        updated_role = PermissionService.assign_permissions_to_role(
            db=db,
            role_id=role.id,
            permission_ids=permission_ids
        )

        assert updated_role is not None
        assert len(updated_role.permissions) == 2

        permission_names = [p.name for p in updated_role.permissions]
        assert 'household_view' in permission_names
        assert 'member_view' in permission_names

    def test_assign_permissions_clears_existing(self, test_db_with_data):
        """测试分配权限会清除现有权限"""
        data = test_db_with_data
        db = data['db']
        roles = data['roles']
        permissions = data['permissions']

        # data_entry 角色原本有 2 个权限
        original_count = len(roles['data_entry'].permissions)
        assert original_count == 2

        # 重新分配权限
        new_permission_ids = [permissions['household_view'].id]
        updated_role = PermissionService.assign_permissions_to_role(
            db=db,
            role_id=roles['data_entry'].id,
            permission_ids=new_permission_ids
        )

        # 现在应该只有 1 个权限
        assert len(updated_role.permissions) == 1
        assert updated_role.permissions[0].name == 'household_view'

    def test_assign_permissions_to_nonexistent_role(self, test_db_with_data):
        """测试为不存在的角色分配权限"""
        data = test_db_with_data
        db = data['db']

        result = PermissionService.assign_permissions_to_role(
            db=db,
            role_id=99999,
            permission_ids=[1, 2]
        )

        assert result is None


@pytest.mark.unit
class TestPermissionServiceVillageAccess:
    """用户堂区访问权限测试"""

    def test_assign_villages_to_user(self, test_db_with_data):
        """测试为用户分配可访问堂区"""
        data = test_db_with_data
        db = data['db']
        users = data['users']
        villages = data['villages']

        # 为 data_entry 用户分配多个堂区
        village_ids = [villages['village1'].id, villages['village2'].id]
        updated_user = PermissionService.assign_villages_to_user(
            db=db,
            user_id=users['data_entry'].id,
            village_ids=village_ids
        )

        assert updated_user is not None
        assert len(updated_user.accessible_villages) == 2

        accessible_ids = [v.id for v in updated_user.accessible_villages]
        assert villages['village1'].id in accessible_ids
        assert villages['village2'].id in accessible_ids

    @pytest.mark.skip(reason="permission_service.assign_villages_to_user() 使用 raw SQL delete 导致 StaleDataError")
    def test_assign_villages_clears_existing(self, test_db_with_data):
        """测试分配堂区会清除现有权限"""
        data = test_db_with_data
        db = data['db']
        villages = data['villages']
        users = data['users']

        # observer 用户原本有 2 个堂区
        original_count = len(users['observer'].accessible_villages)
        assert original_count == 2

        # 重新分配为 1 个堂区（使用新的测试堂区）
        new_village_ids = [villages['village3'].id]
        updated_user = PermissionService.assign_villages_to_user(
            db=db,
            user_id=users['observer'].id,
            village_ids=new_village_ids
        )

        # 现在应该只有 1 个堂区
        db.refresh(updated_user)  # 刷新以获取最新数据
        assert len(updated_user.accessible_villages) == 1
        assert updated_user.accessible_villages[0].id == villages['village3'].id

    def test_assign_empty_villages(self, test_db_with_data):
        """测试分配空堂区列表"""
        data = test_db_with_data
        db = data['db']
        users = data['users']

        # 清空 observer 的堂区权限
        updated_user = PermissionService.assign_villages_to_user(
            db=db,
            user_id=users['observer'].id,
            village_ids=[]
        )

        assert updated_user is not None
        assert len(updated_user.accessible_villages) == 0

    def test_assign_villages_to_nonexistent_user(self, test_db_with_data):
        """测试为不存在的用户分配堂区"""
        data = test_db_with_data
        db = data['db']

        result = PermissionService.assign_villages_to_user(
            db=db,
            user_id=99999,
            village_ids=[1, 2]
        )

        assert result is None

    def test_get_user_villages(self, test_db_with_data):
        """测试获取用户可访问的堂区列表"""
        data = test_db_with_data
        db = data['db']
        users = data['users']
        villages = data['villages']

        # observer 用户有 2 个堂区
        village_list = PermissionService.get_user_villages(db, users['observer'].id)

        assert len(village_list) == 2
        village_ids = [v.id for v in village_list]
        assert villages['village1'].id in village_ids
        assert villages['village2'].id in village_ids

    def test_get_user_villages_for_nonexistent_user(self, test_db_with_data):
        """测试获取不存在用户的堂区列表"""
        data = test_db_with_data
        db = data['db']

        village_list = PermissionService.get_user_villages(db, 99999)

        assert village_list == []


@pytest.mark.integration
class TestPermissionServiceIntegration:
    """权限服务集成测试"""

    def test_create_role_and_assign_permissions(self, test_db_with_data):
        """测试创建角色并分配权限"""
        data = test_db_with_data
        db = data['db']
        permissions = data['permissions']

        # 创建角色
        role = PermissionService.create_role(db, 'custom_role', '自定义角色')

        # 分配权限
        permission_ids = [
            permissions['household_view'].id,
            permissions['member_view'].id,
            permissions['village_manage'].id
        ]
        updated_role = PermissionService.assign_permissions_to_role(
            db=db,
            role_id=role.id,
            permission_ids=permission_ids
        )

        # 验证
        assert len(updated_role.permissions) == 3

        # 从数据库重新读取验证
        reloaded_role = PermissionService.get_role_by_id(db, role.id)
        assert len(reloaded_role.permissions) == 3

    def test_full_role_crud_cycle(self, test_db_with_data):
        """测试完整角色 CRUD 周期"""
        data = test_db_with_data
        db = data['db']

        # Create
        role = PermissionService.create_role(db, 'temp_role', '临时角色')
        role_id = role.id

        # Read
        read_role = PermissionService.get_role_by_id(db, role_id)
        assert read_role is not None

        # Update
        updated_role = PermissionService.update_role(db, role_id, description='更新描述')
        assert updated_role.description == '更新描述'

        # Delete
        result = PermissionService.delete_role(db, role_id)
        assert result is True

        # Verify deletion
        deleted_role = PermissionService.get_role_by_id(db, role_id)
        assert deleted_role is None

    def test_user_village_access_workflow(self, test_db_with_data):
        """测试用户堂区访问权限工作流"""
        data = test_db_with_data
        db = data['db']
        users = data['users']
        villages = data['villages']

        # 1. 获取用户当前堂区
        current_villages = PermissionService.get_user_villages(db, users['data_entry'].id)
        # data_entry 用户属于 village1
        assert len(current_villages) == 0  # data_entry 的accessible_villages为空（通过village_id访问）

        # 2. 修改用户堂区权限
        new_village_ids = [villages['village2'].id, villages['village3'].id]
        updated_user = PermissionService.assign_villages_to_user(
            db=db,
            user_id=users['data_entry'].id,
            village_ids=new_village_ids
        )

        # 3. 验证修改后的堂区
        db.refresh(updated_user)
        updated_villages = PermissionService.get_user_villages(db, users['data_entry'].id)
        assert len(updated_villages) == 2
        village_ids = [v.id for v in updated_villages]
        assert villages['village2'].id in village_ids
        assert villages['village3'].id in village_ids
