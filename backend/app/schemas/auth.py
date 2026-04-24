from datetime import datetime

from pydantic import BaseModel


class RoleSummary(BaseModel):
    id: int
    name: str
    description: str


class CurrentUserResponse(BaseModel):
    id: int
    username: str
    is_active: bool
    role: RoleSummary
    role_names: list[str]
    permission_names: list[str]
    village_id: int | None
    accessible_village_ids: list[int]
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = 'bearer'


class LoginRequest(BaseModel):
    username: str
    password: str


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str
