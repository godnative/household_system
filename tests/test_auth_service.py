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


@pytest.mark.unit
class TestAuthServicePasswordHashing:
    """密码哈希测试"""

    def test_get_password_hash(self):
        """测试获取密码哈希值"""
        password = 'test_password_123'
        hashed = AuthService.get_password_hash(password)

        assert hashed is not None
        assert isinstance(hashed, str)
        assert hashed != password  # 哈希值不应等于原密码

    def test_verify_password_correct(self):
        """测试验证正确密码"""
        password = 'correct_password'
        hashed = AuthService.get_password_hash(password)

        result = AuthService.verify_password(password, hashed)
        assert result is True

    def test_verify_password_incorrect(self):
        """测试验证错误密码"""
        password = 'correct_password'
        hashed = AuthService.get_password_hash(password)

        result = AuthService.verify_password('wrong_password', hashed)
        assert result is False

    def test_same_password_different_hashes(self):
        """测试相同密码生成不同哈希值（盐值随机）"""
        password = 'same_password'
        hash1 = AuthService.get_password_hash(password)
        hash2 = AuthService.get_password_hash(password)

        # 由于使用随机盐值，两次哈希结果应该不同
        assert hash1 != hash2

        # 但两个哈希都应该能验证原密码
        assert AuthService.verify_password(password, hash1) is True
        assert AuthService.verify_password(password, hash2) is True


@pytest.mark.unit
class TestAuthServiceVillageAccess:
    """堂区访问权限测试"""

    def test_check_village_access_super_admin(self, test_db_with_data, super_admin_user):
        """测试超级管理员可以访问任何堂区"""
        data = test_db_with_data
        village1 = data['villages']['village1']
        village3 = data['villages']['village3']

        # 超级管理员可以访问所有堂区
        assert AuthService.check_village_access(super_admin_user, village1.id) is True
        assert AuthService.check_village_access(super_admin_user, village3.id) is True
        assert AuthService.check_village_access(super_admin_user, 99999) is True

    def test_check_village_access_data_entry(self, test_db_with_data, data_entry_user):
        """测试录入员只能访问所属堂区"""
        data = test_db_with_data
        village1 = data['villages']['village1']
        village2 = data['villages']['village2']

        # 录入员只能访问所属堂区 (village1)
        assert AuthService.check_village_access(data_entry_user, village1.id) is True
        assert AuthService.check_village_access(data_entry_user, village2.id) is False

    def test_check_village_access_observer(self, test_db_with_data, observer_user):
        """测试观察员只能访问授权堂区"""
        data = test_db_with_data
        village1 = data['villages']['village1']
        village2 = data['villages']['village2']
        village3 = data['villages']['village3']

        # 观察员可以访问 village1 和 village2，不能访问 village3
        assert AuthService.check_village_access(observer_user, village1.id) is True
        assert AuthService.check_village_access(observer_user, village2.id) is True
        assert AuthService.check_village_access(observer_user, village3.id) is False

    def test_check_household_access_super_admin(self, test_db_with_data, super_admin_user):
        """测试超级管理员可以访问任何家庭"""
        data = test_db_with_data
        db = data['db']
        household1 = data['households']['household1']

        # 超级管理员可以访问所有家庭
        assert AuthService.check_household_access(super_admin_user, household1.id, db) is True

    def test_check_household_access_data_entry(self, test_db_with_data, data_entry_user):
        """测试录入员只能访问所属堂区的家庭"""
        data = test_db_with_data
        db = data['db']
        household1 = data['households']['household1']  # 堂区1
        household2 = data['households']['household2']  # 堂区2

        # 录入员属于堂区1，只能访问堂区1的家庭
        assert AuthService.check_household_access(data_entry_user, household1.id, db) is True
        assert AuthService.check_household_access(data_entry_user, household2.id, db) is False

    def test_check_household_access_nonexistent(self, test_db_with_data, super_admin_user):
        """测试访问不存在的家庭"""
        data = test_db_with_data
        db = data['db']

        # 不存在的家庭应该返回 False
        assert AuthService.check_household_access(super_admin_user, 99999, db) is False


@pytest.mark.unit
class TestAuthServiceUserManagement:
    """用户管理测试"""

    def test_get_user_by_username(self, test_db_with_data):
        """测试根据用户名获取用户"""
        data = test_db_with_data
        db = data['db']

        user = AuthService.get_user_by_username(db, 'admin')

        assert user is not None
        assert user.username == 'admin'

    def test_get_user_by_username_not_found(self, test_db_with_data):
        """测试获取不存在的用户"""
        data = test_db_with_data
        db = data['db']

        user = AuthService.get_user_by_username(db, 'nonexistent')

        assert user is None

    def test_create_user(self, test_db_with_data):
        """测试创建用户"""
        data = test_db_with_data
        db = data['db']
        role = data['roles']['data_entry']
        village1 = data['villages']['village1']

        user = AuthService.create_user(
            db=db,
            username='newuser',
            password='password123',
            role_id=role.id,
            village_id=village1.id
        )

        assert user is not None
        assert user.id is not None
        assert user.username == 'newuser'
        assert user.role_id == role.id
        assert user.village_id == village1.id

        # 验证密码已被哈希
        assert user.password_hash != 'password123'
        assert AuthService.verify_password('password123', user.password_hash) is True

    def test_update_user_basic_info(self, test_db_with_data):
        """测试更新用户基本信息"""
        data = test_db_with_data
        db = data['db']
        user = data['users']['data_entry']
        village2 = data['villages']['village2']

        updated_user = AuthService.update_user(
            db=db,
            user_id=user.id,
            village_id=village2.id
        )

        assert updated_user is not None
        assert updated_user.village_id == village2.id

    def test_update_user_password(self, test_db_with_data):
        """测试更新用户密码"""
        data = test_db_with_data
        db = data['db']
        user = data['users']['data_entry']

        # 更新密码
        new_password = 'new_password_456'
        updated_user = AuthService.update_user(
            db=db,
            user_id=user.id,
            password=new_password
        )

        assert updated_user is not None

        # 验证新密码可以用于认证
        authenticated = AuthService.authenticate_user(db, user.username, new_password)
        assert authenticated is not None
        assert authenticated.id == user.id

        # 验证旧密码不能用于认证
        old_auth = AuthService.authenticate_user(db, user.username, 'entry123')
        assert old_auth is None

    def test_update_user_not_found(self, test_db_with_data):
        """测试更新不存在的用户"""
        data = test_db_with_data
        db = data['db']

        updated_user = AuthService.update_user(
            db=db,
            user_id=99999,
            username='notfound'
        )

        assert updated_user is None

    def test_delete_user(self, test_db_with_data):
        """测试删除用户"""
        data = test_db_with_data
        db = data['db']
        role = data['roles']['observer']

        # 创建一个测试用户
        user = AuthService.create_user(
            db=db,
            username='to_delete',
            password='password',
            role_id=role.id
        )
        user_id = user.id

        # 删除用户
        result = AuthService.delete_user(db, user_id)

        assert result is True

        # 验证用户已被删除
        from src.models.user import User
        deleted_user = db.query(User).filter(User.id == user_id).first()
        assert deleted_user is None

    def test_delete_user_not_found(self, test_db_with_data):
        """测试删除不存在的用户"""
        data = test_db_with_data
        db = data['db']

        result = AuthService.delete_user(db, 99999)

        assert result is False
