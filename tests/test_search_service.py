# -*- coding: utf-8 -*-
"""
搜索服务测试
测试 SearchService 的家庭搜索、成员搜索、权限过滤等功能
"""

import pytest
from src.services.search_service import SearchService


@pytest.mark.unit
class TestSearchServiceHouseholdSearch:
    """家庭搜索测试"""

    def test_search_households_by_head_name(self, test_db_with_data, super_admin_user):
        """测试通过户主姓名搜索家庭"""
        data = test_db_with_data
        db = data['db']

        # 搜索户主姓名包含"张"的家庭
        results = SearchService.search_households(db, '张', super_admin_user)

        assert len(results) == 1
        assert results[0].head_of_household == '张三'

    def test_search_households_by_phone(self, test_db_with_data, super_admin_user):
        """测试通过电话号码搜索家庭"""
        data = test_db_with_data
        db = data['db']

        # 搜索电话号码包含"138"的家庭
        results = SearchService.search_households(db, '138', super_admin_user)

        assert len(results) == 1
        assert '138' in results[0].phone

    def test_search_households_by_address(self, test_db_with_data, super_admin_user):
        """测试通过地址搜索家庭"""
        data = test_db_with_data
        db = data['db']

        # 搜索地址包含"101"的家庭
        results = SearchService.search_households(db, '101', super_admin_user)

        assert len(results) == 1
        assert '101' in results[0].address

    def test_search_households_by_plot_number(self, test_db_with_data, super_admin_user):
        """测试通过地块编号搜索家庭"""
        data = test_db_with_data
        db = data['db']

        # 搜索地块编号为201的家庭
        results = SearchService.search_households(db, '201', super_admin_user)

        assert len(results) == 1
        assert results[0].plot_number == 201

    def test_search_households_empty_keyword(self, test_db_with_data, super_admin_user):
        """测试空关键词搜索"""
        data = test_db_with_data
        db = data['db']

        # 空关键词应该返回空列表
        results = SearchService.search_households(db, '', super_admin_user)
        assert len(results) == 0

        results = SearchService.search_households(db, '   ', super_admin_user)
        assert len(results) == 0

    def test_search_households_no_results(self, test_db_with_data, super_admin_user):
        """测试无匹配结果"""
        data = test_db_with_data
        db = data['db']

        # 搜索不存在的关键词
        results = SearchService.search_households(db, '不存在的户主', super_admin_user)

        assert len(results) == 0


@pytest.mark.unit
class TestSearchServiceMemberSearch:
    """成员搜索测试"""

    def test_search_members_by_name(self, test_db_with_data, super_admin_user):
        """测试通过姓名搜索成员"""
        data = test_db_with_data
        db = data['db']

        # 搜索姓名包含"李四"的成员（只在家庭1）
        results = SearchService.search_members(db, '李四', super_admin_user)

        assert len(results) == 1
        # 返回的是包含匹配成员的家庭
        assert results[0].head_of_household == '张三'

    def test_search_members_by_baptismal_name(self, test_db_with_data, super_admin_user):
        """测试通过圣名搜索成员"""
        data = test_db_with_data
        db = data['db']

        # 搜索圣名为"若瑟"的成员
        results = SearchService.search_members(db, '若瑟', super_admin_user)

        assert len(results) == 1
        assert results[0].head_of_household == '张三'

    def test_search_members_by_church_id(self, test_db_with_data, super_admin_user):
        """测试通过教友编号搜索成员"""
        data = test_db_with_data
        db = data['db']

        # 搜索教友编号为"CH001"的成员
        results = SearchService.search_members(db, 'CH001', super_admin_user)

        assert len(results) == 1

    def test_search_members_by_occupation(self, test_db_with_data, super_admin_user):
        """测试通过职业搜索成员"""
        data = test_db_with_data
        db = data['db']

        # 搜索职业为"教师"的成员
        results = SearchService.search_members(db, '教师', super_admin_user)

        assert len(results) == 1
        assert results[0].head_of_household == '张三'

    def test_search_members_by_association(self, test_db_with_data, super_admin_user):
        """测试通过善会搜索成员"""
        data = test_db_with_data
        db = data['db']

        # 搜索善会为"圣母军"的成员
        results = SearchService.search_members(db, '圣母军', super_admin_user)

        assert len(results) == 1

    def test_search_members_by_baptism_priest(self, test_db_with_data, super_admin_user):
        """测试通过施洗神父搜索成员"""
        data = test_db_with_data
        db = data['db']

        # 搜索施洗神父为"张神父"的成员
        results = SearchService.search_members(db, '张神父', super_admin_user)

        assert len(results) == 1
        assert results[0].head_of_household == '赵六'

    def test_search_members_by_confirmation_priest(self, test_db_with_data, super_admin_user):
        """测试通过坚振神父搜索成员"""
        data = test_db_with_data
        db = data['db']

        # 搜索坚振神父为"李神父"的成员
        results = SearchService.search_members(db, '李神父', super_admin_user)

        assert len(results) == 1

    def test_search_members_empty_keyword(self, test_db_with_data, super_admin_user):
        """测试空关键词搜索"""
        data = test_db_with_data
        db = data['db']

        # 空关键词应该返回空列表
        results = SearchService.search_members(db, '', super_admin_user)
        assert len(results) == 0

    def test_search_members_no_results(self, test_db_with_data, super_admin_user):
        """测试无匹配结果"""
        data = test_db_with_data
        db = data['db']

        # 搜索不存在的关键词
        results = SearchService.search_members(db, '不存在的成员', super_admin_user)

        assert len(results) == 0

    def test_search_members_deduplication(self, test_db_with_data, super_admin_user):
        """测试成员搜索的家庭去重"""
        data = test_db_with_data
        db = data['db']

        # 搜索"测试"（所有成员的教友编号都包含"CH"）
        # 应该返回去重后的家庭列表
        results = SearchService.search_members(db, 'CH', super_admin_user)

        # 应该返回所有家庭，但每个家庭只出现一次
        assert len(results) == 3

        # 验证没有重复的家庭
        household_ids = [h.id for h in results]
        assert len(household_ids) == len(set(household_ids))


