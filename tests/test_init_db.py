from pathlib import Path

from src.models import Role, Permission, User, Village
from src.models.init_db import ensure_seed_data
from src.services.auth_service import AuthService


def test_missing_database_file_is_initialized(tmp_path, monkeypatch):
    database_path = tmp_path / 'data' / 'household.db'
    parent_dir = database_path.parent

    assert not parent_dir.exists()

    monkeypatch.setattr('src.models.base.DB_PATH', str(database_path))
    from src.models.base import ensure_database_parent_dir_exists

    ensure_database_parent_dir_exists()

    assert parent_dir.exists()


def test_ensure_seed_data_is_idempotent(test_db):
    db = test_db

    ensure_seed_data(db)
    ensure_seed_data(db)

    assert db.query(User).filter(User.username == 'admin').count() == 1
    assert db.query(Role).count() == 3
    assert db.query(Permission).count() == 7
    assert db.query(Village).filter(Village.code == '001').count() == 1


def test_existing_admin_password_is_not_reset(test_db_with_data):
    db = test_db_with_data['db']
    admin = db.query(User).filter(User.username == 'admin').first()
    original_hash = admin.password_hash
    admin.password_hash = AuthService.get_password_hash('changed-password')
    db.commit()

    ensure_seed_data(db)

    db.refresh(admin)
    assert admin.password_hash != original_hash
    assert AuthService.authenticate_user(db, 'admin', 'changed-password') is not None
    assert AuthService.authenticate_user(db, 'admin', 'admin123') is None
