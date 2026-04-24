"""Upload functionality tests."""

import io
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


class TestFileUpload:
    """Test file upload functionality."""

    def test_upload_requires_authentication(self, client: TestClient) -> None:
        """Upload should require authentication."""
        response = client.post(
            '/api/v1/uploads',
            files={'file': ('test.jpg', b'fake_image_data', 'image/jpeg')},
        )
        assert response.status_code == 401

    def test_upload_jpeg_success(self, client: TestClient, admin_token: str) -> None:
        """JPEG upload should succeed."""
        # Create a minimal valid JPEG
        jpeg_header = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00'
        jpeg_data = jpeg_header + b'\xff\xd9'  # Add end marker

        response = client.post(
            '/api/v1/uploads',
            files={'file': ('test.jpg', jpeg_data, 'image/jpeg')},
            headers={'Authorization': f'Bearer {admin_token}'},
        )
        assert response.status_code == 200
        data = response.json()
        assert 'filename' in data
        assert 'url' in data
        assert data['content_type'] == 'image/jpeg'

    def test_upload_png_success(self, client: TestClient, admin_token: str) -> None:
        """PNG upload should succeed."""
        # Create a minimal valid PNG
        png_header = b'\x89PNG\r\n\x1a\n' + b'\x00' * 20  # PNG signature

        response = client.post(
            '/api/v1/uploads',
            files={'file': ('test.png', png_header, 'image/png')},
            headers={'Authorization': f'Bearer {admin_token}'},
        )
        assert response.status_code == 200
        data = response.json()
        assert data['content_type'] == 'image/png'

    def test_upload_invalid_type_rejected(self, client: TestClient, admin_token: str) -> None:
        """Non-image file should be rejected."""
        response = client.post(
            '/api/v1/uploads',
            files={'file': ('test.txt', b'hello world', 'text/plain')},
            headers={'Authorization': f'Bearer {admin_token}'},
        )
        assert response.status_code == 400

    def test_upload_exe_rejected(self, client: TestClient, admin_token: str) -> None:
        """Executable file should be rejected."""
        response = client.post(
            '/api/v1/uploads',
            files={'file': ('test.exe', b'MZ\x90\x00', 'application/octet-stream')},
            headers={'Authorization': f'Bearer {admin_token}'},
        )
        assert response.status_code == 400

    def test_upload_response_format(self, client: TestClient, admin_token: str) -> None:
        """Upload response should have expected format."""
        jpeg_header = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xd9'

        response = client.post(
            '/api/v1/uploads',
            files={'file': ('test.jpg', jpeg_header, 'image/jpeg')},
            headers={'Authorization': f'Bearer {admin_token}'},
        )
        assert response.status_code == 200
        data = response.json()
        assert 'filename' in data
        assert 'content_type' in data
        assert 'size' in data
        assert 'url' in data
        assert 'uploaded_by' in data
        assert data['uploaded_by'] == 'admin'


class TestFileSizeLimits:
    """Test file size limits."""

    def test_large_file_rejected(self, client: TestClient, admin_token: str) -> None:
        """Files over 5MB should be rejected."""
        # Create a file slightly over 5MB
        large_data = b'x' * (6 * 1024 * 1024)  # 6MB

        response = client.post(
            '/api/v1/uploads',
            files={'file': ('large.jpg', large_data, 'image/jpeg')},
            headers={'Authorization': f'Bearer {admin_token}'},
        )
        assert response.status_code == 400
