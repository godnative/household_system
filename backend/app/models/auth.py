from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


role_permissions = Table(
    'role_permissions',
    Base.metadata,
    Column('role_id', ForeignKey('roles.id'), primary_key=True),
    Column('permission_id', ForeignKey('permissions.id'), primary_key=True),
)


user_village_access = Table(
    'user_village_access',
    Base.metadata,
    Column('user_id', ForeignKey('users.id'), primary_key=True),
    Column('village_id', ForeignKey('villages.id'), primary_key=True),
)


class Village(Base):
    __tablename__ = 'villages'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    users: Mapped[list['User']] = relationship(back_populates='village', foreign_keys='User.village_id')
    accessible_users: Mapped[list['User']] = relationship(
        secondary=user_village_access,
        back_populates='accessible_villages',
    )
    households: Mapped[list['Household']] = relationship(back_populates='village', cascade='all, delete-orphan')  # type: ignore


class Role(Base):
    __tablename__ = 'roles'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(255), default='')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    permissions: Mapped[list['Permission']] = relationship(
        secondary=role_permissions,
        back_populates='roles',
        lazy='selectin',
    )
    users: Mapped[list['User']] = relationship(back_populates='role')


class Permission(Base):
    __tablename__ = 'permissions'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(255), default='')

    roles: Mapped[list[Role]] = relationship(
        secondary=role_permissions,
        back_populates='permissions',
        lazy='selectin',
    )


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role_id: Mapped[int] = mapped_column(ForeignKey('roles.id'), nullable=False)
    village_id: Mapped[int | None] = mapped_column(ForeignKey('villages.id'), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    role: Mapped[Role] = relationship(back_populates='users', lazy='joined')
    village: Mapped[Village | None] = relationship(back_populates='users', foreign_keys=[village_id], lazy='joined')
    accessible_villages: Mapped[list[Village]] = relationship(
        secondary=user_village_access,
        back_populates='accessible_users',
        lazy='selectin',
    )
