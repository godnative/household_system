"""Schemas for village management."""

from datetime import datetime

from pydantic import BaseModel


class VillageBase(BaseModel):
    name: str
    code: str


class VillageCreate(VillageBase):
    pass


class VillageUpdate(BaseModel):
    name: str | None = None
    code: str | None = None


class VillageListItem(VillageBase):
    id: int
    created_at: datetime
    household_count: int = 0

    class Config:
        from_attributes = True


class VillageDetail(VillageBase):
    id: int
    created_at: datetime
    household_count: int = 0
    member_count: int = 0

    class Config:
        from_attributes = True
