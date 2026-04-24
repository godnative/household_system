"""Tests for search API endpoints."""

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


class TestSearchAPI:
    """Test search endpoints."""

    def test_search_households_requires_keyword(self, client: TestClient, admin_token: str) -> None:
        """Test that search requires keyword parameter."""
        response = client.get(
            '/api/v1/search/households',
            headers={'Authorization': f'Bearer {admin_token}'},
        )
        assert response.status_code == 422  # Validation error

    def test_search_households_empty_keyword(self, client: TestClient, admin_token: str) -> None:
        """Test that empty keyword returns validation error."""
        response = client.get(
            '/api/v1/search/households?keyword=',
            headers={'Authorization': f'Bearer {admin_token}'},
        )
        assert response.status_code == 422  # Validation error (min_length=1)

    def test_search_households_no_results(self, client: TestClient, admin_token: str) -> None:
        """Test search with no matching results."""
        response = client.get(
            '/api/v1/search/households?keyword=不存在的家庭关键词xyz',
            headers={'Authorization': f'Bearer {admin_token}'},
        )
        assert response.status_code == 200
        data = response.json()
        assert 'items' in data
        assert 'meta' in data
        assert data['items'] == []
        assert data['meta']['total'] == 0

    def test_search_members_requires_keyword(self, client: TestClient, admin_token: str) -> None:
        """Test that member search requires keyword parameter."""
        response = client.get(
            '/api/v1/search/members',
            headers={'Authorization': f'Bearer {admin_token}'},
        )
        assert response.status_code == 422  # Validation error

    def test_search_members_no_results(self, client: TestClient, admin_token: str) -> None:
        """Test member search with no matching results."""
        response = client.get(
            '/api/v1/search/members?keyword=不存在的成员关键词xyz',
            headers={'Authorization': f'Bearer {admin_token}'},
        )
        assert response.status_code == 200
        data = response.json()
        assert 'items' in data
        assert data['items'] == []
        assert data['meta']['total'] == 0

    def test_search_requires_authentication(self, client: TestClient) -> None:
        """Test that search requires authentication."""
        response = client.get('/api/v1/search/households?keyword=test')
        assert response.status_code == 401

        response = client.get('/api/v1/search/members?keyword=test')
        assert response.status_code == 401

    def test_search_pagination_params(self, client: TestClient, admin_token: str) -> None:
        """Test search pagination parameters."""
        response = client.get(
            '/api/v1/search/households?keyword=test&page=1&page_size=5',
            headers={'Authorization': f'Bearer {admin_token}'},
        )
        assert response.status_code == 200
        data = response.json()
        assert data['meta']['page'] == 1
        assert data['meta']['page_size'] == 5
