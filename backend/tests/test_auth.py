from contextlib import ExitStack

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_login_and_me_flow():
    with client:
        login_response = client.post('/api/v1/auth/login', json={'username': 'admin', 'password': 'admin123'})
        assert login_response.status_code == 200
        token = login_response.json()['access_token']

        me_response = client.get('/api/v1/auth/me', headers={'Authorization': f'Bearer {token}'})
        assert me_response.status_code == 200
        payload = me_response.json()
        assert payload['username'] == 'admin'
        assert 'super_admin' in payload['role_names']
        assert 'member_view' in payload['permission_names']
