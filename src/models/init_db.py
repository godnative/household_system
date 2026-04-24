from datetime import date

from . import create_tables, Role, Permission, User, Village
from .base import SessionLocal, ensure_database_parent_dir_exists
from src.constants import (
    PERM_USER_MANAGE, PERM_ROLE_MANAGE, PERM_VILLAGE_MANAGE,
    PERM_HOUSEHOLD_MANAGE, PERM_HOUSEHOLD_VIEW,
    PERM_MEMBER_MANAGE, PERM_MEMBER_VIEW,
    ROLE_SUPER_ADMIN, ROLE_DATA_ENTRY, ROLE_OBSERVER
)
from src.services.auth_service import AuthService

DEFAULT_PERMISSIONS = [
    (PERM_USER_MANAGE, '用户管理权限'),
    (PERM_ROLE_MANAGE, '角色管理权限'),
    (PERM_VILLAGE_MANAGE, '堂区管理权限'),
    (PERM_HOUSEHOLD_MANAGE, '家庭完整管理权限'),
    (PERM_HOUSEHOLD_VIEW, '家庭查看权限'),
    (PERM_MEMBER_MANAGE, '成员完整管理权限'),
    (PERM_MEMBER_VIEW, '成员查看权限'),
]

DEFAULT_ROLES = {
    ROLE_SUPER_ADMIN: [
        PERM_USER_MANAGE,
        PERM_ROLE_MANAGE,
        PERM_VILLAGE_MANAGE,
        PERM_HOUSEHOLD_MANAGE,
        PERM_HOUSEHOLD_VIEW,
        PERM_MEMBER_MANAGE,
        PERM_MEMBER_VIEW,
    ],
    ROLE_DATA_ENTRY: [PERM_HOUSEHOLD_MANAGE, PERM_MEMBER_MANAGE],
    ROLE_OBSERVER: [PERM_HOUSEHOLD_VIEW, PERM_MEMBER_VIEW],
}

DEFAULT_VILLAGE = {
    'name': '默认村',
    'code': '001',
    'establishment_date': date.today(),
    'village_priest': '默认神父',
    'address': '默认地址',
    'description': '系统默认村',
}

DEFAULT_ADMIN = {
    'username': 'admin',
    'password': 'admin123',
    'role': ROLE_SUPER_ADMIN,
}


def ensure_seed_data(db):
    permissions = {permission.name: permission for permission in db.query(Permission).all()}
    for key, description in DEFAULT_PERMISSIONS:
        if key not in permissions:
            permission = Permission(name=key, description=description)
            db.add(permission)
            permissions[key] = permission
    db.flush()

    roles = {role.name: role for role in db.query(Role).all()}
    for role_name, permission_keys in DEFAULT_ROLES.items():
        role = roles.get(role_name)
        if role is None:
            role = Role(name=role_name, description=role_name)
            db.add(role)
            roles[role_name] = role
        role.permissions = [permissions[key] for key in permission_keys]
    db.flush()

    village = db.query(Village).filter(Village.code == DEFAULT_VILLAGE['code']).first()
    if village is None:
        village = db.query(Village).filter(Village.name == DEFAULT_VILLAGE['name']).first()
    if village is None:
        village = Village(**DEFAULT_VILLAGE)
        db.add(village)
        db.flush()

    admin = AuthService.get_user_by_username(db, DEFAULT_ADMIN['username'])
    if admin is None:
        admin = User(
            username=DEFAULT_ADMIN['username'],
            password_hash=AuthService.get_password_hash(DEFAULT_ADMIN['password']),
            role_id=roles[DEFAULT_ADMIN['role']].id
        )
        db.add(admin)

    db.commit()


def ensure_database_initialized():
    ensure_database_parent_dir_exists()
    create_tables()
    db = SessionLocal()
    try:
        ensure_seed_data(db)
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def init_database():
    # 强制删除并重新创建表结构
    from .base import Base, engine
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        ensure_seed_data(db)
        print('数据库初始化成功！')
        print(f'创建了 {len(DEFAULT_PERMISSIONS)} 个权限')
        print(f'创建了 3 个角色：{ROLE_SUPER_ADMIN}、{ROLE_DATA_ENTRY}、{ROLE_OBSERVER}')
        print('创建了默认超级管理员用户（用户名: admin，密码: admin123）')
    except Exception as e:
        print(f'数据库初始化失败: {e}')
        db.rollback()
    finally:
        db.close()


if __name__ == '__main__':
    init_database()
