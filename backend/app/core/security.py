from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.auth import User
from app.services.auth_service import decode_access_token, get_user_by_id


bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='未登录')

    payload = decode_access_token(credentials.credentials)
    user = get_user_by_id(db, int(payload['sub']))
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='登录状态无效')
    return user


def require_permission(permission_name: str):
    def dependency(user: User = Depends(get_current_user)) -> User:
        permission_names = {permission.name for permission in user.role.permissions}
        if permission_name not in permission_names:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='权限不足')
        return user

    return dependency


def require_any_permission(permission_names: list[str]):
    def dependency(user: User = Depends(get_current_user)) -> User:
        current_permission_names = {permission.name for permission in user.role.permissions}
        if not any(permission_name in current_permission_names for permission_name in permission_names):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='权限不足')
        return user

    return dependency
