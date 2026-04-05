from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base

class Village(Base):
    __tablename__ = 'villages'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(20), unique=True, nullable=False, index=True)
    establishment_date = Column(Date, nullable=False)
    village_priest = Column(String(50), nullable=False)
    address = Column(String(200), nullable=False)
    description = Column(Text)
    photo = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 关联关系
    users = relationship('User', back_populates='village')
    households = relationship('Household', back_populates='village', cascade='all, delete-orphan')

class Household(Base):
    __tablename__ = 'households'
    
    id = Column(Integer, primary_key=True, index=True)
    village_id = Column(Integer, ForeignKey('villages.id'), nullable=False)
    household_code = Column(String(20), nullable=False, index=True)
    address = Column(String(200))
    head_of_household = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 关联关系
    village = relationship('Village', back_populates='households')
    members = relationship('Member', back_populates='household', cascade='all, delete-orphan')

class Member(Base):
    __tablename__ = 'members'
    
    id = Column(Integer, primary_key=True, index=True)
    household_id = Column(Integer, ForeignKey('households.id'), nullable=False)
    name = Column(String(50), nullable=False)
    gender = Column(String(10))
    birth_date = Column(Date)
    id_number = Column(String(18), unique=True, index=True)
    relation_to_head = Column(String(20))
    status = Column(String(20))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 关联关系
    household = relationship('Household', back_populates='members')