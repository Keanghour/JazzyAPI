# app/api/auth/admin/routes.py

from datetime import timedelta
from typing import List
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException,Header, status
from sqlalchemy.orm import Session
from app.core.security import ACCESS_TOKEN_EXPIRE_MINUTES, get_current_user
from app.database.config import get_db
from app.database.models import User

from app.schemas.auth import ( ChangeEmailRequest, ForgetPasswordRequest, OAuth2ClientCreateRequest,
OAuth2ClientResponse, RefreshTokenRequest, RegisterRequest, RegisterResponse, LoginRequest, LoginResponse,
OTPRequest,OTPResendRequest, OTPVerifyRequest, ResetPasswordRequest, TokenRequest, TokenResponse, UserResponse )

from app.api.auth.admin.controllers import ( change_user_email, forgot_password_controller, get_all_users,
get_user_by_id, refresh_token, register_user, login_user, register_user_and_client, request_otp,
request_token_controller, reset_password_controller, verify_otp,resend_otp )

from app.security.jwt import validate_token

router = APIRouter()

@router.get("/token")
def request_token(client_id: str, client_secret: str, db: Session = Depends(get_db)):
    try:
        access_token = request_token_controller(client_id, client_secret, db)
        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException as e:
        raise e

@router.post("/register/oauth2")
def register_user_and_client_endpoint(request: OAuth2ClientCreateRequest, db: Session = Depends(get_db)):
    return register_user_and_client(request, db)

@router.post("/token/refresh", response_model=TokenResponse)
async def refresh_token_endpoint(request: RefreshTokenRequest, db: Session = Depends(get_db)) -> TokenResponse:
    return refresh_token(request, db)

@router.get("/current-user", response_model=UserResponse)
async def get_current_user_route(
    current_user: User = Depends(get_current_user),  
    db: Session = Depends(get_db)
):  return current_user
    

@router.get("/users", response_model=List[UserResponse])
def get_users_route(
    current_user: User = Depends(get_current_user),  
    db: Session = Depends(get_db)
):  return get_all_users(db)

@router.get("/users/{user_id}", response_model=UserResponse)
def get_user_route(
    user_id: int,
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):  return get_user_by_id(user_id, db)

@router.post("/register", response_model=RegisterResponse)
def register(request: RegisterRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    return register_user(request, db, background_tasks)

@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    return login_user(request, db)

@router.post("/request-otp")
def request_otp_endpoint(request: OTPRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    return request_otp(request, db, background_tasks)

@router.post("/verify-otp")
def otp_verify(request: OTPVerifyRequest, db: Session = Depends(get_db)):
    return verify_otp(request, db)

@router.post("/resend-otp")
def otp_resend(request: OTPResendRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    return request_otp(request, db, background_tasks)

@router.post("/logout")
def logout(authorization: str = Header(None), db: Session = Depends(get_db)):
    token = validate_token(authorization, db) 
    # Implement the logout logic here
    return {"message": "Logged out successfully"}

@router.post("/change-email")
async def change_email(
    request: ChangeEmailRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
): return change_user_email(request.new_email, request.password, current_user, db)

@router.post("/forgot-password")
def forgot_password(
    request: ForgetPasswordRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
): return forgot_password_controller(request.email, db, background_tasks)

@router.post("/reset-password")
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    return reset_password_controller(request.password, request.password_confirmation, request.password_token, db)

