from sqlalchemy.orm import Session
from src.models import Household, Village

class HouseholdService:
    @staticmethod
    def get_all_households(db: Session, village_id: int = None):
        """获取所有家庭，可按村过滤"""
        query = db.query(Household)
        if village_id:
            query = query.filter(Household.village_id == village_id)
        return query.all()
    
    @staticmethod
    def get_household_by_id(db: Session, household_id: int) -> Household:
        """根据ID获取家庭"""
        return db.query(Household).filter(Household.id == household_id).first()
    
    @staticmethod
    def search_households(db: Session, keyword: str = None, village_id: int = None):
        """搜索家庭"""
        query = db.query(Household)
        
        if village_id:
            query = query.filter(Household.village_id == village_id)
        
        if keyword:
            query = query.filter(
                Household.household_code.ilike(f'%{keyword}%') |
                Household.head_of_household.ilike(f'%{keyword}%') |
                Household.address.ilike(f'%{keyword}%')
            )
        
        return query.all()
    
    @staticmethod
    def create_household(db: Session, village_id: int, household_code: str, 
                        address: str = None, head_of_household: str = None) -> Household:
        """创建新家庭"""
        household = Household(
            village_id=village_id,
            household_code=household_code,
            address=address,
            head_of_household=head_of_household
        )
        db.add(household)
        db.commit()
        db.refresh(household)
        return household
    
    @staticmethod
    def update_household(db: Session, household_id: int, **kwargs) -> Household:
        """更新家庭信息"""
        household = db.query(Household).filter(Household.id == household_id).first()
        if not household:
            return None
        
        for key, value in kwargs.items():
            setattr(household, key, value)
        
        db.commit()
        db.refresh(household)
        return household
    
    @staticmethod
    def delete_household(db: Session, household_id: int) -> bool:
        """删除家庭"""
        household = db.query(Household).filter(Household.id == household_id).first()
        if not household:
            return False
        
        db.delete(household)
        db.commit()
        return True