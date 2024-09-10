import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_register_user():
    response = client.post(
        "/v1/auth/admin/api/register",
        json={
            "full_name": "admin",
            "email": "johnpaul.bailey@ethereal.email",
            "password": "password",
            "password_confirmation": "password",
            "role": "admin"
        }
    )
    
    assert response.status_code == 200
    assert response.json()["message"] == "Registration successful"
