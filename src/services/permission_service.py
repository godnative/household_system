from sqlalchemy.orm import Session
from src.models import Role, Permission, role_permissions, User
from src.models.auth import user_village_access

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

    @staticmethod
    def assign_villages_to_user(db: Session, user_id: int, village_ids: list):
        """为用户（观察员）分配可访问的堂区"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None

        # 清除现有的堂区访问权限
        db.execute(user_village_access.delete().where(
            user_village_access.c.user_id == user_id
        ))

        # 添加新的堂区访问权限
        if village_ids:
            from src.models import Village
            villages = db.query(Village).filter(Village.id.in_(village_ids)).all()
            user.accessible_villages = villages

        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def get_user_villages(db: Session, user_id: int):
        """获取用户可访问的堂区列表"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return []

        return user.accessible_villages