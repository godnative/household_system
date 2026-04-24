"""Search service for households and members."""

from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from app.models.auth import User
from app.models.household import Household, Member


def get_user_village_ids(user: User) -> list[int] | None:
    """Get user's accessible village IDs. None means all villages."""
    if user.role.name == 'super_admin':
        return None
    if user.village_id:
        return [user.village_id]
    if user.accessible_villages:
        return [v.id for v in user.accessible_villages]
    return []


def search_households(
    db: Session,
    keyword: str,
    user: User,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[dict], int]:
    """Search households by keyword across multiple fields.

    Args:
        db: Database session
        keyword: Search keyword
        user: Current user for permission filtering
        page: Page number
        page_size: Items per page

    Returns:
        Tuple of (household list, total count)
    """
    if not keyword or not keyword.strip():
        return [], 0

    user_village_ids = get_user_village_ids(user)

    query = db.query(Household).options(joinedload(Household.village))

    # Permission filter
    if user_village_ids is not None:
        query = query.filter(Household.village_id.in_(user_village_ids))

    # Keyword filter (multiple fields OR match)
    search_pattern = f'%{keyword.strip()}%'
    query = query.filter(
        or_(
            Household.head_of_household.ilike(search_pattern),
            Household.address.ilike(search_pattern),
            Household.phone.ilike(search_pattern),
        )
    )

    # Get total count
    total = query.count()

    # Pagination
    offset = (page - 1) * page_size
    households = query.order_by(Household.id.desc()).offset(offset).limit(page_size).all()

    # Build result
    from sqlalchemy import func

    # Get member counts
    household_ids = [h.id for h in households]
    member_counts = {}
    if household_ids:
        member_counts = dict(
            db.query(Member.household_id, func.count(Member.id))
            .filter(Member.household_id.in_(household_ids))
            .group_by(Member.household_id)
            .all()
        )

    result = [
        {
            'id': h.id,
            'village_id': h.village_id,
            'village_name': h.village.name if h.village else '未知',
            'plot_number': h.plot_number,
            'address': h.address,
            'phone': h.phone,
            'head_of_household': h.head_of_household,
            'member_count': member_counts.get(h.id, 0),
            'created_at': h.created_at,
        }
        for h in households
    ]

    return result, total


def search_members(
    db: Session,
    keyword: str,
    user: User,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[dict], int]:
    """Search members by keyword across 20+ fields.

    Returns unique households containing matching members.

    Args:
        db: Database session
        keyword: Search keyword
        user: Current user for permission filtering
        page: Page number
        page_size: Items per page

    Returns:
        Tuple of (member list, total count)
    """
    if not keyword or not keyword.strip():
        return [], 0

    user_village_ids = get_user_village_ids(user)

    query = db.query(Member).options(
        joinedload(Member.household).joinedload(Household.village)
    )

    # Permission filter through household
    if user_village_ids is not None:
        query = query.join(Household).filter(Household.village_id.in_(user_village_ids))

    # Keyword filter (20+ fields OR match)
    search_pattern = f'%{keyword.strip()}%'
    query = query.filter(
        or_(
            # Basic info
            Member.name.ilike(search_pattern),
            Member.baptismal_name.ilike(search_pattern),
            Member.church_id.ilike(search_pattern),
            Member.occupation.ilike(search_pattern),
            Member.association.ilike(search_pattern),
            # Notes
            Member.note.ilike(search_pattern),
            Member.baptism_note.ilike(search_pattern),
            # Baptism
            Member.baptism_priest.ilike(search_pattern),
            Member.baptism_godparent.ilike(search_pattern),
            # Supplementary
            Member.supplementary_priest.ilike(search_pattern),
            Member.supplementary_place.ilike(search_pattern),
            # Confirmation
            Member.confirmation_priest.ilike(search_pattern),
            Member.confirmation_godparent.ilike(search_pattern),
            Member.confirmation_name.ilike(search_pattern),
            Member.confirmation_place.ilike(search_pattern),
            # Marriage
            Member.marriage_priest.ilike(search_pattern),
            Member.marriage_witness.ilike(search_pattern),
            Member.marriage_place.ilike(search_pattern),
            Member.marriage_dispensation_item.ilike(search_pattern),
            Member.marriage_dispensation_priest.ilike(search_pattern),
            # Anointing
            Member.anointing_priest.ilike(search_pattern),
            Member.anointing_place.ilike(search_pattern),
        )
    )

    # Get total count
    total = query.count()

    # Pagination
    offset = (page - 1) * page_size
    members = query.order_by(Member.id.desc()).offset(offset).limit(page_size).all()

    result = [
        {
            'id': m.id,
            'household_id': m.household_id,
            'household_address': m.household.address if m.household else '未知',
            'village_name': m.household.village.name if m.household and m.household.village else '未知',
            'name': m.name,
            'gender': m.gender,
            'birth_date': m.birth_date,
            'baptismal_name': m.baptismal_name,
            'relation_to_head': m.relation_to_head,
            'photo': m.photo,
            'created_at': m.created_at,
        }
        for m in members
    ]

    return result, total