@pytest.mark.unit
class TestSearchServicePermissionFilter:
    """搜索权限过滤测试"""

    def test_super_admin_search_all_villages(self, test_db_with_data, super_admin_user):
        """测试超级管理员可搜索所有堂区"""
        data = test_db_with_data
        db = data['db']

        # 超级管理员搜索应该返回所有堂区的家庭
        results = SearchService.search_households(db, '测试', super_admin_user)

        # 应该返回所有3个家庭
        assert len(results) == 3

    def test_data_entry_search_own_village_only(self, test_db_with_data, data_entry_user):
        """测试录入员只能搜索所属堂区"""
        data = test_db_with_data
        db = data['db']
        village1 = data['villages']['village1']

        # 录入员搜索应该只返回所属堂区的家庭
        results = SearchService.search_households(db, '测试', data_entry_user)

        # 应该只返回堂区1的1个家庭
        assert len(results) == 1
        assert results[0].village_id == village1.id

    def test_observer_search_authorized_villages(self, test_db_with_data, observer_user):
        """测试观察员只能搜索授权堂区"""
        data = test_db_with_data
        db = data['db']
        village1 = data['villages']['village1']
        village2 = data['villages']['village2']

        # 观察员搜索应该只返回授权堂区的家庭
        results = SearchService.search_households(db, '测试', observer_user)

        # 应该返回堂区1和堂区2的2个家庭
        assert len(results) == 2

        village_ids = [h.village_id for h in results]
        assert village1.id in village_ids
        assert village2.id in village_ids

    def test_member_search_permission_filter(self, test_db_with_data, data_entry_user):
        """测试成员搜索的权限过滤"""
        data = test_db_with_data
        db = data['db']
        village1 = data['villages']['village1']

        # 录入员搜索成员应该只返回所属堂区的家庭
        results = SearchService.search_members(db, 'CH', data_entry_user)

        # 应该只返回堂区1的1个家庭
        assert len(results) == 1
        assert results[0].village_id == village1.id


@pytest.mark.integration
class TestSearchServiceIntegration:
    """搜索服务集成测试"""

    def test_search_workflow_household_to_members(self, test_db_with_data, super_admin_user):
        """测试搜索工作流：搜索家庭 -> 查看成员"""
        data = test_db_with_data
        db = data['db']

        # 1. 搜索家庭
        households = SearchService.search_households(db, '张三', super_admin_user)
        assert len(households) == 1

        # 2. 获取该家庭的成员
        household = households[0]
        members = household.members
        assert len(members) == 2

        # 3. 验证成员信息
        member_names = [m.name for m in members]
        assert '张三' in member_names
        assert '李四' in member_names

    def test_search_workflow_member_to_household(self, test_db_with_data, super_admin_user):
        """测试搜索工作流：搜索成员 -> 查看家庭"""
        data = test_db_with_data
        db = data['db']

        # 1. 通过成员姓名搜索
        households = SearchService.search_members(db, '李四', super_admin_user)
        assert len(households) == 1

        # 2. 获取家庭信息
        household = households[0]
        assert household.head_of_household == '张三'

        # 3. 验证家庭包含该成员
        member_names = [m.name for m in household.members]
        assert '李四' in member_names

    def test_cross_field_search(self, test_db_with_data, super_admin_user):
        """测试跨字段搜索"""
        data = test_db_with_data
        db = data['db']

        # 搜索"测试"关键词，应该匹配多个字段
        household_results = SearchService.search_households(db, '测试', super_admin_user)
        member_results = SearchService.search_members(db, '若瑟', super_admin_user)

        # 验证搜索结果
        assert len(household_results) > 0
        assert len(member_results) > 0

    def test_search_performance_with_large_dataset(self, test_db_with_data, super_admin_user):
        """测试大数据集搜索性能"""
        data = test_db_with_data
        db = data['db']
        village1 = data['villages']['village1']

        # 创建更多测试数据
        from src.models.household import Household, Member

        for i in range(100):
            household = Household(
                village_id=village1.id,
                plot_number=1000 + i,
                address=f'性能测试地址{i}',
                phone=f'1380013{i:04d}',
                head_of_household=f'测试户主{i}'
            )
            db.add(household)
            db.commit()

            member = Member(
                household_id=household.id,
                name=f'测试成员{i}',
                baptismal_name=f'圣名{i}',
                church_id=f'PERF{i:04d}',
                gender='男' if i % 2 == 0 else '女',
                relation_to_head='本人'
            )
            db.add(member)

        db.commit()

        # 执行搜索
        import time
        start_time = time.time()
        results = SearchService.search_households(db, '测试', super_admin_user)
        end_time = time.time()

        # 验证结果
        assert len(results) > 100

        # 验证性能（应该在1秒内完成）
        search_time = end_time - start_time
        assert search_time < 1.0, f"搜索耗时 {search_time:.3f}秒，超过1秒阈值"
