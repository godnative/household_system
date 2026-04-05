from sqlalchemy.orm import Session
from src.models import Village

class VillageService:
    @staticmethod
    def get_all_villages(db: Session):
        """获取所有村"""
        return db.query(Village).all()
    
    @staticmethod
    def get_village_by_id(db: Session, village_id: int) -> Village:
        """根据ID获取村"""
        return db.query(Village).filter(Village.id == village_id).first()
    
    @staticmethod
    def get_village_by_code(db: Session, code: str) -> Village:
        """根据代码获取村"""
        return db.query(Village).filter(Village.code == code).first()
    
    @staticmethod
    def search_villages(db: Session, keyword: str = None):
        """搜索村"""
        query = db.query(Village)
        if keyword:
            query = query.filter(Village.name.ilike(f'%{keyword}%') | Village.code.ilike(f'%{keyword}%'))
        return query.all()
    
    @staticmethod
    def create_village(db: Session, name: str, code: str, establishment_date, village_priest: str, address: str, description: str = None, photo: str = None) -> Village:
        """创建新村"""
        village = Village(
            name=name, 
            code=code, 
            establishment_date=establishment_date, 
            village_priest=village_priest, 
            address=address, 
            description=description, 
            photo=photo
        )
        db.add(village)
        db.commit()
        db.refresh(village)
        return village
    
    @staticmethod
    def update_village(db: Session, village_id: int, **kwargs) -> Village:
        """更新村信息"""
        village = db.query(Village).filter(Village.id == village_id).first()
        if not village:
            return None
        
        for key, value in kwargs.items():
            setattr(village, key, value)
        
        db.commit()
        db.refresh(village)
        return village
    
    @staticmethod
    def delete_village(db: Session, village_id: int) -> bool:
        """删除村"""
        village = db.query(Village).filter(Village.id == village_id).first()
        if not village:
            return False
        
        # 检查是否有家庭
        if village.households:
            return False
        
        db.delete(village)
        db.commit()
        return True