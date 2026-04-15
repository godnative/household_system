# -*- coding: utf-8 -*-
"""
权限服务测试
测试 AuthService 的权限检查、用户认证等功能
"""

import pytest
from src.services.auth_service import AuthService
from src.constants.permissions import (
    PERM_USER_MANAGE, PERM_VILLAGE_MANAGE,
    PERM_HOUSEHOLD_MANAGE, PERM_HOUSEHOLD_VIEW,
    PERM_MEMBER_MANAGE, PERM_MEMBER_VIEW
)


@pytest.mark.unit
class TestAuthServicePermissionCheck:
    """权限检查测试"""

    def test_super_admin_has_all_permissions(self, test_db_with_data, super_admin_user):
        """测试超级管理员拥有所有权限"""
        assert AuthService.check_permission(super_admin_user, PERM_USER_MANAGE) is True
        assert AuthService.check_permission(super_admin_user, PERM_VILLAGE_MANAGE) is True
        assert AuthService.check_permission(super_admin_user, PERM_HOUSEHOLD_MANAGE) is True
        assert AuthService.check_permission(super_admin_user, PERM_HOUSEHOLD_VIEW) is True
        assert AuthService.check_permission(super_admin_user, PERM_MEMBER_MANAGE) is True
        assert AuthService.check_permission(super_admin_user, PERM_MEMBER_VIEW) is True

    def test_data_entry_has_limited_permissions(self, test_db_with_data, data_entry_user):
        """测试录入员只有家庭和成员管理权限"""
        # 有的权限
        assert AuthService.check_permission(data_entry_user, PERM_HOUSEHOLD_MANAGE) is True
        assert AuthService.check_permission(data_entry_user, PERM_MEMBER_MANAGE) is True

        # 没有的权限
        assert AuthService.check_permission(data_entry_user, PERM_USER_MANAGE) is False
        assert AuthService.check_permission(data_entry_user, PERM_VILLAGE_MANAGE) is False
        assert AuthService.check_permission(data_entry_user, PERM_HOUSEHOLD_VIEW) is False
        assert AuthService.check_permission(data_entry_user, PERM_MEMBER_VIEW) is False

    def test_observer_has_view_only_permissions(self, test_db_with_data, observer_user):
        """测试观察员只有查看权限"""
        # 有的权限
        assert AuthService.check_permission(observer_user, PERM_HOUSEHOLD_VIEW) is True
        assert AuthService.check_permission(observer_user, PERM_MEMBER_VIEW) is True

        # 没有的权限
        assert AuthService.check_permission(observer_user, PERM_HOUSEHOLD_MANAGE) is False
        assert AuthService.check_permission(observer_user, PERM_MEMBER_MANAGE) is False
        assert AuthService.check_permission(observer_user, PERM_USER_MANAGE) is False

    def test_check_permission_with_none_user(self):
        """测试检查空用户的权限"""
        assert AuthService.check_permission(None, PERM_USER_MANAGE) is False

    def test_check_permission_with_no_role(self, test_db_with_data):
        """测试检查没有角色的用户的权限"""
        import bcrypt
        data = test_db_with_data
        db = data['db']

        from src.models.user import User
        user_no_role = User(
            username='norole',
            role_id=None,
            password_hash=bcrypt.hashpw('test123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        )
        db.add(user_no_role)
        db.commit()

        assert AuthService.check_permission(user_no_role, PERM_USER_MANAGE) is False


@pytest.mark.unit
class TestAuthServiceAccessibleVillages:
    """可访问堂区测试"""

    def test_super_admin_accessible_villages(self, test_db_with_data, super_admin_user):
        """测试超级管理员可访问所有堂区"""
        villages = AuthService.get_user_accessible_villages(super_admin_user)

        # 超级管理员返回 None 表示可访问所有堂区
        assert villages is None

    def test_data_entry_accessible_villages(self, test_db_with_data, data_entry_user):
        """测试录入员只能访问所属堂区"""
        data = test_db_with_data
        village1 = data['villages']['village1']

        villages = AuthService.get_user_accessible_villages(data_entry_user)

        # 录入员只能访问所属堂区
        assert villages is not None
        assert isinstance(villages, list)
        assert len(villages) == 1
        assert villages[0] == village1.id

    def test_observer_accessible_villages(self, test_db_with_data, observer_user):
        """测试观察员可访问授权的多个堂区"""
        data = test_db_with_data
        village1 = data['villages']['village1']
        village2 = data['villages']['village2']

        villages = AuthService.get_user_accessible_villages(observer_user)

        # 观察员可访问授权的堂区列表
        assert villages is not None
        assert isinstance(villages, list)
        assert len(villages) == 2
        assert village1.id in villages
        assert village2.id in villages

    def test_accessible_villages_with_none_user(self):
        """测试空用户的可访问堂区"""
        villages = AuthService.get_user_accessible_villages(None)
        assert villages == []

    def test_accessible_villages_with_no_role(self, test_db_with_data):
        """测试没有角色的用户的可访问堂区"""
        import bcrypt
        data = test_db_with_data
        db = data['db']

        from src.models.user import User
        user_no_role = User(
            username='norole',
            role_id=None,
            password_hash=bcrypt.hashpw('test123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        )
        db.add(user_no_role)
        db.commit()

        villages = AuthService.get_user_accessible_villages(user_no_role)
        assert villages == []


@pytest.mark.unit
class TestAuthServiceUserAuthentication:
    """用户认证测试"""

    def test_authenticate_success(self, test_db_with_data):
        """测试成功认证用户"""
        data = test_db_with_data
        db = data['db']

        user = AuthService.authenticate_user(db, 'admin', 'admin123')

        assert user is not None
        assert user.username == 'admin'

    def test_authenticate_wrong_password(self, test_db_with_data):
        """测试错误密码认证失败"""
        data = test_db_with_data
        db = data['db']

        user = AuthService.authenticate_user(db, 'admin', 'wrongpassword')

        assert user is None

    def test_authenticate_nonexistent_user(self, test_db_with_data):
        """测试不存在的用户认证失败"""
        data = test_db_with_data
        db = data['db']

        user = AuthService.authenticate_user(db, 'nonexistent', 'password')

        assert user is None

    def test_authenticate_empty_credentials(self, test_db_with_data):
        """测试空凭据认证失败"""
        data = test_db_with_data
        db = data['db']

        user = AuthService.authenticate_user(db, '', '')

        assert user is None


@pytest.mark.integration
class TestAuthServiceIntegration:
    """权限服务集成测试"""

    def test_permission_hierarchy(self, test_db_with_data):
        """测试权限层级：超级管理员 > 录入员 > 观察员"""
        data = test_db_with_data
        super_admin = data['users']['super_admin']
        data_entry = data['users']['data_entry']
        observer = data['users']['observer']

        # 统计每个角色的权限数量
        super_admin_perm_count = len(super_admin.role.permissions)
        data_entry_perm_count = len(data_entry.role.permissions)
        observer_perm_count = len(observer.role.permissions)

        assert super_admin_perm_count > data_entry_perm_count
        assert data_entry_perm_count == observer_perm_count  # 都是2个权限，但不同

    def test_data_access_scope(self, test_db_with_data):
        """测试数据访问范围：超级管理员 > 观察员 > 录入员"""
        data = test_db_with_data
        super_admin = data['users']['super_admin']
        data_entry = data['users']['data_entry']
        observer = data['users']['observer']

        super_admin_villages = AuthService.get_user_accessible_villages(super_admin)
        data_entry_villages = AuthService.get_user_accessible_villages(data_entry)
        observer_villages = AuthService.get_user_accessible_villages(observer)

        # 超级管理员可访问所有堂区（返回 None）
        assert super_admin_villages is None

        # 观察员可访问2个堂区
        assert len(observer_villages) == 2

        # 录入员只能访问1个堂区
        assert len(data_entry_villages) == 1

    def test_role_based_access_control(self, test_db_with_data):
        """测试基于角色的访问控制（RBAC）"""
        data = test_db_with_data
        db = data['db']

        # 创建一个新的录入员用户
        role = data['roles']['data_entry']
        village3 = data['villages']['village3']

        new_entry = data['db'].merge(data['users']['data_entry'])
        new_entry.username = 'entry2'
        new_entry.village_id = village3.id
        db.add(new_entry)
        db.commit()

        # 验证新录入员的权限
        assert AuthService.check_permission(new_entry, PERM_HOUSEHOLD_MANAGE) is True
        assert AuthService.check_permission(new_entry, PERM_MEMBER_MANAGE) is True

        # 验证新录入员的可访问堂区
        villages = AuthService.get_user_accessible_villages(new_entry)
        assert len(villages) == 1
        assert villages[0] == village3.id
