from fastapi import APIRouter, Depends, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import get_current_user, require_permission
from app.models.auth import User
from app.schemas.household import HouseholdCreate, HouseholdListItem, HouseholdUpdate, HouseholdWithMembers
from app.schemas.pagination import PaginatedMeta, PaginatedResponse
from app.services.household_service import (
    create_household,
    delete_household,
    get_household_detail,
    get_household_or_404,
    list_households,
    render_household_print_html,
    update_household,
)

router = APIRouter(prefix='/api/v1/households', tags=['households'])


def get_user_village_ids(user: User) -> list[int] | None:
    """Get user's accessible village IDs. None means all villages."""
    if user.role.name == 'super_admin':
        return None
    if user.village_id:
        return [user.village_id]
    if user.accessible_villages:
        return [v.id for v in user.accessible_villages]
    return []


@router.get('', response_model=PaginatedResponse)
def get_households(
    village_id: int | None = Query(None),
    search: str | None = Query(None),
    page: int = Query(1, ge=1, description='页码'),
    page_size: int = Query(20, ge=1, le=100, description='每页数量'),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PaginatedResponse:
    """List households with optional filters."""
    user_village_ids = get_user_village_ids(current_user)

    if user_village_ids is not None and len(user_village_ids) == 0:
        return PaginatedResponse(
            items=[],
            meta=PaginatedMeta(total=0, page=page, page_size=page_size, total_pages=1),
        )

    items, total = list_households(db, village_id, user_village_ids, search, page, page_size)
    total_pages = (total + page_size - 1) // page_size if total > 0 else 1

    return PaginatedResponse(
        items=items,
        meta=PaginatedMeta(
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        ),
    )


@router.get('/{household_id}', response_model=HouseholdWithMembers)
def get_household(
    household_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> HouseholdWithMembers:
    """Get household detail with members."""
    household = get_household_or_404(db, household_id)
    user_village_ids = get_user_village_ids(current_user)
    if user_village_ids is not None and household.village_id not in user_village_ids:
        from fastapi import HTTPException, status

        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='无权访问该家庭')

    return get_household_detail(db, household_id)


@router.get('/{household_id}/print', response_class=HTMLResponse)
def print_household(
    household_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> HTMLResponse:
    household = get_household_or_404(db, household_id)
    user_village_ids = get_user_village_ids(current_user)
    if user_village_ids is not None and household.village_id not in user_village_ids:
        from fastapi import HTTPException, status

        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='无权访问该家庭')
    return HTMLResponse(render_household_print_html(db, household_id))


@router.post('', response_model=HouseholdListItem)
def post_household(
    data: HouseholdCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission('household_manage')),
) -> HouseholdListItem:
    """Create a new household."""
    household = create_household(db, data)
    return HouseholdListItem(
        id=household.id,
        village_id=household.village_id,
        village_name=household.village.name,
        plot_number=household.plot_number,
        address=household.address,
        phone=household.phone,
        head_of_household=household.head_of_household,
        member_count=0,
        created_at=household.created_at,
    )


@router.put('/{household_id}', response_model=HouseholdListItem)
def put_household(
    household_id: int,
    data: HouseholdUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission('household_manage')),
) -> HouseholdListItem:
    """Update a household."""
    household = get_household_or_404(db, household_id)
    household = update_household(db, household, data)
    result, _ = list_households(db, None, None, None)
    for h in result:
        if h.id == household_id:
            return h
    return HouseholdListItem(
        id=household.id,
        village_id=household.village_id,
        village_name=household.village.name,
        plot_number=household.plot_number,
        address=household.address,
        phone=household.phone,
        head_of_household=household.head_of_household,
        member_count=0,
        created_at=household.created_at,
    )


@router.delete('/{household_id}')
def delete_household_endpoint(
    household_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission('household_manage')),
) -> dict:
    """Delete a household."""
    household = get_household_or_404(db, household_id)
    delete_household(db, household)
    return {'message': '家庭已删除'}
