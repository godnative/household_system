from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.auth import Permission, Role, User
from app.schemas.role_admin import PermissionOption, RoleDetailResponse, RoleListItem

SYSTEM_ROLE_NAMES = {'super_admin', 'data_entry', 'observer'}


def _serialize_permission(permission: Permission) -> PermissionOption:
    return PermissionOption(id=permission.id, name=permission.name, description=permission.description)


def _serialize_role(role: Role) -> RoleListItem:
    return RoleListItem(
        id=role.id,
        name=role.name,
        description=role.description,
        permissions=[_serialize_permission(permission) for permission in role.permissions],
    )


def list_roles(db: Session) -> list[RoleListItem]:
    roles = db.query(Role).order_by(Role.id.asc()).all()
    return [_serialize_role(role) for role in roles]


def get_role_or_404(db: Session, role_id: int) -> Role:
    role = db.query(Role).filter(Role.id == role_id).first()
    if role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='角色不存在')
    return role


def get_permission_options(db: Session) -> list[PermissionOption]:
    permissions = db.query(Permission).order_by(Permission.id.asc()).all()
    return [_serialize_permission(permission) for permission in permissions]


def _get_permissions(db: Session, permission_ids: list[int]) -> list[Permission]:
    if not permission_ids:
        return []
    permissions = db.query(Permission).filter(Permission.id.in_(permission_ids)).order_by(Permission.id.asc()).all()
    if len(permissions) != len(set(permission_ids)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='权限不存在')
    return permissions


def create_role(db: Session, name: str, description: str, permission_ids: list[int]) -> Role:
    existing = db.query(Role).filter(Role.name == name).first()
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='角色名已存在')
    role = Role(name=name, description=description)
    role.permissions = _get_permissions(db, permission_ids)
    db.add(role)
    db.commit()
    db.refresh(role)
    return role


def update_role(db: Session, role: Role, name: str, description: str, permission_ids: list[int]) -> Role:
    existing = db.query(Role).filter(Role.name == name, Role.id != role.id).first()
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='角色名已存在')
    role.name = name
    role.description = description
    role.permissions = _get_permissions(db, permission_ids)
    db.commit()
    db.refresh(role)
    return role


def serialize_role_detail(role: Role) -> RoleDetailResponse:
    data = _serialize_role(role)
    return RoleDetailResponse(**data.model_dump())


def ensure_role_mutable(role: Role) -> None:
    if role.name in SYSTEM_ROLE_NAMES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='系统内置角色不可删除')
    if role.users:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='当前角色仍被用户使用')
