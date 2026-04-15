# -*- coding: utf-8 -*-
"""
数据模型测试
测试 Village, Household, Member, User, Role, Permission 模型
"""

import pytest
from datetime import date
from src.models.household import Village, Household, Member
from src.models.auth import Role, Permission
from src.models.user import User


@pytest.mark.unit
class TestVillageModel:
    """堂区模型测试"""

    def test_create_village(self, test_db):
        """测试创建堂区"""
        from datetime import date
        village = Village(
            code='001',
            name='测试堂区',
            address='测试地址',
            establishment_date=date(2000, 1, 1),
            village_priest='测试神父'
        )
        test_db.add(village)
        test_db.commit()

        assert village.id is not None
        assert village.code == '001'
        assert village.name == '测试堂区'
        assert village.address == '测试地址'

    def test_village_code_unique(self, test_db):
        """测试堂区编码唯一性"""
        from datetime import date
        village1 = Village(
            code='001',
            name='堂区1',
            establishment_date=date(2000, 1, 1),
            village_priest='神父1',
            address='地址1'
        )
        test_db.add(village1)
        test_db.commit()

        village2 = Village(
            code='001',
            name='堂区2',
            establishment_date=date(2000, 1, 1),
            village_priest='神父2',
            address='地址2'
        )
        test_db.add(village2)

        with pytest.raises(Exception):  # IntegrityError
            test_db.commit()

    def test_village_households_relationship(self, test_db_with_data):
        """测试堂区和家庭的一对多关系"""
        data = test_db_with_data
        village1 = data['villages']['village1']
        household1 = data['households']['household1']

        assert household1 in village1.households
        assert household1.village == village1


@pytest.mark.unit
class TestHouseholdModel:
    """家庭模型测试"""

    def test_create_household(self, test_db_with_data):
        """测试创建家庭"""
        data = test_db_with_data
        db = data['db']
        village1 = data['villages']['village1']

        household = Household(
            village_id=village1.id,
            plot_number=999,
            address='新地址',
            phone='13812345678',
            head_of_household='测试户主'
        )
        db.add(household)
        db.commit()

        assert household.id is not None
        assert household.village_id == village1.id
        assert household.plot_number == 999
        assert household.address == '新地址'
        assert household.phone == '13812345678'
        assert household.head_of_household == '测试户主'

    def test_household_village_relationship(self, test_db_with_data):
        """测试家庭和堂区的多对一关系"""
        data = test_db_with_data
        household1 = data['households']['household1']
        village1 = data['villages']['village1']

        assert household1.village == village1
        assert household1.village_id == village1.id

    def test_household_members_relationship(self, test_db_with_data):
        """测试家庭和成员的一对多关系"""
        data = test_db_with_data
        household1 = data['households']['household1']
        member1 = data['members']['member1']
        member2 = data['members']['member2']

        assert member1 in household1.members
        assert member2 in household1.members
        assert len(household1.members) == 2


@pytest.mark.unit
class TestMemberModel:
    """成员模型测试"""

    def test_create_member(self, test_db_with_data):
        """测试创建成员"""
        data = test_db_with_data
        db = data['db']
        household1 = data['households']['household1']

        member = Member(
            household_id=household1.id,
            name='新成员',
            baptismal_name='若望',
            church_id='CH999',
            gender='男',
            birth_date=date(1990, 1, 1),
            occupation='测试职业',
            relation_to_head='儿子'
        )
        db.add(member)
        db.commit()

        assert member.id is not None
        assert member.household_id == household1.id
        assert member.name == '新成员'
        assert member.baptismal_name == '若望'
        assert member.church_id == 'CH999'
        assert member.gender == '男'
        assert member.occupation == '测试职业'

    def test_member_household_relationship(self, test_db_with_data):
        """测试成员和家庭的多对一关系"""
        data = test_db_with_data
        member1 = data['members']['member1']
        household1 = data['households']['household1']

        assert member1.household == household1
        assert member1.household_id == household1.id

    def test_member_optional_fields(self, test_db_with_data):
        """测试成员可选字段"""
        data = test_db_with_data
        member4 = data['members']['member4']

        assert member4.baptism_priest == '张神父'
        assert member4.confirmation_priest == '李神父'


