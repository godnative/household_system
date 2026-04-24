"""Schemas for household management."""

from datetime import date, datetime

from pydantic import BaseModel


class HouseholdBase(BaseModel):
    village_id: int
    plot_number: int
    address: str
    phone: str | None = None
    head_of_household: str | None = None


class HouseholdCreate(HouseholdBase):
    pass


class HouseholdUpdate(BaseModel):
    village_id: int | None = None
    plot_number: int | None = None
    address: str | None = None
    phone: str | None = None
    head_of_household: str | None = None


class HouseholdListItem(BaseModel):
    id: int
    village_id: int
    village_name: str
    plot_number: int
    address: str
    phone: str | None
    head_of_household: str | None
    member_count: int = 0
    created_at: datetime

    class Config:
        from_attributes = True


class HouseholdDetail(HouseholdListItem):
    updated_at: datetime


class MemberSummary(BaseModel):
    id: int
    name: str
    gender: str
    birth_date: date | None
    relation_to_head: str | None
    baptismal_name: str | None

    class Config:
        from_attributes = True


class HouseholdWithMembers(HouseholdDetail):
    members: list[MemberSummary] = []
