from http import client


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
    assert response.json() == {
        "message": "Registration successful",
        "status": 200,
        "data": {
            "message": "Registration successful, please verify your email with the OTP sent.",
            "expires_in": 1800,
            "timestamp": response.json()["data"]["timestamp"],
            "role": "admin"
        }
    }
