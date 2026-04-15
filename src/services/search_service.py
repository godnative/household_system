# -*- coding: utf-8 -*-
"""
搜索服务模块
提供家庭和成员的多字段模糊搜索功能
"""

from typing import List
from sqlalchemy import or_, cast, String
from sqlalchemy.orm import Session, joinedload

from src.models.household import Household, Member, Village
from src.services.auth_service import AuthService


class SearchService:
    """搜索服务类"""

    @staticmethod
    def search_households(db: Session, keyword: str, user) -> List[Household]:
        """
        搜索家庭

        Args:
            db: 数据库会话
            keyword: 搜索关键词
            user: 当前用户（用于权限过滤）

        Returns:
            匹配的家庭列表
        """
        if not keyword or not keyword.strip():
            return []

        # 1. 获取用户可访问堂区
        accessible_village_ids = AuthService.get_user_accessible_villages(user)

        # 2. 构建基础查询
        query = db.query(Household)

        # 3. 权限过滤
        if accessible_village_ids is not None:
            query = query.filter(Household.village_id.in_(accessible_village_ids))

        # 4. 关键词过滤（多字段 OR 模糊匹配）
        search_pattern = f"%{keyword.strip()}%"
        query = query.filter(
            or_(
                Household.head_of_household.like(search_pattern),
                Household.address.like(search_pattern),
                Household.phone.like(search_pattern),
                cast(Household.plot_number, String).like(search_pattern)
            )
        )

        # 5. 关联 village 避免 N+1 查询
        query = query.options(joinedload(Household.village))

        return query.all()

    @staticmethod
    def search_members(db: Session, keyword: str, user) -> List[Household]:
        """
        搜索成员，返回其所属家庭（去重）

        Args:
            db: 数据库会话
            keyword: 搜索关键词
            user: 当前用户（用于权限过滤）

        Returns:
            包含匹配成员的家庭列表（去重）
        """
        if not keyword or not keyword.strip():
            return []

        # 1. 获取用户可访问堂区
        accessible_village_ids = AuthService.get_user_accessible_villages(user)

        # 2. 构建成员查询
        query = db.query(Member).join(Household).join(Village)

        # 3. 权限过滤
        if accessible_village_ids is not None:
            query = query.filter(Village.id.in_(accessible_village_ids))

        # 4. 关键词过滤（20+ 字段 OR 模糊匹配）
        search_pattern = f"%{keyword.strip()}%"
        query = query.filter(
            or_(
                # 基本信息
                Member.name.like(search_pattern),
                Member.baptismal_name.like(search_pattern),
                Member.church_id.like(search_pattern),
                Member.occupation.like(search_pattern),
                Member.association.like(search_pattern),
                # 备注字段
                Member.note.like(search_pattern),
                Member.baptism_note.like(search_pattern),
                # 圣洗相关
                Member.baptism_priest.like(search_pattern),
                Member.baptism_godparent.like(search_pattern),
                # 补礼相关
                Member.supplementary_priest.like(search_pattern),
                Member.supplementary_place.like(search_pattern),
                # 坚振相关
                Member.confirmation_priest.like(search_pattern),
                Member.confirmation_godparent.like(search_pattern),
                Member.confirmation_name.like(search_pattern),
                Member.confirmation_place.like(search_pattern),
                # 婚配相关
                Member.marriage_priest.like(search_pattern),
                Member.marriage_witness.like(search_pattern),
                Member.marriage_place.like(search_pattern),
                Member.marriage_dispensation_item.like(search_pattern),
                Member.marriage_dispensation_priest.like(search_pattern),
                # 傅油相关
                Member.anointing_priest.like(search_pattern),
                Member.anointing_place.like(search_pattern)
            )
        )

        # 5. 获取成员列表
        members = query.all()

        # 6. 提取家庭并去重
        household_ids = set(m.household_id for m in members)

        if not household_ids:
            return []

        households = (
            db.query(Household)
            .filter(Household.id.in_(household_ids))
            .options(joinedload(Household.village))
            .all()
        )

        return households
