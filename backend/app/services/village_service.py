"""Village management service."""

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.auth import Village
from app.models.household import Household, Member
from app.schemas.pagination import calculate_offset, calculate_total_pages
from app.schemas.village import VillageCreate, VillageListItem, VillageUpdate


def get_village_or_404(db: Session, village_id: int) -> Village:
    """Get village by ID or raise 404."""
    village = db.query(Village).filter(Village.id == village_id).first()
    if not village:
        from fastapi import HTTPException, status

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='堂区不存在')
    return village


def list_villages(
    db: Session,
    user_village_ids: list[int] | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[VillageListItem], int]:
    """List all villages with household count.

    If user_village_ids is provided, filter to only those villages.
    Returns tuple of (items, total_count).
    """
    query = db.query(Village)

    if user_village_ids is not None:
        query = query.filter(Village.id.in_(user_village_ids))

    # Get total count before pagination
    total = query.count()

    # Apply pagination
    offset = calculate_offset(page, page_size)
    villages = query.order_by(Village.id).offset(offset).limit(page_size).all()

    # Get household counts
    household_counts = dict(
        db.query(Household.village_id, func.count(Household.id))
        .group_by(Household.village_id)
        .all()
    )

    result = []
    for v in villages:
        result.append(
            VillageListItem(
                id=v.id,
                name=v.name,
                code=v.code,
                created_at=v.created_at,
                household_count=household_counts.get(v.id, 0),
            )
        )
    return result, total


def get_village_detail(db: Session, village_id: int) -> dict:
    """Get village detail with household and member counts."""
    village = get_village_or_404(db, village_id)

    household_count = db.query(func.count(Household.id)).filter(Household.village_id == village_id).scalar()

    # Get member count through households
    member_count = (
        db.query(func.count(Member.id))
        .join(Household)
        .filter(Household.village_id == village_id)
        .scalar()
    )

    return {
        'id': village.id,
        'name': village.name,
        'code': village.code,
        'created_at': village.created_at,
        'household_count': household_count or 0,
        'member_count': member_count or 0,
    }


def create_village(db: Session, data: VillageCreate) -> Village:
    """Create a new village."""
    # Check for duplicate name or code
    existing = db.query(Village).filter((Village.name == data.name) | (Village.code == data.code)).first()
    if existing:
        if existing.name == data.name:
            from fastapi import HTTPException, status

            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='堂区名称已存在')
        else:
            from fastapi import HTTPException, status

            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='堂区编码已存在')

    village = Village(name=data.name, code=data.code)
    db.add(village)
    db.commit()
    db.refresh(village)
    return village


def update_village(db: Session, village: Village, data: VillageUpdate) -> Village:
    """Update a village."""
    if data.name is not None and data.name != village.name:
        existing = db.query(Village).filter(Village.name == data.name, Village.id != village.id).first()
        if existing:
            from fastapi import HTTPException, status

            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='堂区名称已存在')
        village.name = data.name

    if data.code is not None and data.code != village.code:
        existing = db.query(Village).filter(Village.code == data.code, Village.id != village.id).first()
        if existing:
            from fastapi import HTTPException, status

            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='堂区编码已存在')
        village.code = data.code

    db.commit()
    db.refresh(village)
    return village


def delete_village(db: Session, village: Village) -> None:
    """Delete a village. Will fail if there are households."""
    household_count = db.query(func.count(Household.id)).filter(Household.village_id == village.id).scalar()
    if household_count and household_count > 0:
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='该堂区下存在家庭，无法删除',
        )
    db.delete(village)
    db.commit()
