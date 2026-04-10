from sqlalchemy import Column, Integer, String, Text, ForeignKey, Table
from sqlalchemy.orm import relationship
from .base import Base

# 角色权限关联表
role_permissions = Table('role_permissions', Base.metadata,
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('permissions.id'), primary_key=True)
)

# 用户-堂区访问权限关联表（用于观察员的细粒度权限控制）
user_village_access = Table('user_village_access', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('village_id', Integer, ForeignKey('villages.id'), primary_key=True)
)

class Role(Base):
    __tablename__ = 'roles'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    
    # 关联关系
    users = relationship('User', back_populates='role')
    permissions = relationship('Permission', secondary=role_permissions, back_populates='roles')

class Permission(Base):
    __tablename__ = 'permissions'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    
    # 关联关系
    roles = relationship('Role', secondary=role_permissions, back_populates='permissions')