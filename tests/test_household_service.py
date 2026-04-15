# -*- coding: utf-8 -*-
"""
家庭服务测试
测试 HouseholdService 的 CRUD 操作和搜索功能
"""

import pytest
from src.services.household_service import HouseholdService
from src.models.household import Household


@pytest.mark.unit
class TestHouseholdServiceCRUD:
    """家庭服务 CRUD 测试"""

    def test_get_all_households(self, test_db_with_data):
        """测试获取所有家庭"""
        data = test_db_with_data
        db = data['db']

        households = HouseholdService.get_all_households(db)

        assert len(households) == 3
        head_names = [h.head_of_household for h in households]
        assert '张三' in head_names
        assert '王五' in head_names
        assert '赵六' in head_names

    def test_get_all_households_filter_by_village(self, test_db_with_data):
        """测试按堂区过滤家庭"""
        data = test_db_with_data
        db = data['db']
        village1 = data['villages']['village1']

        households = HouseholdService.get_all_households(db, village_id=village1.id)

        assert len(households) == 1
        assert households[0].head_of_household == '张三'
        assert households[0].village_id == village1.id

    def test_get_household_by_id(self, test_db_with_data):
        """测试根据 ID 获取家庭"""
        data = test_db_with_data
        db = data['db']
        household1 = data['households']['household1']

        household = HouseholdService.get_household_by_id(db, household1.id)

        assert household is not None
        assert household.id == household1.id
        assert household.head_of_household == '张三'
        # 验证关联加载
        assert household.village is not None

    def test_get_household_by_id_not_found(self, test_db_with_data):
        """测试获取不存在的家庭"""
        data = test_db_with_data
        db = data['db']

        household = HouseholdService.get_household_by_id(db, 99999)

        assert household is None

    def test_create_household(self, test_db_with_data):
        """测试创建家庭"""
        data = test_db_with_data
        db = data['db']
        village1 = data['villages']['village1']

        household = HouseholdService.create_household(
            db=db,
            village_id=village1.id,
            plot_number=999,
            address='新家庭地址',
            phone='13912345678',
            head_of_household='新户主'
        )

        assert household is not None
        assert household.id is not None
        assert household.village_id == village1.id
        assert household.plot_number == 999
        assert household.address == '新家庭地址'
        assert household.phone == '13912345678'
        assert household.head_of_household == '新户主'

        # 验证数据库中确实有这条记录
        saved_household = db.query(Household).filter(Household.id == household.id).first()
        assert saved_household is not None

    def test_create_household_minimal_fields(self, test_db_with_data):
        """测试只填写必需字段创建家庭"""
        data = test_db_with_data
        db = data['db']
        village1 = data['villages']['village1']

        household = HouseholdService.create_household(
            db=db,
            village_id=village1.id,
            plot_number=888,
            address='最小字段地址'
        )

        assert household is not None
        assert household.phone is None
        assert household.head_of_household is None

    def test_update_household(self, test_db_with_data):
        """测试更新家庭"""
        data = test_db_with_data
        db = data['db']
        household1 = data['households']['household1']

        updated_household = HouseholdService.update_household(
            db=db,
            household_id=household1.id,
            address='更新后的地址',
            phone='13999999999'
        )

        assert updated_household is not None
        assert updated_household.id == household1.id
        assert updated_household.address == '更新后的地址'
        assert updated_household.phone == '13999999999'
        # 其他字段不变
        assert updated_household.head_of_household == '张三'

    def test_update_household_not_found(self, test_db_with_data):
        """测试更新不存在的家庭"""
        data = test_db_with_data
        db = data['db']

        updated_household = HouseholdService.update_household(
            db=db,
            household_id=99999,
            address='不存在'
        )

        assert updated_household is None

    def test_delete_household(self, test_db_with_data):
        """测试删除家庭"""
        data = test_db_with_data
        db = data['db']

        # 创建一个测试家庭
        village1 = data['villages']['village1']
        household = HouseholdService.create_household(
            db=db,
            village_id=village1.id,
            plot_number=777,
            address='待删除'
        )
        household_id = household.id

        # 删除家庭
        result = HouseholdService.delete_household(db, household_id)

        assert result is True

        # 验证已删除
        deleted_household = db.query(Household).filter(Household.id == household_id).first()
        assert deleted_household is None

    def test_delete_household_not_found(self, test_db_with_data):
        """测试删除不存在的家庭"""
        data = test_db_with_data
        db = data['db']

        result = HouseholdService.delete_household(db, 99999)

        assert result is False

    def test_delete_household_cascades_members(self, test_db_with_data):
        """测试删除家庭会级联删除成员"""
        data = test_db_with_data
        db = data['db']
        household1 = data['households']['household1']

        # household1 有 2 个成员
        member_count = len(household1.members)
        assert member_count == 2

        # 删除家庭
        result = HouseholdService.delete_household(db, household1.id)

        assert result is True

        # 验证成员也被删除了（由于数据库的 cascade delete）
        from src.models.household import Member
        remaining_members = db.query(Member).filter(Member.household_id == household1.id).all()
        assert len(remaining_members) == 0


