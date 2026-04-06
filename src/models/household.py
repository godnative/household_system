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
    plot_number = Column(Integer, nullable=False)
    address = Column(String(200), nullable=False)
    phone = Column(String(20))
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
    gender = Column(String(10), nullable=False)
    birth_date = Column(Date)
    baptismal_name = Column(String(50))
    relation_to_head = Column(String(20))
    education = Column(String(50))
    move_in_date = Column(Date)
    occupation = Column(String(100))
    church_id = Column(String(50))
    # 圣洗相关信息
    baptism_priest = Column(String(50))
    baptism_godparent = Column(String(50))
    baptism_date = Column(Date)
    baptism_note = Column(Text)
    # 初领圣体时间
    first_communion_date = Column(Date)
    # 补礼相关信息
    supplementary_priest = Column(String(50))
    supplementary_place = Column(String(100))
    supplementary_date = Column(Date)
    # 照片
    photo = Column(String(255))
    # 坚振相关信息
    confirmation_date = Column(Date)
    confirmation_priest = Column(String(50))
    confirmation_godparent = Column(String(50))
    confirmation_name = Column(String(50))
    confirmation_age = Column(Integer)
    confirmation_place = Column(String(100))
    # 婚配相关信息
    marriage_date = Column(Date)
    marriage_priest = Column(String(50))
    marriage_witness = Column(String(100))
    marriage_dispensation_item = Column(String(100))
    marriage_dispensation_priest = Column(String(50))
    marriage_place = Column(String(100))
    # 病人傅油相关信息
    anointing_date = Column(Date)
    anointing_priest = Column(String(50))
    anointing_place = Column(String(100))
    death_date = Column(Date)
    death_age = Column(Integer)
    # 所属善会
    association = Column(String(100))
    # 备注
    note = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 关联关系
    household = relationship('Household', back_populates='members')