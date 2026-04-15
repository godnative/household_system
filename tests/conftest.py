# -*- coding: utf-8 -*-
"""
pytest 配置文件
提供测试共享的 fixtures
"""

import pytest
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.models.base import Base
from src.models.household import Village, Household, Member
from src.models.auth import Role, Permission
from src.models.user import User
from src.constants.permissions import (
    ROLE_SUPER_ADMIN, ROLE_DATA_ENTRY, ROLE_OBSERVER,
    PERM_USER_MANAGE, PERM_ROLE_MANAGE, PERM_VILLAGE_MANAGE,
    PERM_HOUSEHOLD_MANAGE, PERM_HOUSEHOLD_VIEW,
    PERM_MEMBER_MANAGE, PERM_MEMBER_VIEW
)


@pytest.fixture(scope='function')
def test_db():
    """创建测试数据库"""
    # 使用内存数据库
    engine = create_engine('sqlite:///:memory:', echo=False)

    # 创建所有表
    Base.metadata.create_all(engine)

    # 创建会话
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    yield db

    # 清理
    db.close()
    Base.metadata.drop_all(engine)


@pytest.fixture(scope='function')
def test_db_with_data(test_db):
    """创建带有基础测试数据的数据库"""
    db = test_db

    # 创建权限
    permissions = {
        PERM_USER_MANAGE: Permission(name=PERM_USER_MANAGE, description='用户管理'),
        PERM_ROLE_MANAGE: Permission(name=PERM_ROLE_MANAGE, description='角色管理'),
        PERM_VILLAGE_MANAGE: Permission(name=PERM_VILLAGE_MANAGE, description='堂区管理'),
        PERM_HOUSEHOLD_MANAGE: Permission(name=PERM_HOUSEHOLD_MANAGE, description='家庭完整管理'),
        PERM_HOUSEHOLD_VIEW: Permission(name=PERM_HOUSEHOLD_VIEW, description='家庭查看'),
        PERM_MEMBER_MANAGE: Permission(name=PERM_MEMBER_MANAGE, description='成员完整管理'),
        PERM_MEMBER_VIEW: Permission(name=PERM_MEMBER_VIEW, description='成员查看'),
    }

    for perm in permissions.values():
        db.add(perm)
    db.commit()

    # 创建角色
    super_admin_role = Role(
        name=ROLE_SUPER_ADMIN,
        description='超级管理员',
        permissions=list(permissions.values())
    )

    data_entry_role = Role(
        name=ROLE_DATA_ENTRY,
        description='录入员',
        permissions=[permissions[PERM_HOUSEHOLD_MANAGE], permissions[PERM_MEMBER_MANAGE]]
    )

    observer_role = Role(
        name=ROLE_OBSERVER,
        description='观察员',
        permissions=[permissions[PERM_HOUSEHOLD_VIEW], permissions[PERM_MEMBER_VIEW]]
    )

    db.add(super_admin_role)
    db.add(data_entry_role)
    db.add(observer_role)
    db.commit()

    # 创建堂区
    from datetime import date
    village1 = Village(
        code='001',
        name='测试堂区1',
        address='测试地址1',
        establishment_date=date(2000, 1, 1),
        village_priest='测试神父1'
    )
    village2 = Village(
        code='002',
        name='测试堂区2',
        address='测试地址2',
        establishment_date=date(2000, 1, 1),
        village_priest='测试神父2'
    )
    village3 = Village(
        code='003',
        name='测试堂区3',
        address='测试地址3',
        establishment_date=date(2000, 1, 1),
        village_priest='测试神父3'
    )

    db.add(village1)
    db.add(village2)
    db.add(village3)
    db.commit()

    # 创建用户
    import bcrypt

    super_admin = User(
        username='admin',
        role_id=super_admin_role.id,
        village_id=None,
        password_hash=bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    )

    data_entry = User(
        username='entry1',
        role_id=data_entry_role.id,
        village_id=village1.id,
        password_hash=bcrypt.hashpw('entry123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    )

    observer = User(
        username='observer1',
        role_id=observer_role.id,
        village_id=None,
        password_hash=bcrypt.hashpw('observer123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    )
    # 设置观察员可访问的堂区（多对多关系）
    observer.accessible_villages = [village1, village2]

    db.add(super_admin)
    db.add(data_entry)
    db.add(observer)
    db.commit()

    # 创建测试家庭和成员
    # 堂区1的家庭
    household1 = Household(
        village_id=village1.id,
        plot_number=101,
        address='测试地址101',
        phone='13800138001',
        head_of_household='张三'
    )
    db.add(household1)
    db.commit()

    member1 = Member(
        household_id=household1.id,
        name='张三',
        baptismal_name='若瑟',
        church_id='CH001',
        gender='男',
        occupation='教师',
        association='圣母军',
        relation_to_head='本人'
    )

    member2 = Member(
        household_id=household1.id,
        name='李四',
        baptismal_name='玛利亚',
        church_id='CH002',
        gender='女',
        occupation='医生',
        relation_to_head='配偶'
    )

    db.add(member1)
    db.add(member2)

    # 堂区2的家庭
    household2 = Household(
        village_id=village2.id,
        plot_number=201,
        address='测试地址201',
        phone='13900139001',
        head_of_household='王五'
    )
    db.add(household2)
    db.commit()

    member3 = Member(
        household_id=household2.id,
        name='王五',
        baptismal_name='保禄',
        church_id='CH003',
        gender='男',
        occupation='工程师',
        relation_to_head='本人'
    )

    db.add(member3)

    # 堂区3的家庭
    household3 = Household(
        village_id=village3.id,
        plot_number=301,
        address='测试地址301',
        phone='13700137001',
        head_of_household='赵六'
    )
    db.add(household3)
    db.commit()

    member4 = Member(
        household_id=household3.id,
        name='赵六',
        baptismal_name='伯多禄',
        church_id='CH004',
        gender='男',
        occupation='商人',
        baptism_priest='张神父',
        confirmation_priest='李神父',
        relation_to_head='本人'
    )

    db.add(member4)
    db.commit()

    # 刷新对象以获取最新数据
    db.refresh(super_admin)
    db.refresh(data_entry)
    db.refresh(observer)
    db.refresh(village1)
    db.refresh(village2)
    db.refresh(village3)
    db.refresh(household1)
    db.refresh(household2)
    db.refresh(household3)

    # 返回数据库会话和测试数据
    return {
        'db': db,
        'permissions': permissions,
        'roles': {
            'super_admin': super_admin_role,
            'data_entry': data_entry_role,
            'observer': observer_role
        },
        'users': {
            'super_admin': super_admin,
            'data_entry': data_entry,
            'observer': observer
        },
        'villages': {
            'village1': village1,
            'village2': village2,
            'village3': village3
        },
        'households': {
            'household1': household1,
            'household2': household2,
            'household3': household3
        },
        'members': {
            'member1': member1,
            'member2': member2,
            'member3': member3,
            'member4': member4
        }
    }


@pytest.fixture
def super_admin_user(test_db_with_data):
    """返回超级管理员用户"""
    return test_db_with_data['users']['super_admin']


@pytest.fixture
def data_entry_user(test_db_with_data):
    """返回录入员用户"""
    return test_db_with_data['users']['data_entry']


@pytest.fixture
def observer_user(test_db_with_data):
    """返回观察员用户"""
    return test_db_with_data['users']['observer']
