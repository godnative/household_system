from fastapi.testclient import TestClient

from app.main import app, ensure_database_ready
from app.models.auth import User
from app.core.settings import Settings
from app.services.auth_service import hash_password


client = TestClient(app)


def test_missing_database_parent_directory_is_created(tmp_path, monkeypatch):
    database_path = tmp_path / 'nested' / 'startup.db'
    settings = Settings(DATABASE_URL=f'sqlite:///{database_path}')
    monkeypatch.setattr('app.main.settings', settings)

    assert not database_path.parent.exists()

    ensure_database_ready()

    assert database_path.parent.exists()


def test_ensure_database_ready_is_idempotent_for_default_seed(monkeypatch):
    settings = Settings(DATABASE_URL='sqlite:///:memory:')
    monkeypatch.setattr('app.main.settings', settings)

    ensure_database_ready()
    ensure_database_ready()

    with client:
        login_response = client.post('/api/v1/auth/login', json={'username': 'admin', 'password': 'admin123'})
        assert login_response.status_code == 200

        me_response = client.get('/api/v1/auth/me', headers={'Authorization': f"Bearer {login_response.json()['access_token']}"})
        assert me_response.status_code == 200
        assert me_response.json()['username'] == 'admin'


def test_existing_admin_password_is_not_reset(monkeypatch):
    settings = Settings(DATABASE_URL='sqlite:///:memory:')
    monkeypatch.setattr('app.main.settings', settings)

    ensure_database_ready()

    from app.core.db import SessionLocal

    with SessionLocal() as db:
        admin = db.query(User).filter(User.username == 'admin').first()
        admin.password_hash = hash_password('changed-password')
        db.commit()

    ensure_database_ready()

    with client:
        changed_login_response = client.post('/api/v1/auth/login', json={'username': 'admin', 'password': 'changed-password'})
        default_login_response = client.post('/api/v1/auth/login', json={'username': 'admin', 'password': 'admin123'})

    assert changed_login_response.status_code == 200
    assert default_login_response.status_code == 401
