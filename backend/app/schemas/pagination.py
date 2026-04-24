"""Common pagination schemas."""

from pydantic import BaseModel


class PaginationParams(BaseModel):
    """Pagination query parameters."""

    page: int = 1
    page_size: int = 20


class PaginatedMeta(BaseModel):
    """Pagination metadata."""

    total: int
    page: int
    page_size: int
    total_pages: int


class PaginatedResponse(BaseModel):
    """Generic paginated response wrapper."""

    items: list
    meta: PaginatedMeta


def calculate_offset(page: int, page_size: int) -> int:
    """Calculate offset from page and page_size."""
    return (page - 1) * page_size


def calculate_total_pages(total: int, page_size: int) -> int:
    """Calculate total pages."""
    if total == 0:
        return 1
    return (total + page_size - 1) // page_size
