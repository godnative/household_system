from .base import Base, engine, get_db, SessionLocal
from .auth import Role, Permission, role_permissions
from .user import User
from .household import Village, Household, Member

# 导出所有模型
__all__ = [
    'Base', 'engine', 'get_db', 'SessionLocal',
    'Role', 'Permission', 'role_permissions',
    'User',
    'Village', 'Household', 'Member'
]

# 创建数据库表
def create_tables():
    Base.metadata.create_all(bind=engine)