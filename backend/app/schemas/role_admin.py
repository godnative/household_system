from pydantic import BaseModel, Field


class PermissionOption(BaseModel):
    id: int
    name: str
    description: str


class RoleListItem(BaseModel):
    id: int
    name: str
    description: str
    permissions: list[PermissionOption]


class RoleDetailResponse(RoleListItem):
    pass


class RoleCreateRequest(BaseModel):
    name: str
    description: str = ''
    permission_ids: list[int] = Field(default_factory=list)


class RoleUpdateRequest(BaseModel):
    name: str
    description: str = ''
    permission_ids: list[int] = Field(default_factory=list)
