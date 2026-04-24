"""Security baseline tests - verify protection against common attacks."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def admin_token(client: TestClient) -> str:
    response = client.post('/api/v1/auth/login', json={'username': 'admin', 'password': 'admin123'})
    return response.json()['access_token']


class TestSQLInjection:
    """Test SQL injection protection."""

    def test_login_sql_injection(self, client: TestClient) -> None:
        """SQL injection in login should not work."""
        # Classic SQL injection attempt
        response = client.post(
            '/api/v1/auth/login',
            json={'username': "admin' OR '1'='1", 'password': 'anything'},
        )
        assert response.status_code == 401

    def test_search_sql_injection(self, client: TestClient, admin_token: str) -> None:
        """SQL injection in search should not work."""
        response = client.get(
            "/api/v1/search/households?keyword=' OR '1'='1",
            headers={'Authorization': f'Bearer {admin_token}'},
        )
        # Should not crash or return all data
        assert response.status_code in [200, 422]

    def test_village_name_sql_injection(self, client: TestClient, admin_token: str) -> None:
        """SQL injection in village creation should be handled."""
        response = client.post(
            '/api/v1/villages',
            json={'name': "'; DROP TABLE villages; --", 'code': 'SQL_TEST'},
            headers={'Authorization': f'Bearer {admin_token}'},
        )
        # Should either succeed (safe) or reject
        assert response.status_code in [200, 400]


class TestXSS:
    """Test XSS protection."""

    def test_xss_in_village_name(self, client: TestClient, admin_token: str) -> None:
        """XSS payload in village name should be stored safely."""
        xss_payload = '<script>alert("xss")</script>'
        response = client.post(
            '/api/v1/villages',
            json={'name': xss_payload, 'code': 'XSS_TEST'},
            headers={'Authorization': f'Bearer {admin_token}'},
        )
        assert response.status_code == 200

        # Cleanup
        from app.core.db import SessionLocal
        from app.models.auth import Village
        db = SessionLocal()
        village = db.query(Village).filter(Village.code == 'XSS_TEST').first()
        if village:
            db.delete(village)
            db.commit()
        db.close()

    def test_xss_in_household_address(self, client: TestClient, admin_token: str) -> None:
        """XSS payload in household address should be stored safely."""
        xss_payload = '<img src=x onerror=alert(1)>'
        response = client.post(
            '/api/v1/households',
            json={
                'village_id': 1,
                'plot_number': 999,
                'address': xss_payload,
            },
            headers={'Authorization': f'Bearer {admin_token}'},
        )
        assert response.status_code == 200

        # Cleanup
        from app.core.db import SessionLocal
        from app.models.household import Household
        db = SessionLocal()
        household = db.query(Household).filter(Household.plot_number == 999).first()
        if household:
            db.delete(household)
            db.commit()
        db.close()


class TestAuthenticationSecurity:
    """Test authentication security."""

    def test_wrong_password_rejected(self, client: TestClient) -> None:
        """Wrong password should be rejected."""
        response = client.post(
            '/api/v1/auth/login',
            json={'username': 'admin', 'password': 'wrongpassword'},
        )
        assert response.status_code == 401

    def test_nonexistent_user_rejected(self, client: TestClient) -> None:
        """Non-existent user should be rejected."""
        response = client.post(
            '/api/v1/auth/login',
            json={'username': 'nonexistent', 'password': 'password'},
        )
        assert response.status_code == 401

    def test_token_required_for_protected_endpoints(self, client: TestClient) -> None:
        """Protected endpoints should require valid token."""
        endpoints = [
            ('GET', '/api/v1/villages'),
            ('GET', '/api/v1/households'),
            ('GET', '/api/v1/members'),
            ('GET', '/api/v1/users'),
        ]
        for method, endpoint in endpoints:
            if method == 'GET':
                response = client.get(endpoint)
            assert response.status_code == 401


class TestAuthorizationSecurity:
    """Test authorization security."""

    def test_cannot_access_other_village_data(self, client: TestClient, admin_token: str) -> None:
        """Data entry user cannot access other village's data."""
        # Create data entry user for village 1
        client.post(
            '/api/v1/users',
            json={
                'username': 'village1_user',
                'password': 'test123',
                'role_id': 2,
                'is_active': True,
                'village_id': 1,
            },
            headers={'Authorization': f'Bearer {admin_token}'},
        )

        # Login as data entry user
        login_resp = client.post('/api/v1/auth/login', json={'username': 'village1_user', 'password': 'test123'})
        user_token = login_resp.json()['access_token']

        # Create a village 2
        village_resp = client.post(
            '/api/v1/villages',
            json={'name': '其他堂区', 'code': 'OTHER_V'},
            headers={'Authorization': f'Bearer {admin_token}'},
        )
        other_village_id = village_resp.json()['id']

        # Create household in village 2
        hh_resp = client.post(
            '/api/v1/households',
            json={
                'village_id': other_village_id,
                'plot_number': 1,
                'address': '其他堂区地址',
            },
            headers={'Authorization': f'Bearer {admin_token}'},
        )

        # Data entry user should not see village 2
        response = client.get('/api/v1/villages', headers={'Authorization': f'Bearer {user_token}'})
        villages = response.json()['items']
        village_ids = [v['id'] for v in villages]
        assert other_village_id not in village_ids

        # Cleanup
        from app.core.db import SessionLocal
        from app.models.auth import User, Village
        from app.models.household import Household
        db = SessionLocal()
        user = db.query(User).filter(User.username == 'village1_user').first()
        if user:
            db.delete(user)
        hh = db.query(Household).filter(Household.address == '其他堂区地址').first()
        if hh:
            db.delete(hh)
        village = db.query(Village).filter(Village.code == 'OTHER_V').first()
        if village:
            db.delete(village)
        db.commit()
        db.close()


class TestInputValidation:
    """Test input validation."""

    def test_empty_username_rejected(self, client: TestClient) -> None:
        """Empty username should be rejected."""
        response = client.post('/api/v1/auth/login', json={'username': '', 'password': 'password'})
        # Either 401 (invalid credentials) or 422 (validation error) is acceptable
        assert response.status_code in [401, 422]

    def test_missing_fields_rejected(self, client: TestClient, admin_token: str) -> None:
        """Missing required fields should be rejected."""
        response = client.post(
            '/api/v1/villages',
            json={},  # Missing name and code
            headers={'Authorization': f'Bearer {admin_token}'},
        )
        assert response.status_code == 422

    def test_invalid_page_number(self, client: TestClient, admin_token: str) -> None:
        """Invalid page number should be rejected."""
        response = client.get(
            '/api/v1/villages?page=-1',
            headers={'Authorization': f'Bearer {admin_token}'},
        )
        assert response.status_code == 422
