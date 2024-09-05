from pydantic import BaseModel, EmailStr, constr
from typing import Optional

class RegisterRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    password_confirmation: str
    role: Optional[str] = "admin"

    # Validate password confirmation
    @staticmethod
    def validate_password(data):
        if data["password"] != data["password_confirmation"]:
            raise ValueError("Passwords do not match")
        return data

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RegisterResponse(BaseModel):
    message: str
    status: int
    data: dict

class LoginResponse(BaseModel):
    message: str
    status: int
    data: dict

class UserResponse(BaseModel):
    id: int
    full_name: str
    email: str
    role: str

    class Config:
        orm_mode = True