from sqlalchemy.orm import Session
from src.models import User, Role, Permission
from src.constants import PERM_USER_MANAGE, PERM_ROLE_MANAGE
import bcrypt

class AuthService:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

    @staticmethod
    def get_password_hash(password: str) -> str:
        """获取密码哈希值"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> User:
        """验证用户身份"""
        user = db.query(User).filter(User.username == username).first()
        if not user:
            return None
        if not AuthService.verify_password(password, user.password_hash):
            return None
        return user

    @staticmethod
    def check_permission(user: User, permission_name: str) -> bool:
        """检查用户是否有指定权限"""
        if not user or not user.role:
            return False

        # 检查用户角色是否有该权限
        for permission in user.role.permissions:
            if permission.name == permission_name:
                return True
        return False

    @staticmethod
    def get_user_accessible_villages(user: User):
        """
        获取用户可访问的堂区ID列表

        Returns:
            None: 超级管理员，可访问所有堂区
            list[int]: 录入员/观察员，返回可访问的堂区ID列表
        """
        if not user or not user.role:
            return []

        # 超级管理员可以访问所有堂区
        if AuthService.check_permission(user, PERM_USER_MANAGE) or \
           AuthService.check_permission(user, PERM_ROLE_MANAGE):
            return None

        # 录入员：返回所属堂区
        if user.village_id:
            return [user.village_id]

        # 观察员：返回可访问堂区列表
        if user.accessible_villages:
            return [v.id for v in user.accessible_villages]

        return []

    @staticmethod
    def check_village_access(user: User, village_id: int) -> bool:
        """检查用户是否可以访问指定堂区"""
        accessible_villages = AuthService.get_user_accessible_villages(user)

        # None 表示可以访问所有堂区（超级管理员）
        if accessible_villages is None:
            return True

        return village_id in accessible_villages

    @staticmethod
    def check_household_access(user: User, household_id: int, db: Session) -> bool:
        """检查用户是否可以访问指定家庭（通过家庭所属堂区判断）"""
        from src.models import Household
        household = db.query(Household).filter(Household.id == household_id).first()
        if not household:
            return False

        return AuthService.check_village_access(user, household.village_id)

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> User:
        """根据用户名获取用户"""
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def create_user(db: Session, username: str, password: str, role_id: int, village_id: int = None) -> User:
        """创建新用户"""
        hashed_password = AuthService.get_password_hash(password)
        user = User(
            username=username,
            password_hash=hashed_password,
            role_id=role_id,
            village_id=village_id
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def update_user(db: Session, user_id: int, **kwargs) -> User:
        """更新用户信息"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None

        # 如果更新密码，需要重新哈希
        if 'password' in kwargs:
            kwargs['password_hash'] = AuthService.get_password_hash(kwargs.pop('password'))

        for key, value in kwargs.items():
            setattr(user, key, value)

        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        """删除用户"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False

        db.delete(user)
        db.commit()
        return True