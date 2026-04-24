"""System settings service."""

import os
import shutil
from pathlib import Path

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.db import engine
from app.core.settings import get_settings
from app.models.auth import User, Village
from app.models.household import Household, Member


SQLITE_HEADER = b'SQLite format 3'
ALLOWED_DATABASE_EXTENSIONS = {'.db', '.sqlite', '.sqlite3'}


def _get_sqlite_database_path() -> Path:
    settings = get_settings()
    database_url = settings.database_url

    for prefix in ('sqlite:///', 'sqlite+pysqlite:///'):
        if database_url.startswith(prefix):
            return Path(database_url.replace(prefix, '', 1)).resolve()

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail='当前仅支持 SQLite 数据库导入恢复',
    )


def _validate_database_extension(filename: str | None) -> None:
    suffix = Path(filename or '').suffix.lower()
    if suffix not in ALLOWED_DATABASE_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='仅支持导入 .db、.sqlite、.sqlite3 文件',
        )


def _is_valid_sqlite_file(content: bytes) -> bool:
    return content[:15] == SQLITE_HEADER


def get_database_info(db: Session) -> dict:
    """Get database information."""
    settings = get_settings()

    db_path = _get_sqlite_database_path()
    info = {
        'database_url': settings.database_url.split('@')[-1] if '@' in settings.database_url else settings.database_url,
    }

    if db_path.exists():
        stat = os.stat(db_path)
        info['file_size'] = stat.st_size
        info['file_size_mb'] = round(stat.st_size / (1024 * 1024), 2)
        info['last_modified'] = stat.st_mtime

    info['user_count'] = db.query(func.count(User.id)).scalar() or 0
    info['village_count'] = db.query(func.count(Village.id)).scalar() or 0
    info['household_count'] = db.query(func.count(Household.id)).scalar() or 0
    info['member_count'] = db.query(func.count(Member.id)).scalar() or 0

    return info


def get_backup_file_path() -> str:
    """Generate backup file path with timestamp."""
    from datetime import datetime

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = _get_sqlite_database_path().parent / 'backups'
    backup_dir.mkdir(parents=True, exist_ok=True)

    return str(backup_dir / f'household_backup_{timestamp}.db')


def import_database_file(file: UploadFile) -> dict:
    """Import and restore SQLite database from uploaded file."""
    _validate_database_extension(file.filename)

    content = file.file.read()
    if not content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='导入文件不能为空')
    if not _is_valid_sqlite_file(content):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='所选文件不是有效的 SQLite 数据库文件')

    db_path = _get_sqlite_database_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)

    backup_path = get_backup_file_path()
    engine.dispose()

    if db_path.exists():
        shutil.copy2(db_path, backup_path)

    with open(db_path, 'wb') as target:
        target.write(content)

    return {
        'message': '数据库导入成功，已自动备份当前数据库，请重启后端服务后重新登录。',
        'backup_path': backup_path,
        'requires_restart': True,
    }
