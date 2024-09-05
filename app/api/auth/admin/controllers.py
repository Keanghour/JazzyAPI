from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.schemas.auth import RegisterRequest, LoginRequest
from app.database.models import User, UserLog
from app.core.security import verify_password, get_password_hash, create_access_token
from datetime import datetime, timedelta

ACCESS_TOKEN_EXPIRE_MINUTES = 60

def register_user(request: RegisterRequest, db: Session):
    try:
        # Validate if the password and password_confirmation match
        if request.password != request.password_confirmation:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match")

        # Check if the email already exists
        existing_user = db.query(User).filter(User.email == request.email).first()
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

        # Hash the password
        hashed_password = get_password_hash(request.password)

        # Create a new user
        new_user = User(
            full_name=request.full_name,
            email=request.email,
            hashed_password=hashed_password,
            role=request.role
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        # Log the registration event
        user_log = UserLog(user_id=new_user.id, event="register")
        db.add(user_log)
        db.commit()

        return {
            "message": "Registration successful",
            "status": 200,
            "data": {
                "message": "Registration successful, please verify your email",
                "timestamp": datetime.utcnow().isoformat(),
                "role": new_user.role
            }
        }
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Registration failed")
    
def login_user(request: LoginRequest, db: Session):
    try:
        # Retrieve user by email
        user = db.query(User).filter(User.email == request.email).first()
        
        # Initialize error messages
        email_error = password_error = None
        
        # Validate email
        if not user:
            email_error = "Email not found."
        
        # Validate password if email exists
        if user and not verify_password(request.password, user.hashed_password):
            password_error = "Incorrect password."

        # If both email and password are wrong, show combined message
        if email_error and password_error:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email and password. Please verify your credentials."
            )

        # If only email is wrong, show email-specific error
        if email_error:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=email_error
            )

        # If only password is wrong, show password-specific error
        if password_error:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=password_error
            )

        # Generate access token if both email and password are correct
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)

        # Log the login event
        user_log = UserLog(user_id=user.id, event="login")
        db.add(user_log)
        db.commit()

        return {
            "message": "Login successful",
            "status": 200,
            "data": {
                "jwt": {
                    "access_token": access_token,
                    "token_type": "bearer",
                    "expires_in": int(ACCESS_TOKEN_EXPIRE_MINUTES * 60)  # in seconds
                }
            }
        }
    except HTTPException as http_exc:
        raise http_exc  # Keep the raised exception intact
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Login failed")
    

