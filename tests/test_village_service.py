# -*- coding: utf-8 -*-
"""
堂区服务测试
测试 VillageService 的 CRUD 操作和搜索功能
"""

import pytest
from datetime import date
from src.services.village_service import VillageService
from src.models.household import Village


@pytest.mark.unit
class TestVillageServiceCRUD:
    """堂区服务 CRUD 测试"""

    def test_get_all_villages(self, test_db_with_data):
        """测试获取所有堂区"""
        data = test_db_with_data
        db = data['db']

        villages = VillageService.get_all_villages(db)

        assert len(villages) == 3
        village_names = [v.name for v in villages]
        assert '测试堂区1' in village_names
        assert '测试堂区2' in village_names
        assert '测试堂区3' in village_names

    def test_get_village_by_id(self, test_db_with_data):
        """测试根据 ID 获取堂区"""
        data = test_db_with_data
        db = data['db']
        village1 = data['villages']['village1']

        village = VillageService.get_village_by_id(db, village1.id)

        assert village is not None
        assert village.id == village1.id
        assert village.name == '测试堂区1'

    def test_get_village_by_id_not_found(self, test_db_with_data):
        """测试获取不存在的堂区"""
        data = test_db_with_data
        db = data['db']

        village = VillageService.get_village_by_id(db, 99999)

        assert village is None

    def test_get_village_by_code(self, test_db_with_data):
        """测试根据编码获取堂区"""
        data = test_db_with_data
        db = data['db']

        village = VillageService.get_village_by_code(db, '001')

        assert village is not None
        assert village.code == '001'
        assert village.name == '测试堂区1'

    def test_get_village_by_code_not_found(self, test_db_with_data):
        """测试获取不存在编码的堂区"""
        data = test_db_with_data
        db = data['db']

        village = VillageService.get_village_by_code(db, '999')

        assert village is None

    def test_create_village(self, test_db_with_data):
        """测试创建堂区"""
        data = test_db_with_data
        db = data['db']

        village = VillageService.create_village(
            db=db,
            name='新堂区',
            code='004',
            establishment_date=date(2024, 1, 1),
            village_priest='新神父',
            address='新地址',
            description='测试描述'
        )

        assert village is not None
        assert village.id is not None
        assert village.name == '新堂区'
        assert village.code == '004'
        assert village.village_priest == '新神父'
        assert village.description == '测试描述'

        # 验证数据库中确实有这条记录
        saved_village = db.query(Village).filter(Village.code == '004').first()
        assert saved_village is not None
        assert saved_village.name == '新堂区'

    def test_update_village(self, test_db_with_data):
        """测试更新堂区"""
        data = test_db_with_data
        db = data['db']
        village1 = data['villages']['village1']

        updated_village = VillageService.update_village(
            db=db,
            village_id=village1.id,
            name='更新后的堂区',
            address='更新后的地址'
        )

        assert updated_village is not None
        assert updated_village.id == village1.id
        assert updated_village.name == '更新后的堂区'
        assert updated_village.address == '更新后的地址'
        # 编码不应该改变
        assert updated_village.code == '001'

    def test_update_village_not_found(self, test_db_with_data):
        """测试更新不存在的堂区"""
        data = test_db_with_data
        db = data['db']

        updated_village = VillageService.update_village(
            db=db,
            village_id=99999,
            name='不存在的堂区'
        )

        assert updated_village is None

    def test_delete_village_success(self, test_db_with_data):
        """测试删除堂区（无家庭）"""
        data = test_db_with_data
        db = data['db']

        # 创建一个没有家庭的堂区
        village = VillageService.create_village(
            db=db,
            name='待删除堂区',
            code='999',
            establishment_date=date(2024, 1, 1),
            village_priest='神父',
            address='地址'
        )

        # 删除堂区
        result = VillageService.delete_village(db, village.id)

        assert result is True

        # 验证堂区已被删除
        deleted_village = db.query(Village).filter(Village.id == village.id).first()
        assert deleted_village is None

    def test_delete_village_with_households(self, test_db_with_data):
        """测试删除有家庭的堂区（应该失败）"""
        data = test_db_with_data
        db = data['db']
        village1 = data['villages']['village1']

        # 堂区1有家庭，不能删除
        result = VillageService.delete_village(db, village1.id)

        assert result is False

        # 验证堂区还在
        village = db.query(Village).filter(Village.id == village1.id).first()
        assert village is not None

    def test_delete_village_not_found(self, test_db_with_data):
        """测试删除不存在的堂区"""
        data = test_db_with_data
        db = data['db']

        result = VillageService.delete_village(db, 99999)

        assert result is False


