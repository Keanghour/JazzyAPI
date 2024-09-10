# app\schemas\auth.py

from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional

from pydantic_settings import BaseSettings

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



# Forget Password Request Schema
class ForgetPasswordRequest(BaseModel):
    email: EmailStr

# Reset Password Request Schema
class ResetPasswordRequest(BaseModel):
    password: str
    password_confirmation: str
    password_token: str

    class Config:
        json_schema_extra = {
            "example": {
                "password": "newpassword",
                "password_confirmation": "newpassword",
                "password_token": "9009ed1a-a293-4bb6-a179-60507bffc538"
            }
        }



class UpdateUserInfo(BaseModel):
    full_name: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=6)
    role: Optional[str] = Field(None, max_length=20)  # e.g., "admin", "user"
    
    # class Config:
    #     orm_mode = True

    class Config:
        from_attributes = True

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

class TokenRefreshRequest(BaseModel):
    refresh_token: str


class OAuth2ClientCreateRequest(BaseModel):
    client_id: str
    client_secret: str
    username: str
    password: str
    redirect_uris: Optional[List[str]]  # Optional should be used with List[str] 

class OAuth2ClientResponse(BaseModel):
    message: str
    status: int
    data: dict

class TokenRequest(BaseModel):
    client_id: str
    client_secret: str


class EmailRequest(BaseModel):
    to_email: EmailStr
    subject: str
    message: str



class Settings(BaseSettings):
    mail_host: str
    mail_port: int
    mail_username: str
    mail_password: str
    email_from: str

    class Config:
        env_file = "env/.env"


        
         