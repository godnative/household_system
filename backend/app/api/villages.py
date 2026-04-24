"""Village management API endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import get_current_user, require_permission
from app.models.auth import User
from app.schemas.pagination import PaginatedMeta, PaginatedResponse
from app.schemas.village import VillageCreate, VillageDetail, VillageListItem, VillageUpdate
from app.services.village_service import (
    create_village,
    delete_village,
    get_village_detail,
    get_village_or_404,
    list_villages,
    update_village,
)

router = APIRouter(prefix='/api/v1/villages', tags=['villages'])


@router.get('', response_model=PaginatedResponse)
def get_villages(
    page: int = Query(1, ge=1, description='页码'),
    page_size: int = Query(20, ge=1, le=100, description='每页数量'),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PaginatedResponse:
    """List all villages. Filter by user's accessible villages for non-admins."""
    user_village_ids = None

    # Non-super_admin users can only see their accessible villages
    if current_user.role.name != 'super_admin':
        if current_user.village_id:
            user_village_ids = [current_user.village_id]
        elif current_user.accessible_villages:
            user_village_ids = [v.id for v in current_user.accessible_villages]
        else:
            user_village_ids = []

    items, total = list_villages(db, user_village_ids, page, page_size)
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


@router.get('/{village_id}', response_model=VillageDetail)
def get_village(
    village_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> VillageDetail:
    """Get village detail."""
    village = get_village_or_404(db, village_id)

    # Check access
    if current_user.role.name != 'super_admin':
        accessible_ids = []
        if current_user.village_id:
            accessible_ids = [current_user.village_id]
        elif current_user.accessible_villages:
            accessible_ids = [v.id for v in current_user.accessible_villages]
        if village_id not in accessible_ids:
            from fastapi import HTTPException, status

            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='无权访问该堂区')

    return get_village_detail(db, village_id)


@router.post('', response_model=VillageListItem)
def post_village(
    data: VillageCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission('village_manage')),
) -> VillageListItem:
    """Create a new village."""
    village = create_village(db, data)
    return VillageListItem(id=village.id, name=village.name, code=village.code, created_at=village.created_at)


@router.put('/{village_id}', response_model=VillageListItem)
def put_village(
    village_id: int,
    data: VillageUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission('village_manage')),
) -> VillageListItem:
    """Update a village."""
    village = get_village_or_404(db, village_id)
    village = update_village(db, village, data)
    return VillageListItem(id=village.id, name=village.name, code=village.code, created_at=village.created_at)


@router.delete('/{village_id}')
def delete_village_endpoint(
    village_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission('village_manage'),
)) -> dict:
    """Delete a village."""
    village = get_village_or_404(db, village_id)
    delete_village(db, village)
    return {'message': '堂区已删除'}
