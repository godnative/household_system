from sqlalchemy.orm import Session
from src.models import Role, Permission, role_permissions

class PermissionService:
    @staticmethod
    def get_all_roles(db: Session):
        """获取所有角色"""
        return db.query(Role).all()
    
    @staticmethod
    def get_role_by_id(db: Session, role_id: int) -> Role:
        """根据ID获取角色"""
        return db.query(Role).filter(Role.id == role_id).first()
    
    @staticmethod
    def create_role(db: Session, name: str, description: str = None) -> Role:
        """创建新角色"""
        role = Role(name=name, description=description)
        db.add(role)
        db.commit()
        db.refresh(role)
        return role
    
    @staticmethod
    def update_role(db: Session, role_id: int, **kwargs) -> Role:
        """更新角色信息"""
        role = db.query(Role).filter(Role.id == role_id).first()
        if not role:
            return None
        
        for key, value in kwargs.items():
            setattr(role, key, value)
        
        db.commit()
        db.refresh(role)
        return role
    
    @staticmethod
    def delete_role(db: Session, role_id: int) -> bool:
        """删除角色"""
        role = db.query(Role).filter(Role.id == role_id).first()
        if not role:
            return False
        
        db.delete(role)
        db.commit()
        return True
    
    @staticmethod
    def get_all_permissions(db: Session):
        """获取所有权限"""
        return db.query(Permission).all()
    
    @staticmethod
    def get_permission_by_id(db: Session, permission_id: int) -> Permission:
        """根据ID获取权限"""
        return db.query(Permission).filter(Permission.id == permission_id).first()
    
    @staticmethod
    def assign_permissions_to_role(db: Session, role_id: int, permission_ids: list) -> Role:
        """为角色分配权限"""
        role = db.query(Role).filter(Role.id == role_id).first()
        if not role:
            return None
        
        # 清除现有权限
        role.permissions = []
        
        # 添加新权限
        permissions = db.query(Permission).filter(Permission.id.in_(permission_ids)).all()
        role.permissions = permissions
        
        db.commit()
        db.refresh(role)
        return role