from sqlalchemy.orm import Session
from sqlalchemy import and_
from src.models import Member, Household

class MemberService:
    @staticmethod
    def get_all_members(db: Session, household_id: int = None, village_id: int = None):
        """获取所有成员，可按家庭或村过滤"""
        query = db.query(Member)
        
        if household_id:
            query = query.filter(Member.household_id == household_id)
        elif village_id:
            # 通过家庭关联到村
            query = query.join(Household).filter(Household.village_id == village_id)
        
        return query.all()
    
    @staticmethod
    def get_member_by_id(db: Session, member_id: int) -> Member:
        """根据ID获取成员"""
        return db.query(Member).filter(Member.id == member_id).first()
    
    @staticmethod
    def get_member_by_id_number(db: Session, id_number: str) -> Member:
        """根据身份证号获取成员"""
        return db.query(Member).filter(Member.id_number == id_number).first()
    
    @staticmethod
    def search_members(db: Session, keyword: str = None, household_id: int = None, village_id: int = None):
        """搜索成员"""
        query = db.query(Member)
        
        if household_id:
            query = query.filter(Member.household_id == household_id)
        elif village_id:
            query = query.join(Household).filter(Household.village_id == village_id)
        
        if keyword:
            query = query.filter(
                Member.name.ilike(f'%{keyword}%') |
                Member.id_number.ilike(f'%{keyword}%') |
                Member.relation_to_head.ilike(f'%{keyword}%')
            )
        
        return query.all()
    
    @staticmethod
    def create_member(db: Session, household_id: int, name: str, gender: str = None, 
                     birth_date: str = None, id_number: str = None, 
                     relation_to_head: str = None, status: str = None) -> Member:
        """创建新成员"""
        member = Member(
            household_id=household_id,
            name=name,
            gender=gender,
            birth_date=birth_date,
            id_number=id_number,
            relation_to_head=relation_to_head,
            status=status
        )
        db.add(member)
        db.commit()
        db.refresh(member)
        return member
    
    @staticmethod
    def update_member(db: Session, member_id: int, **kwargs) -> Member:
        """更新成员信息"""
        member = db.query(Member).filter(Member.id == member_id).first()
        if not member:
            return None
        
        for key, value in kwargs.items():
            setattr(member, key, value)
        
        db.commit()
        db.refresh(member)
        return member
    
    @staticmethod
    def delete_member(db: Session, member_id: int) -> bool:
        """删除成员"""
        member = db.query(Member).filter(Member.id == member_id).first()
        if not member:
            return False
        
        db.delete(member)
        db.commit()
        return True