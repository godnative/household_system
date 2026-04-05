from . import create_tables, Role, Permission, User, Village
from .base import SessionLocal
import bcrypt

def init_database():
    # 创建表结构
    create_tables()
    
    # 创建数据库会话
    db = SessionLocal()
    
    try:
        # 检查是否已有数据
        if db.query(Role).count() == 0:
            # 创建默认权限
            permissions = [
                Permission(name='user_manage', description='用户管理'),
                Permission(name='role_manage', description='角色管理'),
                Permission(name='village_manage', description='村管理'),
                Permission(name='household_manage', description='家庭管理'),
                Permission(name='member_manage', description='成员管理')
            ]
            db.add_all(permissions)
            db.commit()
            
            # 创建默认角色
            admin_role = Role(name='超级管理员', description='拥有所有权限')
            village_admin_role = Role(name='村管理员', description='管理本村的所有数据')
            operator_role = Role(name='操作员', description='只能操作指定范围内的数据')
            
            # 为角色分配权限
            admin_role.permissions = permissions
            village_admin_role.permissions = permissions[3:]
            operator_role.permissions = [permissions[4]]
            
            db.add_all([admin_role, village_admin_role, operator_role])
            db.commit()
            
            # 创建默认超级管理员用户
            hashed_password = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt())
            admin_user = User(
                username='admin',
                password_hash=hashed_password.decode('utf-8'),
                role_id=admin_role.id
            )
            db.add(admin_user)
            db.commit()
            
            # 创建默认村
            default_village = Village(
                name='默认村',
                code='001',
                description='系统默认村'
            )
            db.add(default_village)
            db.commit()
            
            print('数据库初始化成功！')
        else:
            print('数据库已有数据，跳过初始化。')
    except Exception as e:
        print(f'数据库初始化失败: {e}')
        db.rollback()
    finally:
        db.close()

if __name__ == '__main__':
    init_database()