@pytest.mark.unit
class TestPermissionModel:
    """权限模型测试"""

    def test_create_permission(self, test_db):
        """测试创建权限"""
        permission = Permission(
            name='test_permission',
            description='测试权限'
        )
        test_db.add(permission)
        test_db.commit()

        assert permission.id is not None
        assert permission.name == 'test_permission'
        assert permission.description == '测试权限'

    def test_permission_name_unique(self, test_db):
        """测试权限名称唯一性"""
        perm1 = Permission(name='test', description='测试1')
        test_db.add(perm1)
        test_db.commit()

        perm2 = Permission(name='test', description='测试2')
        test_db.add(perm2)

        with pytest.raises(Exception):  # IntegrityError
            test_db.commit()


@pytest.mark.unit
class TestRoleModel:
    """角色模型测试"""

    def test_create_role(self, test_db):
        """测试创建角色"""
        role = Role(
            name='test_role',
            description='测试角色'
        )
        test_db.add(role)
        test_db.commit()

        assert role.id is not None
        assert role.name == 'test_role'
        assert role.description == '测试角色'

    def test_role_permissions_relationship(self, test_db_with_data):
        """测试角色和权限的多对多关系"""
        data = test_db_with_data
        super_admin_role = data['roles']['super_admin']

        # 超级管理员应该有所有7个权限
        assert len(super_admin_role.permissions) == 7

        data_entry_role = data['roles']['data_entry']
        # 录入员应该有2个权限
        assert len(data_entry_role.permissions) == 2


@pytest.mark.unit
class TestUserModel:
    """用户模型测试"""

    def test_create_user(self, test_db_with_data):
        """测试创建用户"""
        import bcrypt
        data = test_db_with_data
        db = data['db']
        role = data['roles']['data_entry']

        user = User(
            username='testuser',
            role_id=role.id,
            password_hash=bcrypt.hashpw('testpassword'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        )
        db.add(user)
        db.commit()

        assert user.id is not None
        assert user.username == 'testuser'
        assert user.password_hash is not None

    def test_user_password(self, test_db_with_data):
        """测试用户密码加密和验证"""
        import bcrypt
        data = test_db_with_data
        user = data['users']['super_admin']

        # 验证正确密码
        assert bcrypt.checkpw('admin123'.encode('utf-8'), user.password_hash.encode('utf-8')) is True

        # 验证错误密码
        assert bcrypt.checkpw('wrongpassword'.encode('utf-8'), user.password_hash.encode('utf-8')) is False

    def test_user_role_relationship(self, test_db_with_data):
        """测试用户和角色的多对一关系"""
        data = test_db_with_data
        super_admin = data['users']['super_admin']
        super_admin_role = data['roles']['super_admin']

        assert super_admin.role == super_admin_role
        assert super_admin.role_id == super_admin_role.id

    def test_user_accessible_villages(self, test_db_with_data):
        """测试用户可访问堂区列表"""
        data = test_db_with_data
        observer = data['users']['observer']
        village1 = data['villages']['village1']
        village2 = data['villages']['village2']

        # 观察员应该可以访问堂区1和堂区2（多对多关系）
        accessible_ids = [v.id for v in observer.accessible_villages]
        assert village1.id in accessible_ids
        assert village2.id in accessible_ids
        assert len(observer.accessible_villages) == 2


@pytest.mark.unit
class TestModelRelationships:
    """模型关系集成测试"""

    def test_cascade_delete_household(self, test_db_with_data):
        """测试删除家庭时级联删除成员"""
        data = test_db_with_data
        db = data['db']
        household1 = data['households']['household1']

        # 获取成员数量
        member_count = len(household1.members)
        assert member_count == 2

        # 删除家庭
        db.delete(household1)
        db.commit()

        # 验证成员也被删除
        from src.models.household import Member
        remaining_members = db.query(Member).filter(Member.household_id == household1.id).all()
        assert len(remaining_members) == 0

    def test_data_integrity_chain(self, test_db_with_data):
        """测试数据完整性链：Village -> Household -> Member"""
        data = test_db_with_data
        member1 = data['members']['member1']
        household1 = data['households']['household1']
        village1 = data['villages']['village1']

        # 验证完整链条
        assert member1.household == household1
        assert household1.village == village1
        assert member1.household.village == village1
