"""Tests for village, household and member API."""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.db import SessionLocal
from app.models.auth import User, Village
from app.models.household import Household, Member


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def admin_token(client: TestClient) -> str:
    """Get admin token for authenticated requests."""
    response = client.post('/api/v1/auth/login', json={'username': 'admin', 'password': 'admin123'})
    return response.json()['access_token']


class TestVillagesAPI:
    """Test village management endpoints."""

    def test_list_villages(self, client: TestClient, admin_token: str) -> None:
        """Test listing villages with pagination."""
        response = client.get('/api/v1/villages', headers={'Authorization': f'Bearer {admin_token}'})
        assert response.status_code == 200
        data = response.json()
        assert 'items' in data
        assert 'meta' in data
        assert isinstance(data['items'], list)
        assert data['meta']['total'] >= 1  # Default village

    def test_villages_pagination_params(self, client: TestClient, admin_token: str) -> None:
        """Test villages pagination parameters."""
        # Test page and page_size parameters
        response = client.get(
            '/api/v1/villages?page=1&page_size=5',
            headers={'Authorization': f'Bearer {admin_token}'},
        )
        assert response.status_code == 200
        data = response.json()
        assert 'items' in data
        assert 'meta' in data
        assert data['meta']['page'] == 1
        assert data['meta']['page_size'] == 5

    def test_create_village(self, client: TestClient, admin_token: str) -> None:
        """Test creating a village."""
        response = client.post(
            '/api/v1/villages',
            json={'name': '测试堂区', 'code': 'TEST001'},
            headers={'Authorization': f'Bearer {admin_token}'},
        )
        assert response.status_code == 200
        data = response.json()
        assert data['name'] == '测试堂区'
        assert data['code'] == 'TEST001'

        # Cleanup
        db = SessionLocal()
        village = db.query(Village).filter(Village.code == 'TEST001').first()
        if village:
            db.delete(village)
            db.commit()
        db.close()

    def test_create_village_requires_permission(self, client: TestClient, admin_token: str) -> None:
        """Test that creating village requires village_manage permission."""
        # Create a data_entry user
        client.post(
            '/api/v1/users',
            json={'username': 'entry_village', 'password': 'test123', 'role_id': 2, 'is_active': True, 'village_id': 1},
            headers={'Authorization': f'Bearer {admin_token}'},
        )

        # Login as data_entry
        login_resp = client.post('/api/v1/auth/login', json={'username': 'entry_village', 'password': 'test123'})
        entry_token = login_resp.json()['access_token']

        # Try to create village
        response = client.post(
            '/api/v1/villages',
            json={'name': '不应创建', 'code': 'NOPE'},
            headers={'Authorization': f'Bearer {entry_token}'},
        )
        assert response.status_code == 403

        # Cleanup
        db = SessionLocal()
        user = db.query(User).filter(User.username == 'entry_village').first()
        if user:
            db.delete(user)
            db.commit()
        db.close()


class TestHouseholdsAPI:
    """Test household management endpoints."""

    def test_list_households(self, client: TestClient, admin_token: str) -> None:
        """Test listing households with pagination."""
        response = client.get('/api/v1/households', headers={'Authorization': f'Bearer {admin_token}'})
        assert response.status_code == 200
        data = response.json()
        assert 'items' in data
        assert 'meta' in data
        assert isinstance(data['items'], list)

    def test_create_household(self, client: TestClient, admin_token: str) -> None:
        """Test creating a household."""
        response = client.post(
            '/api/v1/households',
            json={'village_id': 1, 'plot_number': 1, 'address': '测试地址123号', 'phone': '13800138000'},
            headers={'Authorization': f'Bearer {admin_token}'},
        )
        assert response.status_code == 200
        data = response.json()
        assert data['address'] == '测试地址123号'

        # Cleanup
        db = SessionLocal()
        household = db.query(Household).filter(Household.id == data['id']).first()
        if household:
            db.delete(household)
            db.commit()
        db.close()


class TestMembersAPI:
    """Test member management endpoints."""

    def test_list_members(self, client: TestClient, admin_token: str) -> None:
        """Test listing members with pagination."""
        response = client.get('/api/v1/members', headers={'Authorization': f'Bearer {admin_token}'})
        assert response.status_code == 200
        data = response.json()
        assert 'items' in data
        assert 'meta' in data
        assert isinstance(data['items'], list)

    def test_create_member(self, client: TestClient, admin_token: str) -> None:
        """Test creating a member."""
        # First create a household
        hh_resp = client.post(
            '/api/v1/households',
            json={'village_id': 1, 'plot_number': 99, 'address': '成员测试家庭'},
            headers={'Authorization': f'Bearer {admin_token}'},
        )
        household_id = hh_resp.json()['id']

        # Create member
        response = client.post(
            '/api/v1/members',
            json={'household_id': household_id, 'name': '测试成员', 'gender': '男'},
            headers={'Authorization': f'Bearer {admin_token}'},
        )
        assert response.status_code == 200
        data = response.json()
        assert data['name'] == '测试成员'

        # Cleanup
        db = SessionLocal()
        member = db.query(Member).filter(Member.id == data['id']).first()
        if member:
            db.delete(member)
        household = db.query(Household).filter(Household.id == household_id).first()
        if household:
            db.delete(household)
        db.commit()
        db.close()

    def test_create_member_requires_permission(self, client: TestClient, admin_token: str) -> None:
        """Test that creating member requires member_manage permission."""
        # Create an observer user
        client.post(
            '/api/v1/users',
            json={'username': 'observer_member', 'password': 'test123', 'role_id': 3, 'is_active': True, 'accessible_village_ids': [1]},
            headers={'Authorization': f'Bearer {admin_token}'},
        )

        # Login as observer
        login_resp = client.post('/api/v1/auth/login', json={'username': 'observer_member', 'password': 'test123'})
        observer_token = login_resp.json()['access_token']

        # Try to create member
        response = client.post(
            '/api/v1/members',
            json={'household_id': 1, 'name': '不应创建', 'gender': '男'},
            headers={'Authorization': f'Bearer {observer_token}'},
        )
        assert response.status_code == 403

        # Cleanup
        db = SessionLocal()
        user = db.query(User).filter(User.username == 'observer_member').first()
        if user:
            db.delete(user)
            db.commit()
        db.close()
