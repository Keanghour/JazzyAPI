# app/api/auth/admin/controllers.py

from datetime import datetime, timedelta
import random
from uuid import uuid4
from sqlalchemy.orm import Session
from fastapi import BackgroundTasks, HTTPException, Header, status
from app.core.email import send_email
from app.core.oauth2 import create_access_token_oauth2
from app.database.models import OTP, OAuth2Client, User, UserLog, UserOAuth2
from app.core.security import create_access_token, create_refresh_token, get_user_from_refresh_token, verify_password, get_password_hash
from app.database.models.blacklisted_token import BlacklistedToken
from app.schemas.auth import OAuth2ClientCreateRequest, RefreshTokenRequest, RegisterRequest, LoginRequest, OTPRequest, OTPResendRequest, OTPVerifyRequest, TokenResponse

OTP_EXPIRE_MINUTES = 1
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def request_token_controller(client_id: str, client_secret: str, db: Session) -> str:
    # Verify client credentials
    client = db.query(OAuth2Client).filter(
        OAuth2Client.client_id == client_id,
        OAuth2Client.client_secret == client_secret
    ).first()

    if not client:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid client credentials")

    # Generate access token
    access_token = create_access_token_oauth2(data={"client_id": client_id})

    return access_token

def register_user_and_client(request: OAuth2ClientCreateRequest, db: Session) -> dict:
    # Register the user
    hashed_password = get_password_hash(request.password)
    db_user = UserOAuth2(
        username=request.username,
        hashed_password=hashed_password
    )
    db.add(db_user)
    
    # Register the OAuth2 client
    client_id = request.client_id
    client_secret = get_password_hash(request.client_secret)
    redirect_uris = ','.join(request.redirect_uris) if request.redirect_uris else ''

    # Check if client ID already exists
    existing_client = db.query(OAuth2Client).filter(OAuth2Client.client_id == client_id).first()
    if existing_client:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Client ID already exists")
    
    new_client = OAuth2Client(client_id=client_id, client_secret=client_secret, redirect_uris=redirect_uris)
    db.add(new_client)
    
    # Commit the transaction for both
    db.commit()
    
    return {
        "message": "User and OAuth2 Client created successfully",
        "status": status.HTTP_201_CREATED,
        "data": {
            "client_id": client_id,
            "username": request.username,
            "redirect_uris": request.redirect_uris
        }
    }

