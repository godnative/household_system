"""Permission regression tests - verify RBAC and data scope controls."""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.db import SessionLocal
from app.models.auth import User, Village


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def admin_token(client: TestClient) -> str:
    response = client.post('/api/v1/auth/login', json={'username': 'admin', 'password': 'admin123'})
    return response.json()['access_token']


@pytest.fixture
def data_entry_token(client: TestClient, admin_token: str) -> str:
    """Create and login as data_entry user."""
    # Create data_entry user
    client.post(
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

    response = client.post('/api/v1/auth/login', json={'username': 'test_entry', 'password': 'test123'})
    return response.json()['access_token']


@pytest.fixture
def observer_token(client: TestClient, admin_token: str) -> str:
    """Create and login as observer user."""
    # Create observer user
    client.post(
        '/api/v1/users',
        json={
            'username': 'test_observer',
            'password': 'test123',
            'role_id': 3,  # observer
            'is_active': True,
            'accessible_village_ids': [1],
        },
        headers={'Authorization': f'Bearer {admin_token}'},
    )

    response = client.post('/api/v1/auth/login', json={'username': 'test_observer', 'password': 'test123'})
    return response.json()['access_token']


class TestSuperAdminPermissions:
    """Test super_admin permissions."""

    def test_can_access_all_villages(self, client: TestClient, admin_token: str) -> None:
        """Super admin can see all villages."""
        response = client.get('/api/v1/villages', headers={'Authorization': f'Bearer {admin_token}'})
        assert response.status_code == 200

    def test_can_create_village(self, client: TestClient, admin_token: str) -> None:
        """Super admin can create villages."""
        response = client.post(
            '/api/v1/villages',
            json={'name': '测试堂区权限', 'code': 'PERM_TEST'},
            headers={'Authorization': f'Bearer {admin_token}'},
        )
        assert response.status_code == 200

        # Cleanup
        db = SessionLocal()
        village = db.query(Village).filter(Village.code == 'PERM_TEST').first()
        if village:
            db.delete(village)
            db.commit()
        db.close()

    def test_can_manage_users(self, client: TestClient, admin_token: str) -> None:
        """Super admin can manage users."""
        response = client.get('/api/v1/users', headers={'Authorization': f'Bearer {admin_token}'})
        assert response.status_code == 200

    def test_can_manage_roles(self, client: TestClient, admin_token: str) -> None:
        """Super admin can manage roles."""
        response = client.get('/api/v1/roles', headers={'Authorization': f'Bearer {admin_token}'})
        assert response.status_code == 200


class TestDataEntryPermissions:
    """Test data_entry permissions."""

    def test_cannot_create_village(self, client: TestClient, data_entry_token: str) -> None:
        """Data entry cannot create villages."""
        response = client.post(
            '/api/v1/villages',
            json={'name': '不应创建', 'code': 'NOPE'},
            headers={'Authorization': f'Bearer {data_entry_token}'},
        )
        assert response.status_code == 403

    def test_can_create_household_in_own_village(self, client: TestClient, data_entry_token: str) -> None:
        """Data entry can create households in their assigned village."""
        response = client.post(
            '/api/v1/households',
            json={
                'village_id': 1,
                'plot_number': 99,
                'address': '权限测试地址',
            },
            headers={'Authorization': f'Bearer {data_entry_token}'},
        )
        assert response.status_code == 200

        # Cleanup
        db = SessionLocal()
        from app.models.household import Household
        household = db.query(Household).filter(Household.address == '权限测试地址').first()
        if household:
            db.delete(household)
            db.commit()
        db.close()

    def test_can_create_member(self, client: TestClient, data_entry_token: str) -> None:
        """Data entry can create members."""
        # First create household
        hh_resp = client.post(
            '/api/v1/households',
            json={'village_id': 1, 'plot_number': 88, 'address': '成员测试家庭'},
            headers={'Authorization': f'Bearer {data_entry_token}'},
        )
        household_id = hh_resp.json()['id']

        # Create member
        response = client.post(
            '/api/v1/members',
            json={'household_id': household_id, 'name': '测试成员', 'gender': '男'},
            headers={'Authorization': f'Bearer {data_entry_token}'},
        )
        assert response.status_code == 200

        # Cleanup
        db = SessionLocal()
        from app.models.household import Household, Member
        member = db.query(Member).filter(Member.name == '测试成员').first()
        if member:
            db.delete(member)
        household = db.query(Household).filter(Household.id == household_id).first()
        if household:
            db.delete(household)
        db.commit()
        db.close()


class TestObserverPermissions:
    """Test observer permissions."""

    def test_cannot_create_household(self, client: TestClient, observer_token: str) -> None:
        """Observer cannot create households."""
        response = client.post(
            '/api/v1/households',
            json={'village_id': 1, 'plot_number': 77, 'address': '不应创建'},
            headers={'Authorization': f'Bearer {observer_token}'},
        )
        assert response.status_code == 403

    def test_cannot_create_member(self, client: TestClient, observer_token: str) -> None:
        """Observer cannot create members."""
        response = client.post(
            '/api/v1/members',
            json={'household_id': 1, 'name': '不应创建', 'gender': '男'},
            headers={'Authorization': f'Bearer {observer_token}'},
        )
        assert response.status_code == 403

    def test_can_view_households(self, client: TestClient, observer_token: str) -> None:
        """Observer can view households."""
        response = client.get('/api/v1/households', headers={'Authorization': f'Bearer {observer_token}'})
        assert response.status_code == 200

    def test_can_view_members(self, client: TestClient, observer_token: str) -> None:
        """Observer can view members."""
        response = client.get('/api/v1/members', headers={'Authorization': f'Bearer {observer_token}'})
        assert response.status_code == 200


class TestUnauthenticatedAccess:
    """Test unauthenticated access is blocked."""

    def test_cannot_access_villages(self, client: TestClient) -> None:
        """Unauthenticated cannot access villages."""
        response = client.get('/api/v1/villages')
        assert response.status_code == 401

    def test_cannot_access_households(self, client: TestClient) -> None:
        """Unauthenticated cannot access households."""
        response = client.get('/api/v1/households')
        assert response.status_code == 401

    def test_cannot_access_users(self, client: TestClient) -> None:
        """Unauthenticated cannot access users."""
        response = client.get('/api/v1/users')
        assert response.status_code == 401


class TestTokenValidation:
    """Test token validation."""

    def test_invalid_token(self, client: TestClient) -> None:
        """Invalid token should return 401."""
        response = client.get('/api/v1/villages', headers={'Authorization': 'Bearer invalid_token'})
        assert response.status_code == 401

    def test_expired_token_format(self, client: TestClient) -> None:
        """Malformed authorization header should return 401."""
        response = client.get('/api/v1/villages', headers={'Authorization': 'InvalidFormat'})
        assert response.status_code == 401
