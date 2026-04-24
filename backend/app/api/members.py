"""Member management API endpoints."""

from fastapi import APIRouter, Depends, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import get_current_user, require_permission
from app.models.auth import User
from app.models.household import Household
from app.schemas.member import MemberCreate, MemberDetail, MemberListItem, MemberUpdate
from app.schemas.pagination import PaginatedMeta, PaginatedResponse
from app.services.member_service import (
    create_member,
    delete_member,
    get_member_detail,
    get_member_or_404,
    list_members,
    render_member_print_html,
    set_as_household_head,
    update_member,
)

router = APIRouter(prefix='/api/v1/members', tags=['members'])


def get_user_village_ids(user: User) -> list[int] | None:
    """Get user's accessible village IDs. None means all villages."""
    if user.role.name == 'super_admin':
        return None
    if user.village_id:
        return [user.village_id]
    if user.accessible_villages:
        return [v.id for v in user.accessible_villages]
    return []


def check_household_access(db: Session, household_id: int, user: User) -> Household:
    """Check if user has access to the household."""
    household = db.query(Household).filter(Household.id == household_id).first()
    if not household:
        from fastapi import HTTPException, status

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='家庭不存在')

    user_village_ids = get_user_village_ids(user)
    if user_village_ids is not None and household.village_id not in user_village_ids:
        from fastapi import HTTPException, status

        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='无权访问该家庭')

    return household


@router.get('', response_model=PaginatedResponse)
def get_members(
    household_id: int | None = Query(None),
    search: str | None = Query(None),
    page: int = Query(1, ge=1, description='页码'),
    page_size: int = Query(20, ge=1, le=100, description='每页数量'),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PaginatedResponse:
    """List members with optional filters."""
    user_village_ids = get_user_village_ids(current_user)

    if user_village_ids is not None and len(user_village_ids) == 0:
        return PaginatedResponse(
            items=[],
            meta=PaginatedMeta(total=0, page=page, page_size=page_size, total_pages=1),
        )

    items, total = list_members(db, household_id, user_village_ids, search, page, page_size)
    total_pages = (total + page_size - 1) // page_size if total > 0 else 1

    return PaginatedResponse(
        items=[MemberListItem(**m) for m in items],
        meta=PaginatedMeta(
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        ),
    )


@router.get('/{member_id}', response_model=MemberDetail)
def get_member(
    member_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MemberDetail:
    """Get member detail."""
    member = get_member_or_404(db, member_id)
    check_household_access(db, member.household_id, current_user)
    return get_member_detail(db, member_id)


@router.get('/{member_id}/print', response_class=HTMLResponse)
def print_member(
    member_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> HTMLResponse:
    member = get_member_or_404(db, member_id)
    check_household_access(db, member.household_id, current_user)
    return HTMLResponse(render_member_print_html(get_member_detail(db, member_id)))


@router.post('', response_model=MemberDetail)
def post_member(
    data: MemberCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission('member_manage')),
) -> MemberDetail:
    """Create a new member."""
    check_household_access(db, data.household_id, current_user)
    member = create_member(db, data)
    return get_member_detail(db, member.id)


@router.put('/{member_id}', response_model=MemberDetail)
def put_member(
    member_id: int,
    data: MemberUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission('member_manage')),
) -> MemberDetail:
    """Update a member."""
    member = get_member_or_404(db, member_id)
    check_household_access(db, member.household_id, current_user)
    member = update_member(db, member, data)
    return get_member_detail(db, member.id)


@router.delete('/{member_id}')
def delete_member_endpoint(
    member_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission('member_manage')),
) -> dict:
    """Delete a member."""
    member = get_member_or_404(db, member_id)
    check_household_access(db, member.household_id, current_user)
    delete_member(db, member)
    return {'message': '成员已删除'}


@router.post('/{member_id}/set-head')
def set_head(
    member_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission('member_manage')),
) -> dict:
    """Set member as head of household."""
    member = get_member_or_404(db, member_id)
    check_household_access(db, member.household_id, current_user)
    set_as_household_head(db, member)
    return {'message': '已设为户主'}
