"""Tests for role management API."""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.db import SessionLocal
from app.models.auth import Role


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def admin_token(client: TestClient) -> str:
    """Get admin token for authenticated requests."""
    response = client.post('/api/v1/auth/login', json={'username': 'admin', 'password': 'admin123'})
    return response.json()['access_token']


class TestRolesAPI:
    """Test role management endpoints."""

    def test_list_roles_requires_permission(self, client: TestClient, admin_token: str) -> None:
        """Test that listing roles requires role_manage permission."""
        response = client.get('/api/v1/roles', headers={'Authorization': f'Bearer {admin_token}'})
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 3  # At least super_admin, data_entry, observer

    def test_get_role_detail(self, client: TestClient, admin_token: str) -> None:
        """Test getting role detail."""
        response = client.get('/api/v1/roles/1', headers={'Authorization': f'Bearer {admin_token}'})
        assert response.status_code == 200
        data = response.json()
        assert data['name'] == 'super_admin'
        assert 'permissions' in data

    def test_update_role_permissions(self, client: TestClient, admin_token: str) -> None:
        """Test updating role permissions (full replacement)."""
        # Get current data_entry role permissions
        response = client.get('/api/v1/roles/2', headers={'Authorization': f'Bearer {admin_token}'})
        original_permissions = response.json()['permissions']

        # Update with new permissions
        response = client.put(
            '/api/v1/roles/2',
            json={
                'name': 'data_entry',
                'description': '录入员',
                'permission_ids': [4, 5, 6],  # household_manage, household_view, member_manage
            },
            headers={'Authorization': f'Bearer {admin_token}'},
        )
        assert response.status_code == 200
        data = response.json()
        permission_ids = [p['id'] for p in data['permissions']]
        assert permission_ids == [4, 5, 6]

        # Restore original permissions
        original_ids = [p['id'] for p in original_permissions]
        client.put(
            '/api/v1/roles/2',
            json={
                'name': 'data_entry',
                'description': '录入员',
                'permission_ids': original_ids,
            },
            headers={'Authorization': f'Bearer {admin_token}'},
        )

    def test_get_permission_options(self, client: TestClient, admin_token: str) -> None:
        """Test getting permission options."""
        response = client.get('/api/v1/roles/options/permissions', headers={'Authorization': f'Bearer {admin_token}'})
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 7  # 7 permissions

    def test_create_custom_role(self, client: TestClient, admin_token: str) -> None:
        """Test creating a custom role."""
        response = client.post(
            '/api/v1/roles',
            json={
                'name': 'custom_role',
                'description': '自定义角色',
                'permission_ids': [4, 5],  # household_manage, household_view
            },
            headers={'Authorization': f'Bearer {admin_token}'},
        )
        assert response.status_code == 200
        data = response.json()
        assert data['name'] == 'custom_role'
        assert data['description'] == '自定义角色'

        # Cleanup
        db = SessionLocal()
        role = db.query(Role).filter(Role.name == 'custom_role').first()
        if role:
            db.delete(role)
            db.commit()
        db.close()

    def test_non_admin_cannot_access_roles(self, client: TestClient, admin_token: str) -> None:
        """Test that non-admin cannot access role management."""
        # Create a data_entry user
        client.post(
            '/api/v1/users',
            json={
                'username': 'entry_role_test',
                'password': 'test123',
                'role_id': 2,
                'is_active': True,
                'village_id': 1,
            },
            headers={'Authorization': f'Bearer {admin_token}'},
        )

        # Login as data_entry user
        entry_resp = client.post('/api/v1/auth/login', json={'username': 'entry_role_test', 'password': 'test123'})
        entry_token = entry_resp.json()['access_token']

        # Try to access roles list
        response = client.get('/api/v1/roles', headers={'Authorization': f'Bearer {entry_token}'})
        assert response.status_code == 403

        # Cleanup
        db = SessionLocal()
        from app.models.auth import User

        user = db.query(User).filter(User.username == 'entry_role_test').first()
        if user:
            db.delete(user)
            db.commit()
        db.close()
