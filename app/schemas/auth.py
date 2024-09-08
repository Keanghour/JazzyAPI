from pydantic import BaseModel, EmailStr
from typing import Optional

# class RegisterRequest(BaseModel):
#     full_name: str
#     email: EmailStr
#     password: str
#     password_confirmation: str
#     role: Optional[str] = "admin"

#     # Validate password confirmation
#     @staticmethod
#     def validate_password(data):
#         if data["password"] != data["password_confirmation"]:
#             raise ValueError("Passwords do not match")
#         return data

# class LoginRequest(BaseModel):
#     email: EmailStr
#     password: str

# class RegisterResponse(BaseModel):
#     message: str
#     status: int
#     data: dict

# class LoginResponse(BaseModel):
#     message: str
#     status: int
#     data: dict

# class UserResponse(BaseModel):
#     id: int
#     full_name: str
#     email: str
#     role: str

#     class Config:
#         orm_mode = True

# class OTPRequest(BaseModel):
#     email: EmailStr

# class OTPVerifyRequest(BaseModel):
#     email: EmailStr
#     otp_code: int

# class OTPResendRequest(BaseModel):
#     email: EmailStr

# Registration request
class RegisterRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    password_confirmation: str
    role: str

class RegisterResponse(BaseModel):
    message: str
    status: int
    data: dict

# Login request
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    message: str
    status: int
    data: dict

# OTP Requests
class OTPRequest(BaseModel):
    email: EmailStr

class OTPVerifyRequest(BaseModel):
    email: EmailStr
    otp_code: int

class OTPResendRequest(BaseModel):
    email: EmailStr

# User Response
class UserResponse(BaseModel):
    id: int
    full_name: Optional[str] = None
    email: str
    role: str
    is_active: bool

    class Config:
        from_attributes = True

# class UserResponse(BaseModel):
#     id: int
#     full_name: str
#     email: str
#     role: str  # Add this line to include the role field

#     class Config:
#         orm_mode = True

class ChangeEmailRequest(BaseModel):
    new_email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str