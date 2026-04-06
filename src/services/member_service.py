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
    def create_member(db: Session, household_id: int, name: str, gender: str, 
                     birth_date: str = None, baptismal_name: str = None, 
                     relation_to_head: str = None, education: str = None, 
                     move_in_date: str = None, occupation: str = None, 
                     church_id: str = None, baptism_priest: str = None, 
                     baptism_godparent: str = None, baptism_date: str = None, 
                     baptism_note: str = None, first_communion_date: str = None, 
                     supplementary_priest: str = None, supplementary_place: str = None, 
                     supplementary_date: str = None, photo: str = None, 
                     confirmation_date: str = None, confirmation_priest: str = None, 
                     confirmation_godparent: str = None, confirmation_name: str = None, 
                     confirmation_age: int = None, confirmation_place: str = None, 
                     marriage_date: str = None, marriage_priest: str = None, 
                     marriage_witness: str = None, marriage_dispensation_item: str = None, 
                     marriage_dispensation_priest: str = None, marriage_place: str = None, 
                     anointing_date: str = None, anointing_priest: str = None, 
                     anointing_place: str = None, death_date: str = None, 
                     death_age: int = None, association: str = None, note: str = None) -> Member:
        """创建新成员"""
        member = Member(
            household_id=household_id,
            name=name,
            gender=gender,
            birth_date=birth_date,
            baptismal_name=baptismal_name,
            relation_to_head=relation_to_head,
            education=education,
            move_in_date=move_in_date,
            occupation=occupation,
            church_id=church_id,
            baptism_priest=baptism_priest,
            baptism_godparent=baptism_godparent,
            baptism_date=baptism_date,
            baptism_note=baptism_note,
            first_communion_date=first_communion_date,
            supplementary_priest=supplementary_priest,
            supplementary_place=supplementary_place,
            supplementary_date=supplementary_date,
            photo=photo,
            confirmation_date=confirmation_date,
            confirmation_priest=confirmation_priest,
            confirmation_godparent=confirmation_godparent,
            confirmation_name=confirmation_name,
            confirmation_age=confirmation_age,
            confirmation_place=confirmation_place,
            marriage_date=marriage_date,
            marriage_priest=marriage_priest,
            marriage_witness=marriage_witness,
            marriage_dispensation_item=marriage_dispensation_item,
            marriage_dispensation_priest=marriage_dispensation_priest,
            marriage_place=marriage_place,
            anointing_date=anointing_date,
            anointing_priest=anointing_priest,
            anointing_place=anointing_place,
            death_date=death_date,
            death_age=death_age,
            association=association,
            note=note
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