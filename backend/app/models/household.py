"""Household and Member models for the parish management system."""

from datetime import date, datetime, timezone

from sqlalchemy import Date, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class Household(Base):
    """家庭模型"""
    __tablename__ = 'households'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    village_id: Mapped[int] = mapped_column(ForeignKey('villages.id'), nullable=False, index=True)
    plot_number: Mapped[int] = mapped_column(nullable=False)
    address: Mapped[str] = mapped_column(String(200), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20))
    head_of_household: Mapped[str | None] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    village: Mapped['Village'] = relationship(back_populates='households')  # type: ignore
    members: Mapped[list['Member']] = relationship(back_populates='household', cascade='all, delete-orphan')


class Member(Base):
    """成员模型"""
    __tablename__ = 'members'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    household_id: Mapped[int] = mapped_column(ForeignKey('households.id'), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    gender: Mapped[str] = mapped_column(String(10), nullable=False)
    birth_date: Mapped[date | None] = mapped_column(Date)
    baptismal_name: Mapped[str | None] = mapped_column(String(50))
    relation_to_head: Mapped[str | None] = mapped_column(String(20))
    education: Mapped[str | None] = mapped_column(String(50))
    move_in_date: Mapped[date | None] = mapped_column(Date)
    occupation: Mapped[str | None] = mapped_column(String(100))
    church_id: Mapped[str | None] = mapped_column(String(50))

    # 圣洗信息
    baptism_priest: Mapped[str | None] = mapped_column(String(50))
    baptism_godparent: Mapped[str | None] = mapped_column(String(50))
    baptism_date: Mapped[date | None] = mapped_column(Date)
    baptism_note: Mapped[str | None] = mapped_column(Text)

    # 初领圣体
    first_communion_date: Mapped[date | None] = mapped_column(Date)

    # 补礼
    supplementary_priest: Mapped[str | None] = mapped_column(String(50))
    supplementary_place: Mapped[str | None] = mapped_column(String(100))
    supplementary_date: Mapped[date | None] = mapped_column(Date)

    # 照片
    photo: Mapped[str | None] = mapped_column(String(255))

    # 坚振信息
    confirmation_date: Mapped[date | None] = mapped_column(Date)
    confirmation_priest: Mapped[str | None] = mapped_column(String(50))
    confirmation_godparent: Mapped[str | None] = mapped_column(String(50))
    confirmation_name: Mapped[str | None] = mapped_column(String(50))
    confirmation_age: Mapped[int | None]
    confirmation_place: Mapped[str | None] = mapped_column(String(100))

    # 婚配信息
    marriage_date: Mapped[date | None] = mapped_column(Date)
    marriage_priest: Mapped[str | None] = mapped_column(String(50))
    marriage_witness: Mapped[str | None] = mapped_column(String(100))
    marriage_dispensation_item: Mapped[str | None] = mapped_column(String(100))
    marriage_dispensation_priest: Mapped[str | None] = mapped_column(String(50))
    marriage_place: Mapped[str | None] = mapped_column(String(100))

    # 病人傅油
    anointing_date: Mapped[date | None] = mapped_column(Date)
    anointing_priest: Mapped[str | None] = mapped_column(String(50))
    anointing_place: Mapped[str | None] = mapped_column(String(100))

    # 死亡信息
    death_date: Mapped[date | None] = mapped_column(Date)
    death_age: Mapped[int | None]

    # 所属善会
    association: Mapped[str | None] = mapped_column(String(100))

    # 备注
    note: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    household: Mapped['Household'] = relationship(back_populates='members')  # type: ignore
