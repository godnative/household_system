from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_upload_requires_authentication():
    with client:
        response = client.post('/api/v1/uploads', files={'file': ('avatar.png', b'fake', 'image/png')})
        assert response.status_code == 401
