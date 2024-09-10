import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app

client = TestClient(app)

@patch('httpx.AsyncClient.post')
def test_send_email(mock_post):
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"message": "Email sent successfully"}

    response = client.post(
        "/v1/email/send-email",
        json={
            "to_email": "test@example.com",
            "subject": "Test Email",
            "message": "This is a test email."
        }
    )
    
    assert response.status_code == 200
    assert response.json() == {"message": "Email sent successfully"}
