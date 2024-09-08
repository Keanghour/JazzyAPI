# app/api/auth/admin/controllers.py

from datetime import datetime, timedelta
import random
from flask_jwt_extended import get_current_user
from sqlalchemy.orm import Session
from fastapi import HTTPException, Header, status
from app.database.models import OTP, User, UserLog
from app.core.security import create_access_token, verify_password, get_password_hash
from app.schemas.auth import ChangeEmailRequest, RegisterRequest, LoginRequest, OTPRequest, OTPResendRequest, OTPVerifyRequest

OTP_EXPIRE_MINUTES = 1
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def validate_token(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    # Implement your token validation logic here
    return True

def get_all_users(db: Session, authorization: str = Header(None)):
    validate_token(authorization)
    return db.query(User).all()

def get_user_by_id(user_id: int, db: Session, authorization: str = Header(None)):
    validate_token(authorization)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

# def get_current_user_by_token(token: str, db: Session) -> User:
#     user_email = validate_token(token, db) 
#     if not user_email:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token or expired")
    
#     user = db.query(User).filter(User.email == user_email).first()
#     if not user:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
#     return user

def get_current_user_by_token(token: str, db: Session):
    # Verify the token and extract user information
    user_data = verify_token(token)
    if not user_data:
        raise Exception("Invalid token")

    # Fetch user from the database
    user = db.query(User).filter(User.id == user_data["user_id"]).first()
    if not user:
        raise Exception("User not found")

    return user

def register_user(request: RegisterRequest, db: Session):
    if request.password != request.password_confirmation:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match")

    if db.query(User).filter(User.email == request.email).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    hashed_password = get_password_hash(request.password)

    new_user = User(
        full_name=request.full_name,
        email=request.email,
        hashed_password=hashed_password,
        role=request.role
    )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        user_log = UserLog(user_id=new_user.id, event="register")
        db.add(user_log)
        db.commit()

        # Immediately send OTP upon registration
        otp_code = random.randint(100000, 999999)
        expires_at = datetime.utcnow() + timedelta(minutes=OTP_EXPIRE_MINUTES)

        otp = OTP(
            email=request.email,
            otp_code=otp_code,
            expires_at=expires_at,
            request_time=datetime.utcnow(),
            active=True
        )
        
        db.add(otp)
        db.commit()

        return {
            "message": "Registration successful",
            "status": status.HTTP_200_OK,
            "data": {
                "message": "Registration successful, please verify your email with the OTP sent.",
                "otp_code": otp_code,  # In production, do not return this
                "expires_in": OTP_EXPIRE_MINUTES * 60,
                "timestamp": datetime.utcnow().isoformat(),
                "role": new_user.role
            }
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Registration failed")

def login_user(request: LoginRequest, db: Session):
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account not activated. Please verify your email with OTP.")

    # Token expiration time
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    # Create access token with user's email or ID
    access_token = create_access_token(
        data={"sub": user.email},  # or use {"sub": user.id} if you prefer
        expires_delta=access_token_expires
    )

    return {
        "message": "Login successful",
        "status": status.HTTP_200_OK,
        "data": {
            "jwt": {
                "access_token": access_token,
                "token_type": "bearer",
                "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
            }
        }
    }

def request_otp(request: OTPRequest, db: Session):
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    if user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already verified.")
    
    otp_code = random.randint(100000, 999999)
    expires_at = datetime.utcnow() + timedelta(minutes=OTP_EXPIRE_MINUTES)

    otp = OTP(
        email=request.email,
        otp_code=otp_code,
        expires_at=expires_at,
        request_time=datetime.utcnow(),
        active=True
    )

    try:
        db.add(otp)
        db.commit()
        return {
            "message": "OTP requested successfully",
            "data": {
                "otp_code": otp_code,  # In production, do not return this
                "expires_in": OTP_EXPIRE_MINUTES * 60
            }
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="OTP request failed")

def verify_otp(request: OTPVerifyRequest, db: Session):
    otp = db.query(OTP).filter(OTP.email == request.email, OTP.otp_code == request.otp_code, OTP.active == True).first()
    if not otp:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired OTP.")
    
    if otp.expires_at < datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OTP has expired.")

    otp.active = False
    db.commit()

    user = db.query(User).filter(User.email == request.email).first()
    user.is_active = True
    db.commit()

    return {
        "message": "OTP verified successfully. You can now log in."
    }

def resend_otp(request: OTPResendRequest, db: Session):
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    if user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already verified.")
    
    existing_otp = db.query(OTP).filter(OTP.email == request.email, OTP.active == True).first()
    if existing_otp and existing_otp.expires_at > datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="An active OTP already exists.")
    
    otp_code = random.randint(100000, 999999)
    expires_at = datetime.utcnow() + timedelta(minutes=OTP_EXPIRE_MINUTES)

    new_otp = OTP(
        email=request.email,
        otp_code=otp_code,
        expires_at=expires_at,
        request_time=datetime.utcnow(),
        active=True
    )

    try:
        db.add(new_otp)
        db.commit()
        return {
            "message": "OTP resent successfully",
            "data": {
                "otp_code": otp_code,  # Don't return this in production
                "expires_in": OTP_EXPIRE_MINUTES * 60
            }
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="OTP resend failed")

def logout_user(token: str, db: Session):
    # Add the token to the blacklist
    blacklisted_token = BlacklistedToken(token=token)
    db.add(blacklisted_token)
    db.commit()
    return {"message": "Logged out successfully"}

def change_user_email(new_email: str, password: str, current_user: User, db: Session) -> dict:
    # Check if the new email is already in use
    if db.query(User).filter(User.email == new_email).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already in use")
    
    # Fetch the user again to get the full password hash if needed
    user = db.query(User).filter(User.id == current_user.id).first()

    # Verify the password with the hash stored in the database
    if not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    # Update the user's email
    user.email = new_email
    db.commit()
    return {"msg": "Email updated successfully"}