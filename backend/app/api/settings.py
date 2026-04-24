"""System settings API endpoints."""

import shutil

from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import get_current_user, require_permission
from app.core.settings import get_settings
from app.models.auth import User
from app.services.settings_service import get_backup_file_path, get_database_info, import_database_file

router = APIRouter(prefix='/api/v1/settings', tags=['settings'])


@router.get('/database-info')
def get_db_info(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Get database information."""
    return get_database_info(db)


@router.get('/backup')
def download_backup(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FileResponse:
    """Download database backup.

    Note: This is a simple implementation for SQLite.
    For production, consider using pg_dump for PostgreSQL.
    """
    from fastapi import HTTPException, status

    settings = get_settings()
    db_path = settings.database_url.replace('sqlite:///', '')
    if not db_path or not db_path.endswith('.db'):
        db_path = settings.database_url.replace('sqlite+pysqlite:///', '')

    if not db_path or not db_path.endswith('.db'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Backup is only supported for SQLite databases',
        )

    backup_path = get_backup_file_path()
    shutil.copy2(db_path, backup_path)

    return FileResponse(
        path=backup_path,
        filename=backup_path.split('/')[-1],
        media_type='application/octet-stream',
    )


@router.post('/import')
def import_database(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission('user_manage')),
) -> dict:
    """Import and restore SQLite database."""
    db.close()
    return import_database_file(file)
