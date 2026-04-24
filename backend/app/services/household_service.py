"""Household management service."""

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.models.household import Household, Member
from app.models.auth import Village
from app.schemas.household import HouseholdCreate, HouseholdListItem, HouseholdUpdate, HouseholdWithMembers
from app.schemas.pagination import calculate_offset
from app.services.member_service import render_member_print_html


def _value(value: object | None) -> str:
    if value in {None, '', '1752-09-14'}:
        return '无'
    return str(value)


def render_household_print_html(db: Session, household_id: int) -> str:
    household = (
        db.query(Household)
        .options(joinedload(Household.village), joinedload(Household.members))
        .filter(Household.id == household_id)
        .first()
    )
    if not household:
        from fastapi import HTTPException, status

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='家庭不存在')

    household_html = f"""
    <div class=\"print-household\">
      <h3>家庭信息</h3>
      <table border=\"1\" cellspacing=\"0\" cellpadding=\"8\" style=\"border-collapse:collapse; width:100%;\">
        <tr>
          <td width=\"25%\">所属堂区</td>
          <td width=\"25%\">{_value(household.village.name if household.village else '')}</td>
          <td width=\"25%\">家庭户号</td>
          <td width=\"25%\">{household.id}</td>
        </tr>
        <tr>
          <td>片号</td>
          <td>{_value(household.plot_number)}</td>
          <td>家庭住址</td>
          <td>{_value(household.address)}</td>
        </tr>
        <tr>
          <td>户主姓名</td>
          <td>{_value(household.head_of_household)}</td>
          <td>电话</td>
          <td>{_value(household.phone)}</td>
        </tr>
      </table>
    </div>
    """

    member_sections = []
    for member in household.members:
        member_sections.append(f'<div style="page-break-before: always; margin-top: 24px;">{render_member_print_html(member)}</div>')

    return f"{household_html}{''.join(member_sections)}"


def get_household_or_404(db: Session, household_id: int) -> Household:
    """Get household by ID or raise 404."""
    household = db.query(Household).filter(Household.id == household_id).first()
    if not household:
        from fastapi import HTTPException, status

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='家庭不存在')
    return household


def list_households(
    db: Session,
    village_id: int | None = None,
    user_village_ids: list[int] | None = None,
    search: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[HouseholdListItem], int]:
    """List households with optional filters.

    Returns tuple of (items, total_count).
    """
    query = db.query(Household).options(joinedload(Household.village))

    if village_id:
        query = query.filter(Household.village_id == village_id)
    elif user_village_ids is not None:
        query = query.filter(Household.village_id.in_(user_village_ids))

    if search:
        query = query.filter(
            (Household.address.contains(search)) | (Household.head_of_household.contains(search))
        )

    total = query.count()
    offset = calculate_offset(page, page_size)
    households = query.order_by(Household.id.desc()).offset(offset).limit(page_size).all()

    household_ids = [h.id for h in households]
    member_counts = {}
    if household_ids:
        member_counts = dict(
            db.query(Member.household_id, func.count(Member.id))
            .filter(Member.household_id.in_(household_ids))
            .group_by(Member.household_id)
            .all()
        )

    result = []
    for h in households:
        result.append(
            HouseholdListItem(
                id=h.id,
                village_id=h.village_id,
                village_name=h.village.name,
                plot_number=h.plot_number,
                address=h.address,
                phone=h.phone,
                head_of_household=h.head_of_household,
                member_count=member_counts.get(h.id, 0),
                created_at=h.created_at,
            )
        )
    return result, total


def get_household_detail(db: Session, household_id: int) -> HouseholdWithMembers:
    """Get household detail with members."""
    household = (
        db.query(Household)
        .options(joinedload(Household.village), joinedload(Household.members))
        .filter(Household.id == household_id)
        .first()
    )
    if not household:
        from fastapi import HTTPException, status

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='家庭不存在')

    members = [
        {
            'id': m.id,
            'name': m.name,
            'gender': m.gender,
            'birth_date': m.birth_date,
            'relation_to_head': m.relation_to_head,
            'baptismal_name': m.baptismal_name,
        }
        for m in household.members
    ]

    return HouseholdWithMembers(
        id=household.id,
        village_id=household.village_id,
        village_name=household.village.name,
        plot_number=household.plot_number,
        address=household.address,
        phone=household.phone,
        head_of_household=household.head_of_household,
        member_count=len(household.members),
        created_at=household.created_at,
        updated_at=household.updated_at,
        members=members,
    )


def create_household(db: Session, data: HouseholdCreate) -> Household:
    """Create a new household."""
    village = db.query(Village).filter(Village.id == data.village_id).first()
    if not village:
        from fastapi import HTTPException, status

        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='堂区不存在')

    household = Household(
        village_id=data.village_id,
        plot_number=data.plot_number,
        address=data.address,
        phone=data.phone,
        head_of_household=data.head_of_household,
    )
    db.add(household)
    db.commit()
    db.refresh(household)
    return household


def update_household(db: Session, household: Household, data: HouseholdUpdate) -> Household:
    """Update a household."""
    if data.village_id is not None and data.village_id != household.village_id:
        village = db.query(Village).filter(Village.id == data.village_id).first()
        if not village:
            from fastapi import HTTPException, status

            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='堂区不存在')
        household.village_id = data.village_id

    if data.plot_number is not None:
        household.plot_number = data.plot_number
    if data.address is not None:
        household.address = data.address
    if data.phone is not None:
        household.phone = data.phone
    if data.head_of_household is not None:
        household.head_of_household = data.head_of_household

    db.commit()
    db.refresh(household)
    return household


def delete_household(db: Session, household: Household) -> None:
    """Delete a household. Members will be cascade deleted."""
    db.delete(household)
    db.commit()
