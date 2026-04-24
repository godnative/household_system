"""Tests for user management API."""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.db import SessionLocal
from app.models.auth import User


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def admin_token(client: TestClient) -> str:
    """Get admin token for authenticated requests."""
    response = client.post('/api/v1/auth/login', json={'username': 'admin', 'password': 'admin123'})
    return response.json()['access_token']


@pytest.fixture
def test_user_id(client: TestClient, admin_token: str) -> int:
    """Create a test user and return its ID."""
    # First check if user already exists
    db = SessionLocal()
    existing_user = db.query(User).filter(User.username == 'test_entry').first()
    if existing_user:
        user_id = existing_user.id
        db.close()
        yield user_id
        return

    db.close()

    response = client.post(
        '/api/v1/users',
        json={
            'username': 'test_entry',
            'password': 'test123',
            'role_id': 2,  # data_entry
            'is_active': True,
            'village_id': 1,
        },
        headers={'Authorization': f'Bearer {admin_token}'},
    )
    data = response.json()
    user_id = data.get('id')
    if not user_id:
        # User might already exist, find it
        db = SessionLocal()
        user = db.query(User).filter(User.username == 'test_entry').first()
        if user:
            user_id = user.id
        db.close()

    yield user_id
    # Cleanup
    db = SessionLocal()
    user = db.query(User).filter(User.username == 'test_entry').first()
    if user:
        db.delete(user)
        db.commit()
    db.close()


class TestUsersAPI:
    """Test user management endpoints."""

    def test_list_users_requires_permission(self, client: TestClient) -> None:
        """Test that listing users requires user_manage permission."""
        # Login as data_entry user
        # First create a data_entry user
        admin_resp = client.post('/api/v1/auth/login', json={'username': 'admin', 'password': 'admin123'})
        admin_token = admin_resp.json()['access_token']

        # Create data_entry user
        client.post(
            '/api/v1/users',
            json={
                'username': 'entry_test',
                'password': 'test123',
                'role_id': 2,
                'is_active': True,
                'village_id': 1,
            },
            headers={'Authorization': f'Bearer {admin_token}'},
        )

        # Login as data_entry user
        entry_resp = client.post('/api/v1/auth/login', json={'username': 'entry_test', 'password': 'test123'})
        entry_token = entry_resp.json()['access_token']

        # Try to access users list
        response = client.get('/api/v1/users', headers={'Authorization': f'Bearer {entry_token}'})
        assert response.status_code == 403

        # Cleanup
        db = SessionLocal()
        user = db.query(User).filter(User.username == 'entry_test').first()
        if user:
            db.delete(user)
            db.commit()
        db.close()

    def test_list_users_success(self, client: TestClient, admin_token: str) -> None:
        """Test listing users with proper permission."""
        response = client.get('/api/v1/users', headers={'Authorization': f'Bearer {admin_token}'})
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_create_data_entry_user_requires_village(self, client: TestClient, admin_token: str) -> None:
        """Test that data_entry user requires village_id."""
        response = client.post(
            '/api/v1/users',
            json={
                'username': 'entry_no_village',
                'password': 'test123',
                'role_id': 2,  # data_entry
                'is_active': True,
            },
            headers={'Authorization': f'Bearer {admin_token}'},
        )
        assert response.status_code == 400
        assert '所属堂区' in response.json()['detail']

    def test_create_observer_with_accessible_villages(self, client: TestClient, admin_token: str) -> None:
        """Test creating observer user with accessible villages."""
        response = client.post(
            '/api/v1/users',
            json={
                'username': 'observer_test',
                'password': 'test123',
                'role_id': 3,  # observer
                'is_active': True,
                'accessible_village_ids': [1],
            },
            headers={'Authorization': f'Bearer {admin_token}'},
        )
        assert response.status_code == 200
        data = response.json()
        assert data['accessible_village_ids'] == [1]
        assert data['village_id'] is None

        # Cleanup
        db = SessionLocal()
        user = db.query(User).filter(User.username == 'observer_test').first()
        if user:
            db.delete(user)
            db.commit()
        db.close()

    def test_reset_password(self, client: TestClient, admin_token: str, test_user_id: int) -> None:
        """Test resetting user password."""
        response = client.put(
            f'/api/v1/users/{test_user_id}/password',
            json={'new_password': 'newpass123'},
            headers={'Authorization': f'Bearer {admin_token}'},
        )
        assert response.status_code == 200

        # Verify new password works
        login_resp = client.post('/api/v1/auth/login', json={'username': 'test_entry', 'password': 'newpass123'})
        assert login_resp.status_code == 200


class TestAuthMeExtended:
    """Test extended /auth/me response."""

    def test_me_returns_extended_fields(self, client: TestClient, admin_token: str) -> None:
        """Test that /auth/me returns extended fields."""
        response = client.get('/api/v1/auth/me', headers={'Authorization': f'Bearer {admin_token}'})
        assert response.status_code == 200
        data = response.json()
        assert 'role' in data
        assert 'permission_names' in data
        assert 'village_id' in data
        assert 'accessible_village_ids' in data
        assert 'is_active' in data

    def test_change_password(self, client: TestClient, admin_token: str) -> None:
        """Test changing password."""
        response = client.post(
            '/api/v1/auth/change-password',
            json={'old_password': 'admin123', 'new_password': 'newadmin123'},
            headers={'Authorization': f'Bearer {admin_token}'},
        )
        assert response.status_code == 200

        # Verify new password works
        login_resp = client.post('/api/v1/auth/login', json={'username': 'admin', 'password': 'newadmin123'})
        assert login_resp.status_code == 200

        # Reset password back
        new_token = login_resp.json()['access_token']
        client.post(
            '/api/v1/auth/change-password',
            json={'old_password': 'newadmin123', 'new_password': 'admin123'},
            headers={'Authorization': f'Bearer {new_token}'},
        )