def refresh_token(request: RefreshTokenRequest, db: Session) -> TokenResponse:
    # Retrieve the user based on the refresh token
    user = get_user_from_refresh_token(request.refresh_token, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    # Generate new access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

def validate_token(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    # Implement your token validation logic here (e.g., decode and verify token)
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

def get_current_user_by_token(token: str, db: Session) -> User:
    user_email = validate_token(token)  # Ensure token validation returns user info
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

def register_user(request: RegisterRequest, db: Session, background_tasks: BackgroundTasks):
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

        # Prepare the email content
        email_subject = "Email Verification Code"
        email_body = f"""
        Dear {new_user.full_name},

        Thank you for registering with us. To complete your registration, please verify your email address using the
        One-Time Password (OTP) code provided below:

        OTP Code: {otp_code}
        Expiration Time: {OTP_EXPIRE_MINUTES} minutes

        If you did not request this registration, please disregard this email.

        Best regards,
        JazzyAPI - Hour Zackry
        """

        # Schedule sending the email in the background
        background_tasks.add_task(send_email, new_user.email, email_subject, email_body)

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

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(days=7)  # Refresh token expiry

    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )
    
    refresh_token = create_refresh_token(
        data={"sub": user.email},
        expires_delta=refresh_token_expires
    )

    user.refresh_token = refresh_token
    db.commit()

    return {
        "message": "Login successful",
        "status": status.HTTP_200_OK,
        "data": {
            "jwt": {
                "access_token": access_token,
                "token_type": "bearer",
                "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
            },
            "refresh_token": refresh_token
        }
    }

def request_otp(request, db: Session, background_tasks: BackgroundTasks):
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

        # Prepare email content
        email_subject = "Your OTP Code for Email Verification"
        email_body = f"""
        Dear {user.full_name},

        You have requested an OTP for verifying your email address. Please use the code below to complete your verification:

        OTP Code: {otp_code}
        Expiration Time: {OTP_EXPIRE_MINUTES} minutes

        Best regards,
        Your Team
        """

        # Send email in the background
        background_tasks.add_task(send_email, user.email, email_subject, email_body)

        return {
            "message": "OTP requested successfully",
            "data": {
                "otp_code": otp_code,  # Do not return OTP in production
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

def resend_otp(request, db: Session, background_tasks: BackgroundTasks):
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

        # Prepare email content
        email_subject = "Resend OTP Code"
        email_body = f"""
        Dear {user.full_name},

        You have requested a new OTP for email verification. Please use the following OTP code:

        OTP Code: {otp_code}
        Expiration Time: {OTP_EXPIRE_MINUTES} minutes

        Best regards,
        Your Team
        """

        # Send email in the background
        background_tasks.add_task(send_email, user.email, email_subject, email_body)

        return {
            "message": "OTP resent successfully",
            "data": {
                "otp_code": otp_code,  # Do not return OTP in production
                "expires_in": OTP_EXPIRE_MINUTES * 60
            }
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="OTP resend failed")
    
def logout_user(token: str, db: Session):
    user = db.query(User).filter(User.refresh_token == token).first()
    if user:
        user.refresh_token = None
        db.commit()

    blacklisted_token = BlacklistedToken(token=token)
    db.add(blacklisted_token)
    db.commit()
    return {"message": "Logged out successfully"}

def change_user_email(new_email: str, password: str, current_user: User, db: Session) -> dict:
    if db.query(User).filter(User.email == new_email).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already in use")
    
    user = db.query(User).filter(User.id == current_user.id).first()
    if not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    user.email = new_email
    db.commit()
    return {"message": "Email changed successfully"}

def forgot_password_controller(email: str, db: Session, background_tasks: BackgroundTasks):
    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User with this email does not exist")

    # Generate password reset token (UUID)
    reset_token = str(uuid4())

    # Create expiration time (e.g., 10 minutes)
    expires_at = datetime.utcnow() + timedelta(minutes=10)

    # Store the reset token in OTP table
    otp = OTP(
        email=email,
        otp_code=reset_token,
        request_time=datetime.utcnow(),
        expires_at=expires_at,
        active=True
    )
    db.add(otp)
    db.commit()

    # Prepare email content
    email_subject = "Password Reset Request"
    email_body = f"""
    Dear {user.full_name},

    We received a request to reset your password. Please use the following link to reset your password:

    Reset Token: {reset_token}
    Expiration Time: 10 minutes

    If you did not request this password reset, please ignore this email.

    Best regards,
    Your Team
    """

    # Send email in the background
    background_tasks.add_task(send_email, user.email, email_subject, email_body)

    # Return response
    return {
        "message": "Please check your email, reset link has been sent.",
        "status": 200,
        "data": {
            "password_token": reset_token,  # In production, this should be sent via email
            "expires_in": 10,  # 10 minutes validity
        }
    }

def reset_password_controller(password: str, password_confirmation: str, password_token: str, db: Session):
    # Check if passwords match
    if password != password_confirmation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )

    # Look up the reset token in OTP table
    token_entry = db.query(OTP).filter(OTP.otp_code == password_token, OTP.active == True).first()

    if not token_entry or token_entry.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token"
        )

    # Look up the user based on email
    user = db.query(User).filter(User.email == token_entry.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Hash the new password
    user.hashed_password = get_password_hash(password)

    # Deactivate the token (so it can't be reused)
    token_entry.active = False

    # Save changes to the database
    db.commit()

    return {"message": "Password reset successfully."}

    