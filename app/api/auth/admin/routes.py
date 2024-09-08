# app/api/auth/admin/routes.py

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session
from app.core.security import get_current_user
from app.database.config import get_db
from app.database.models import User
from app.schemas.auth import (
    ChangeEmailRequest,
    RegisterRequest,
    RegisterResponse,
    LoginRequest,
    LoginResponse,
    OTPRequest,
    OTPResendRequest,
    OTPVerifyRequest,
    UserResponse,
)
from app.api.auth.admin.controllers import (
    change_user_email,
    get_all_users,
    get_user_by_id,
    logout_user,
    register_user,
    login_user,
    request_otp,
    verify_otp,
    resend_otp,
)

from app.security.jwt import validate_token

router = APIRouter()


@router.get("/current-user", response_model=UserResponse)
def get_current_user_route(
    current_user: User = Depends(get_current_user),  # Use dependency to get current user
    db: Session = Depends(get_db)
):
    return current_user

@router.get("/users", response_model=List[UserResponse])
def get_users_route(
    current_user: User = Depends(get_current_user),  # Add token validation
    db: Session = Depends(get_db)
):
    return get_all_users(db)

@router.get("/users/{user_id}", response_model=UserResponse)
def get_user_route(
    user_id: int,
    current_user: User = Depends(get_current_user),  # Validate JWT token
    db: Session = Depends(get_db)
):
    return get_user_by_id(user_id, db)

@router.post("/register", response_model=RegisterResponse)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    return register_user(request, db)

@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    return login_user(request, db)

@router.post("/request-otp")
def otp_request(request: OTPRequest, db: Session = Depends(get_db)):
    return request_otp(request, db)

@router.post("/verify-otp")
def otp_verify(request: OTPVerifyRequest, db: Session = Depends(get_db)):
    return verify_otp(request, db)

@router.post("/resend-otp")
def otp_resend(request: OTPResendRequest, db: Session = Depends(get_db)):
    return resend_otp(request, db)

@router.post("/logout")
def logout(authorization: str = Header(None), db: Session = Depends(get_db)):
    token = validate_token(authorization, db)  # Validate the token
    # Implement the logout logic here
    return {"message": "Logged out successfully"}

@router.post("/change-email")
async def change_email(
    request: ChangeEmailRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return change_user_email(request.new_email, request.password, current_user, db)