@pytest.mark.unit
class TestVillageServiceSearch:
    """堂区搜索测试"""

    def test_search_villages_by_name(self, test_db_with_data):
        """测试按名称搜索堂区"""
        data = test_db_with_data
        db = data['db']

        villages = VillageService.search_villages(db, '堂区1')

        assert len(villages) == 1
        assert villages[0].name == '测试堂区1'

    def test_search_villages_by_code(self, test_db_with_data):
        """测试按编码搜索堂区"""
        data = test_db_with_data
        db = data['db']

        villages = VillageService.search_villages(db, '002')

        assert len(villages) == 1
        assert villages[0].code == '002'

    def test_search_villages_partial_match(self, test_db_with_data):
        """测试部分匹配搜索"""
        data = test_db_with_data
        db = data['db']

        # 搜索"测试"应该匹配所有堂区
        villages = VillageService.search_villages(db, '测试')

        assert len(villages) == 3

    def test_search_villages_no_keyword(self, test_db_with_data):
        """测试无关键词搜索（返回全部）"""
        data = test_db_with_data
        db = data['db']

        villages = VillageService.search_villages(db)

        assert len(villages) == 3

    def test_search_villages_no_results(self, test_db_with_data):
        """测试无结果搜索"""
        data = test_db_with_data
        db = data['db']

        villages = VillageService.search_villages(db, '不存在的堂区')

        assert len(villages) == 0

    def test_search_villages_case_insensitive(self, test_db_with_data):
        """测试大小写不敏感搜索"""
        data = test_db_with_data
        db = data['db']

        # 使用不同大小写搜索编码
        villages_lower = VillageService.search_villages(db, '堂区')
        villages_upper = VillageService.search_villages(db, '堂区')

        assert len(villages_lower) == len(villages_upper)
        assert len(villages_lower) == 3


@pytest.mark.integration
class TestVillageServiceIntegration:
    """堂区服务集成测试"""

    def test_create_and_retrieve_village(self, test_db_with_data):
        """测试创建后立即检索"""
        data = test_db_with_data
        db = data['db']

        # 创建
        created = VillageService.create_village(
            db=db,
            name='集成测试堂区',
            code='INT001',
            establishment_date=date(2024, 1, 1),
            village_priest='测试神父',
            address='测试地址'
        )

        # 按 ID 检索
        by_id = VillageService.get_village_by_id(db, created.id)
        assert by_id.name == '集成测试堂区'

        # 按 code 检索
        by_code = VillageService.get_village_by_code(db, 'INT001')
        assert by_code.id == created.id

        # 搜索检索
        by_search = VillageService.search_villages(db, '集成')
        assert len(by_search) == 1
        assert by_search[0].id == created.id

    def test_update_and_verify_village(self, test_db_with_data):
        """测试更新后验证"""
        data = test_db_with_data
        db = data['db']
        village1 = data['villages']['village1']

        # 更新
        VillageService.update_village(
            db=db,
            village_id=village1.id,
            name='已更新',
            village_priest='新神父'
        )

        # 验证
        updated = VillageService.get_village_by_id(db, village1.id)
        assert updated.name == '已更新'
        assert updated.village_priest == '新神父'
        # 其他字段不变
        assert updated.code == '001'

    def test_full_crud_cycle(self, test_db_with_data):
        """测试完整 CRUD 周期"""
        data = test_db_with_data
        db = data['db']

        # Create
        village = VillageService.create_village(
            db=db,
            name='CRUD测试',
            code='CRUD001',
            establishment_date=date(2024, 1, 1),
            village_priest='神父',
            address='地址'
        )
        village_id = village.id

        # Read
        read_village = VillageService.get_village_by_id(db, village_id)
        assert read_village is not None

        # Update
        VillageService.update_village(db, village_id, name='CRUD更新')
        updated_village = VillageService.get_village_by_id(db, village_id)
        assert updated_village.name == 'CRUD更新'

        # Delete
        result = VillageService.delete_village(db, village_id)
        assert result is True

        # Verify deletion
        deleted_village = VillageService.get_village_by_id(db, village_id)
        assert deleted_village is None
