"""Schemas for member management."""

from datetime import date, datetime

from pydantic import BaseModel


class MemberBase(BaseModel):
    name: str
    gender: str
    birth_date: date | None = None
    baptismal_name: str | None = None
    relation_to_head: str | None = None
    education: str | None = None
    move_in_date: date | None = None
    occupation: str | None = None
    church_id: str | None = None
    # 圣洗
    baptism_priest: str | None = None
    baptism_godparent: str | None = None
    baptism_date: date | None = None
    baptism_note: str | None = None
    # 初领圣体
    first_communion_date: date | None = None
    # 补礼
    supplementary_priest: str | None = None
    supplementary_place: str | None = None
    supplementary_date: date | None = None
    # 照片
    photo: str | None = None
    # 坚振
    confirmation_date: date | None = None
    confirmation_priest: str | None = None
    confirmation_godparent: str | None = None
    confirmation_name: str | None = None
    confirmation_age: int | None = None
    confirmation_place: str | None = None
    # 婚配
    marriage_date: date | None = None
    marriage_priest: str | None = None
    marriage_witness: str | None = None
    marriage_dispensation_item: str | None = None
    marriage_dispensation_priest: str | None = None
    marriage_place: str | None = None
    # 病人傅油
    anointing_date: date | None = None
    anointing_priest: str | None = None
    anointing_place: str | None = None
    # 死亡
    death_date: date | None = None
    death_age: int | None = None
    # 善会
    association: str | None = None
    # 备注
    note: str | None = None


class MemberCreate(MemberBase):
    household_id: int


class MemberUpdate(BaseModel):
    name: str | None = None
    gender: str | None = None
    birth_date: date | None = None
    baptismal_name: str | None = None
    relation_to_head: str | None = None
    education: str | None = None
    move_in_date: date | None = None
    occupation: str | None = None
    church_id: str | None = None
    baptism_priest: str | None = None
    baptism_godparent: str | None = None
    baptism_date: date | None = None
    baptism_note: str | None = None
    first_communion_date: date | None = None
    supplementary_priest: str | None = None
    supplementary_place: str | None = None
    supplementary_date: date | None = None
    photo: str | None = None
    confirmation_date: date | None = None
    confirmation_priest: str | None = None
    confirmation_godparent: str | None = None
    confirmation_name: str | None = None
    confirmation_age: int | None = None
    confirmation_place: str | None = None
    marriage_date: date | None = None
    marriage_priest: str | None = None
    marriage_witness: str | None = None
    marriage_dispensation_item: str | None = None
    marriage_dispensation_priest: str | None = None
    marriage_place: str | None = None
    anointing_date: date | None = None
    anointing_priest: str | None = None
    anointing_place: str | None = None
    death_date: date | None = None
    death_age: int | None = None
    association: str | None = None
    note: str | None = None


class MemberListItem(BaseModel):
    id: int
    household_id: int
    name: str
    gender: str
    birth_date: date | None
    baptismal_name: str | None
    relation_to_head: str | None
    photo: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class MemberDetail(MemberBase):
    id: int
    household_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
