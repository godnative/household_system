from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import get_current_user
from app.models.auth import User
from app.schemas.auth import ChangePasswordRequest, CurrentUserResponse, LoginRequest, TokenResponse
from app.services.auth_service import authenticate_user, build_current_user_response, create_access_token
from app.services.user_service import change_current_user_password


router = APIRouter(prefix='/api/v1/auth', tags=['auth'])


@router.post('/login', response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = authenticate_user(db, payload.username, payload.password)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='用户名或密码错误')
    token = create_access_token(str(user.id))
    return TokenResponse(access_token=token)


@router.get('/me', response_model=CurrentUserResponse)
def me(current_user: User = Depends(get_current_user)) -> CurrentUserResponse:
    return CurrentUserResponse(**build_current_user_response(current_user))


@router.post('/change-password')
def change_password(
    payload: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    change_current_user_password(db, current_user, payload.old_password, payload.new_password)
    return {'message': '密码修改成功'}
