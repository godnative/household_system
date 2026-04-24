"""API Contract tests - verify request/response formats match OpenAPI spec."""

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


class TestAPIContract:
    """Test API contract compliance."""

    def test_openapi_docs_available(self, client: TestClient) -> None:
        """Test that OpenAPI docs are available."""
        response = client.get('/docs')
        assert response.status_code == 200

    def test_openapi_json_available(self, client: TestClient) -> None:
        """Test that OpenAPI JSON schema is available."""
        response = client.get('/openapi.json')
        assert response.status_code == 200
        schema = response.json()
        assert 'openapi' in schema
        assert 'paths' in schema

    def test_auth_login_response_format(self, client: TestClient) -> None:
        """Test login response format."""
        response = client.post('/api/v1/auth/login', json={'username': 'admin', 'password': 'admin123'})
        assert response.status_code == 200
        data = response.json()
        assert 'access_token' in data
        assert 'token_type' in data
        assert data['token_type'] == 'bearer'

    def test_auth_login_invalid_credentials(self, client: TestClient) -> None:
        """Test login with invalid credentials."""
        response = client.post('/api/v1/auth/login', json={'username': 'admin', 'password': 'wrongpassword'})
        assert response.status_code == 401
        data = response.json()
        assert 'detail' in data

    def test_auth_me_response_format(self, client: TestClient, admin_token: str) -> None:
        """Test /auth/me response format."""
        response = client.get('/api/v1/auth/me', headers={'Authorization': f'Bearer {admin_token}'})
        assert response.status_code == 200
        data = response.json()
        assert 'id' in data
        assert 'username' in data
        assert 'role' in data
        assert 'permission_names' in data
        assert 'is_active' in data

    def test_error_response_format(self, client: TestClient) -> None:
        """Test that error responses have consistent format."""
        response = client.get('/api/v1/villages')  # No auth header
        assert response.status_code == 401
        data = response.json()
        assert 'detail' in data

    def test_paginated_response_format(self, client: TestClient, admin_token: str) -> None:
        """Test paginated response format."""
        response = client.get('/api/v1/villages', headers={'Authorization': f'Bearer {admin_token}'})
        assert response.status_code == 200
        data = response.json()
        assert 'items' in data
        assert 'meta' in data
        assert 'total' in data['meta']
        assert 'page' in data['meta']
        assert 'page_size' in data['meta']
        assert 'total_pages' in data['meta']

    def test_validation_error_format(self, client: TestClient, admin_token: str) -> None:
        """Test validation error response format."""
        response = client.post(
            '/api/v1/villages',
            json={'name': ''},  # Missing required 'code' field
            headers={'Authorization': f'Bearer {admin_token}'},
        )
        assert response.status_code == 422
        data = response.json()
        assert 'detail' in data


class TestHealthEndpoint:
    """Test health check endpoint."""

    def test_health_check(self, client: TestClient) -> None:
        """Test health check endpoint."""
        response = client.get('/health')
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'ok'


class TestHTTPMethods:
    """Test HTTP method handling."""

    def test_method_not_allowed(self, client: TestClient, admin_token: str) -> None:
        """Test that unsupported methods return 405."""
        response = client.patch('/api/v1/villages', headers={'Authorization': f'Bearer {admin_token}'})
        assert response.status_code == 405

    def test_options_request(self, client: TestClient) -> None:
        """Test CORS preflight handling."""
        response = client.options('/api/v1/auth/login')
        # CORS should be handled, not 404
        assert response.status_code in [200, 405]