@pytest.mark.unit
class TestHouseholdServiceSearch:
    """家庭搜索测试"""

    def test_search_households_by_head_name(self, test_db_with_data):
        """测试按户主姓名搜索"""
        data = test_db_with_data
        db = data['db']

        households = HouseholdService.search_households(db, keyword='张三')

        assert len(households) == 1
        assert households[0].head_of_household == '张三'

    def test_search_households_by_address(self, test_db_with_data):
        """测试按地址搜索"""
        data = test_db_with_data
        db = data['db']

        households = HouseholdService.search_households(db, keyword='101')

        assert len(households) == 1
        assert '101' in households[0].address

    def test_search_households_by_phone(self, test_db_with_data):
        """测试按电话搜索"""
        data = test_db_with_data
        db = data['db']

        households = HouseholdService.search_households(db, keyword='138')

        assert len(households) == 1
        assert '138' in households[0].phone

    def test_search_households_with_village_filter(self, test_db_with_data):
        """测试搜索时过滤堂区"""
        data = test_db_with_data
        db = data['db']
        village1 = data['villages']['village1']

        # 搜索"测试"但限制在堂区1
        households = HouseholdService.search_households(db, keyword='测试', village_id=village1.id)

        assert len(households) == 1
        assert households[0].village_id == village1.id

    def test_search_households_no_keyword(self, test_db_with_data):
        """测试无关键词搜索"""
        data = test_db_with_data
        db = data['db']

        # 无关键词应返回所有家庭
        households = HouseholdService.search_households(db)

        assert len(households) == 3

    def test_search_households_no_results(self, test_db_with_data):
        """测试无结果搜索"""
        data = test_db_with_data
        db = data['db']

        households = HouseholdService.search_households(db, keyword='不存在的户主')

        assert len(households) == 0

    def test_search_households_partial_match(self, test_db_with_data):
        """测试部分匹配"""
        data = test_db_with_data
        db = data['db']

        # 搜索"测试"应该匹配多个家庭
        households = HouseholdService.search_households(db, keyword='测试')

        assert len(households) == 3


@pytest.mark.integration
class TestHouseholdServiceIntegration:
    """家庭服务集成测试"""

    def test_create_and_retrieve_household(self, test_db_with_data):
        """测试创建后立即检索"""
        data = test_db_with_data
        db = data['db']
        village1 = data['villages']['village1']

        # 创建
        created = HouseholdService.create_household(
            db=db,
            village_id=village1.id,
            plot_number=666,
            address='集成测试地址',
            phone='13666666666',
            head_of_household='集成测试户主'
        )

        # 按 ID 检索
        by_id = HouseholdService.get_household_by_id(db, created.id)
        assert by_id.head_of_household == '集成测试户主'

        # 按关键词检索
        by_search = HouseholdService.search_households(db, keyword='集成')
        assert len(by_search) == 1
        assert by_search[0].id == created.id

    def test_full_crud_cycle(self, test_db_with_data):
        """测试完整 CRUD 周期"""
        data = test_db_with_data
        db = data['db']
        village1 = data['villages']['village1']

        # Create
        household = HouseholdService.create_household(
            db=db,
            village_id=village1.id,
            plot_number=555,
            address='CRUD测试',
            head_of_household='CRUD户主'
        )
        household_id = household.id

        # Read
        read_household = HouseholdService.get_household_by_id(db, household_id)
        assert read_household is not None

        # Update
        HouseholdService.update_household(db, household_id, phone='13555555555')
        updated_household = HouseholdService.get_household_by_id(db, household_id)
        assert updated_household.phone == '13555555555'

        # Delete
        result = HouseholdService.delete_household(db, household_id)
        assert result is True

        # Verify deletion
        deleted_household = HouseholdService.get_household_by_id(db, household_id)
        assert deleted_household is None

    def test_village_relationship(self, test_db_with_data):
        """测试家庭和堂区的关系"""
        data = test_db_with_data
        db = data['db']
        village1 = data['villages']['village1']

        # 获取堂区1的所有家庭
        households = HouseholdService.get_all_households(db, village_id=village1.id)

        # 验证所有家庭都属于堂区1
        for household in households:
            assert household.village_id == village1.id
            assert household.village.id == village1.id
            assert household.village.name == '测试堂区1'
