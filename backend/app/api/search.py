"""Search API endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import get_current_user
from app.models.auth import User
from app.schemas.pagination import PaginatedMeta, PaginatedResponse
from app.services.search_service import search_households, search_members

router = APIRouter(prefix='/api/v1/search', tags=['search'])


@router.get('/households', response_model=PaginatedResponse)
def search_households_endpoint(
    keyword: str = Query(..., min_length=1, description='搜索关键词'),
    page: int = Query(1, ge=1, description='页码'),
    page_size: int = Query(20, ge=1, le=100, description='每页数量'),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PaginatedResponse:
    """Search households by keyword (head_of_household, address, phone)."""
    items, total = search_households(db, keyword, current_user, page, page_size)
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


@router.get('/members', response_model=PaginatedResponse)
def search_members_endpoint(
    keyword: str = Query(..., min_length=1, description='搜索关键词'),
    page: int = Query(1, ge=1, description='页码'),
    page_size: int = Query(20, ge=1, le=100, description='每页数量'),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PaginatedResponse:
    """Search members by keyword across 20+ fields."""
    items, total = search_members(db, keyword, current_user, page, page_size)
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
