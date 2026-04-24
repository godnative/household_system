from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.auth import Permission, Role, User, Village
from app.schemas.auth import RoleSummary
from app.schemas.user_admin import UserCreateRequest, UserDetailResponse, UserListItem
from app.services.auth_service import get_user_by_username, hash_password, verify_password


ROLE_SCOPE_RULES = {
    'super_admin': {'requires_village': False, 'allows_accessible_villages': False},
    'data_entry': {'requires_village': True, 'allows_accessible_villages': False},
    'observer': {'requires_village': False, 'allows_accessible_villages': True},
}


def _build_role_summary(role: Role) -> RoleSummary:
    return RoleSummary(id=role.id, name=role.name, description=role.description)


def _serialize_user(user: User) -> UserListItem:
    return UserListItem(
        id=user.id,
        username=user.username,
        is_active=user.is_active,
        role=_build_role_summary(user.role),
        village_id=user.village_id,
        accessible_village_ids=[village.id for village in user.accessible_villages],
    )


def serialize_user_detail(user: User) -> UserDetailResponse:
    base = _serialize_user(user)
    return UserDetailResponse(**base.model_dump(), created_at=user.created_at.isoformat())


def list_users(db: Session) -> list[UserListItem]:
    users = db.query(User).order_by(User.id.asc()).all()
    return [_serialize_user(user) for user in users]


def get_user_or_404(db: Session, user_id: int) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='用户不存在')
    return user


def _get_role_or_404(db: Session, role_id: int) -> Role:
    role = db.query(Role).filter(Role.id == role_id).first()
    if role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='角色不存在')
    return role


def _get_villages(db: Session, village_ids: list[int]) -> list[Village]:
    if not village_ids:
        return []
    villages = db.query(Village).filter(Village.id.in_(village_ids)).order_by(Village.id.asc()).all()
    if len(villages) != len(set(village_ids)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='堂区不存在')
    return villages


def _validate_scope(role: Role, village_id: int | None, accessible_village_ids: list[int]) -> tuple[int | None, list[int]]:
    rule = ROLE_SCOPE_RULES.get(role.name)
    if rule is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='暂不支持该角色范围配置')

    if rule['requires_village'] and village_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='当前角色必须选择所属堂区')

    if rule['requires_village']:
        return village_id, []

    if rule['allows_accessible_villages']:
        return None, accessible_village_ids

    return None, []


def create_user(db: Session, payload: UserCreateRequest) -> User:
    if get_user_by_username(db, payload.username):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='用户名已存在')

    role = _get_role_or_404(db, payload.role_id)
    village_id, accessible_village_ids = _validate_scope(role, payload.village_id, payload.accessible_village_ids)
    if village_id is not None:
        _get_villages(db, [village_id])
    villages = _get_villages(db, accessible_village_ids)

    user = User(
        username=payload.username,
        password_hash=hash_password(payload.password),
        role_id=role.id,
        village_id=village_id,
        is_active=payload.is_active,
    )
    user.accessible_villages = villages
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user(db: Session, user: User, role_id: int, is_active: bool, village_id: int | None, accessible_village_ids: list[int]) -> User:
    role = _get_role_or_404(db, role_id)
    normalized_village_id, normalized_accessible_village_ids = _validate_scope(role, village_id, accessible_village_ids)
    if normalized_village_id is not None:
        _get_villages(db, [normalized_village_id])
    villages = _get_villages(db, normalized_accessible_village_ids)

    user.role_id = role.id
    user.village_id = normalized_village_id
    user.is_active = is_active
    user.accessible_villages = villages
    db.commit()
    db.refresh(user)
    return user


def reset_user_password(db: Session, user: User, new_password: str) -> User:
    user.password_hash = hash_password(new_password)
    db.commit()
    db.refresh(user)
    return user


def change_current_user_password(db: Session, user: User, old_password: str, new_password: str) -> User:
    if not verify_password(old_password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='旧密码不正确')
    user.password_hash = hash_password(new_password)
    db.commit()
    db.refresh(user)
    return user


def list_village_options(db: Session) -> list[dict]:
    villages = db.query(Village).order_by(Village.id.asc()).all()
    return [{'id': village.id, 'name': village.name} for village in villages]
