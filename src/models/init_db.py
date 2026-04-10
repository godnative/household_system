from . import create_tables, Role, Permission, User, Village
from .base import SessionLocal
from src.constants import (
    PERM_USER_MANAGE, PERM_ROLE_MANAGE, PERM_VILLAGE_MANAGE,
    PERM_HOUSEHOLD_MANAGE, PERM_HOUSEHOLD_VIEW,
    PERM_MEMBER_MANAGE, PERM_MEMBER_VIEW,
    ROLE_SUPER_ADMIN, ROLE_DATA_ENTRY, ROLE_OBSERVER
)
import bcrypt

def init_database():
    # 强制删除并重新创建表结构
    from .base import Base, engine
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    # 创建数据库会话
    db = SessionLocal()

    try:
        # 检查是否已有数据
        if db.query(Role).count() == 0:
            # 创建默认权限
            permissions = [
                Permission(name=PERM_USER_MANAGE, description='用户管理权限'),
                Permission(name=PERM_ROLE_MANAGE, description='角色管理权限'),
                Permission(name=PERM_VILLAGE_MANAGE, description='堂区管理权限'),
                Permission(name=PERM_HOUSEHOLD_MANAGE, description='家庭完整管理权限'),
                Permission(name=PERM_HOUSEHOLD_VIEW, description='家庭查看权限'),
                Permission(name=PERM_MEMBER_MANAGE, description='成员完整管理权限'),
                Permission(name=PERM_MEMBER_VIEW, description='成员查看权限')
            ]
            db.add_all(permissions)
            db.commit()

            # 刷新以获取ID
            for p in permissions:
                db.refresh(p)

            # 创建默认角色
            # 1. 超级管理员 - 拥有所有权限
            super_admin_role = Role(name=ROLE_SUPER_ADMIN, description='拥有所有权限')
            super_admin_role.permissions = permissions
            db.add(super_admin_role)

            # 2. 录入员 - 可以完整管理指定堂区的数据
            data_entry_role = Role(name=ROLE_DATA_ENTRY, description='可以管理指定堂区的家庭和成员数据')
            data_entry_role.permissions = [p for p in permissions
                                          if p.name in [PERM_HOUSEHOLD_MANAGE, PERM_MEMBER_MANAGE]]
            db.add(data_entry_role)

            # 3. 观察员 - 只能查看指定堂区的数据
            observer_role = Role(name=ROLE_OBSERVER, description='只能查看指定堂区的家庭和成员数据')
            observer_role.permissions = [p for p in permissions
                                        if p.name in [PERM_HOUSEHOLD_VIEW, PERM_MEMBER_VIEW]]
            db.add(observer_role)

            db.commit()

            # 刷新角色以获取ID
            db.refresh(super_admin_role)
            db.refresh(data_entry_role)
            db.refresh(observer_role)

            # 创建默认超级管理员用户
            hashed_password = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt())
            admin_user = User(
                username='admin',
                password_hash=hashed_password.decode('utf-8'),
                role_id=super_admin_role.id
            )
            db.add(admin_user)
            db.commit()

            # 创建默认村
            from datetime import date
            default_village = Village(
                name='默认村',
                code='001',
                establishment_date=date.today(),
                village_priest='默认神父',
                address='默认地址',
                description='系统默认村'
            )
            db.add(default_village)
            db.commit()

            print('数据库初始化成功！')
            print(f'创建了 {len(permissions)} 个权限')
            print(f'创建了 3 个角色：{ROLE_SUPER_ADMIN}、{ROLE_DATA_ENTRY}、{ROLE_OBSERVER}')
            print('创建了默认超级管理员用户（用户名: admin，密码: admin123）')
        else:
            print('数据库已有数据，跳过初始化。')
    except Exception as e:
        print(f'数据库初始化失败: {e}')
        db.rollback()
    finally:
        db.close()

if __name__ == '__main__':
    init_database()