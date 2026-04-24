from datetime import datetime, timezone, timedelta
import base64
import hashlib
import hmac
import json

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.settings import get_settings
from app.models.auth import Permission, Role, User, Village
from app.schemas.auth import RoleSummary


settings = get_settings()

DEFAULT_PERMISSIONS = [
    ('user_manage', '用户管理'),
    ('role_manage', '角色管理'),
    ('village_manage', '堂区管理'),
    ('household_manage', '家庭管理'),
    ('household_view', '家庭查看'),
    ('member_manage', '成员管理'),
    ('member_view', '成员查看'),
]

DEFAULT_ROLES = {
    'super_admin': ['user_manage', 'role_manage', 'village_manage', 'household_manage', 'household_view', 'member_manage', 'member_view'],
    'data_entry': ['household_manage', 'member_manage'],
    'observer': ['household_view', 'member_view'],
}

DEFAULT_ADMIN = {
    'username': 'admin',
    'password': 'admin123',
    'role': 'super_admin',
}

DEFAULT_VILLAGE = {
    'name': '默认堂区',
    'code': '001',
}


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def verify_password(password: str, password_hash: str) -> bool:
    return hash_password(password) == password_hash


def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    expire_at = datetime.now(timezone.utc) + (expires_delta or settings.access_token_expire_delta)
    payload = {'sub': subject, 'exp': int(expire_at.timestamp())}
    payload_json = json.dumps(payload, separators=(',', ':'), sort_keys=True).encode('utf-8')
    payload_b64 = base64.urlsafe_b64encode(payload_json).decode('utf-8').rstrip('=')
    signature = hmac.new(settings.jwt_secret_key.encode('utf-8'), payload_b64.encode('utf-8'), hashlib.sha256).digest()
    signature_b64 = base64.urlsafe_b64encode(signature).decode('utf-8').rstrip('=')
    return f'{payload_b64}.{signature_b64}'


def decode_access_token(token: str) -> dict:
    try:
        payload_b64, signature_b64 = token.split('.')
        expected_signature = hmac.new(settings.jwt_secret_key.encode('utf-8'), payload_b64.encode('utf-8'), hashlib.sha256).digest()
        actual_signature = base64.urlsafe_b64decode(signature_b64 + '=' * (-len(signature_b64) % 4))
        if not hmac.compare_digest(expected_signature, actual_signature):
            raise ValueError('invalid signature')
        payload_json = base64.urlsafe_b64decode(payload_b64 + '=' * (-len(payload_b64) % 4))
        payload = json.loads(payload_json.decode('utf-8'))
        if payload['exp'] < int(datetime.now(timezone.utc).timestamp()):
            raise ValueError('token expired')
        return payload
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='无效登录状态') from exc


def authenticate_user(db: Session, username: str, password: str) -> User | None:
    user = db.query(User).filter(User.username == username, User.is_active.is_(True)).first()
    if not user or not verify_password(password, user.password_hash):
        return None
    return user


def get_user_by_username(db: Session, username: str) -> User | None:
    return db.query(User).filter(User.username == username).first()


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def build_role_summary(role: Role) -> RoleSummary:
    return RoleSummary(id=role.id, name=role.name, description=role.description)


def build_current_user_response(user: User) -> dict:
    permission_names = [permission.name for permission in user.role.permissions]
    return {
        'id': user.id,
        'username': user.username,
        'is_active': user.is_active,
        'role': build_role_summary(user.role),
        'role_names': [user.role.name],
        'permission_names': permission_names,
        'village_id': user.village_id,
        'accessible_village_ids': [village.id for village in user.accessible_villages],
        'created_at': user.created_at,
    }


def ensure_seed_data(db: Session) -> None:
    permissions: dict[str, Permission] = {permission.name: permission for permission in db.query(Permission).all()}
    for key, description in DEFAULT_PERMISSIONS:
        if key not in permissions:
            permission = Permission(name=key, description=description)
            db.add(permission)
            permissions[key] = permission
    db.flush()

    roles: dict[str, Role] = {role.name: role for role in db.query(Role).all()}
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
        village = Village(name=DEFAULT_VILLAGE['name'], code=DEFAULT_VILLAGE['code'])
        db.add(village)
        db.flush()

    admin = db.query(User).filter(User.username == DEFAULT_ADMIN['username']).first()
    if admin is None:
        admin = User(
            username=DEFAULT_ADMIN['username'],
            password_hash=hash_password(DEFAULT_ADMIN['password']),
            role_id=roles[DEFAULT_ADMIN['role']].id,
            is_active=True,
        )
        db.add(admin)

    db.commit()
