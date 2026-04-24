from pydantic import BaseModel, Field

from app.schemas.auth import RoleSummary


class VillageOption(BaseModel):
    id: int
    name: str


class UserListItem(BaseModel):
    id: int
    username: str
    is_active: bool
    role: RoleSummary
    village_id: int | None
    accessible_village_ids: list[int]


class UserDetailResponse(UserListItem):
    created_at: str


class UserCreateRequest(BaseModel):
    username: str
    password: str
    role_id: int
    is_active: bool = True
    village_id: int | None = None
    accessible_village_ids: list[int] = Field(default_factory=list)


class UserUpdateRequest(BaseModel):
    role_id: int
    is_active: bool = True
    village_id: int | None = None
    accessible_village_ids: list[int] = Field(default_factory=list)


class PasswordResetRequest(BaseModel):
    new_password: str
