from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import get_current_user, require_permission
from app.models.auth import User
from app.schemas.role_admin import PermissionOption, RoleCreateRequest, RoleDetailResponse, RoleListItem, RoleUpdateRequest
from app.services.role_service import (
    create_role,
    ensure_role_mutable,
    get_permission_options,
    get_role_or_404,
    list_roles,
    serialize_role_detail,
    update_role,
)


router = APIRouter(prefix='/api/v1/roles', tags=['roles'])


@router.get('', response_model=list[RoleListItem])
def get_roles(
    db: Session = Depends(get_db),
    _: User = Depends(require_permission('role_manage')),
) -> list[RoleListItem]:
    return list_roles(db)


@router.get('/options/permissions', response_model=list[PermissionOption])
def get_permission_options_endpoint(
    db: Session = Depends(get_db),
    _: User = Depends(require_permission('role_manage')),
) -> list[PermissionOption]:
    return get_permission_options(db)


@router.get('/{role_id}', response_model=RoleDetailResponse)
def get_role(
    role_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission('role_manage')),
) -> RoleDetailResponse:
    role = get_role_or_404(db, role_id)
    return serialize_role_detail(role)


@router.post('', response_model=RoleDetailResponse)
def post_role(
    payload: RoleCreateRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission('role_manage')),
) -> RoleDetailResponse:
    role = create_role(db, payload.name, payload.description, payload.permission_ids)
    return serialize_role_detail(role)


@router.put('/{role_id}', response_model=RoleDetailResponse)
def put_role(
    role_id: int,
    payload: RoleUpdateRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission('role_manage')),
) -> RoleDetailResponse:
    role = get_role_or_404(db, role_id)
    role = update_role(db, role, payload.name, payload.description, payload.permission_ids)
    return serialize_role_detail(role)


@router.delete('/{role_id}')
def delete_role(
    role_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission('role_manage')),
) -> dict:
    role = get_role_or_404(db, role_id)
    ensure_role_mutable(role)
    db.delete(role)
    db.commit()
    return {'message': '角色已删除'}
