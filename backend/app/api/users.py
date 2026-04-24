from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import get_current_user, require_permission
from app.models.auth import User
from app.schemas.user_admin import PasswordResetRequest, UserCreateRequest, UserDetailResponse, UserListItem, UserUpdateRequest, VillageOption
from app.services.user_service import (
    create_user,
    get_user_or_404,
    list_users,
    list_village_options,
    reset_user_password,
    serialize_user_detail,
    update_user,
)


router = APIRouter(prefix='/api/v1/users', tags=['users'])


@router.get('', response_model=list[UserListItem])
def get_users(
    db: Session = Depends(get_db),
    _: User = Depends(require_permission('user_manage')),
) -> list[UserListItem]:
    return list_users(db)


@router.get('/options/villages', response_model=list[VillageOption])
def get_village_options(
    db: Session = Depends(get_db),
    _: User = Depends(require_permission('user_manage')),
) -> list[VillageOption]:
    return [VillageOption(**option) for option in list_village_options(db)]


@router.get('/{user_id}', response_model=UserDetailResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission('user_manage')),
) -> UserDetailResponse:
    user = get_user_or_404(db, user_id)
    return serialize_user_detail(user)


@router.post('', response_model=UserDetailResponse)
def post_user(
    payload: UserCreateRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission('user_manage')),
) -> UserDetailResponse:
    user = create_user(db, payload)
    return serialize_user_detail(user)


@router.put('/{user_id}', response_model=UserDetailResponse)
def put_user(
    user_id: int,
    payload: UserUpdateRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission('user_manage')),
) -> UserDetailResponse:
    user = get_user_or_404(db, user_id)
    user = update_user(db, user, payload.role_id, payload.is_active, payload.village_id, payload.accessible_village_ids)
    return serialize_user_detail(user)


@router.put('/{user_id}/password')
def put_user_password(
    user_id: int,
    payload: PasswordResetRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission('user_manage')),
) -> dict:
    user = get_user_or_404(db, user_id)
    reset_user_password(db, user, payload.new_password)
    return {'message': '密码重置成功'}
