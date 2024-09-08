# # Core authentication logic

# # app/core/security.py

# from fastapi import Depends, HTTPException, status, Header
# from passlib.context import CryptContext
# from jose import JWTError, jwt
# from datetime import datetime, timedelta
# from dotenv import load_dotenv
# import os
# from sqlalchemy.orm import Session
# from fastapi.security import OAuth2PasswordBearer

# from app.database.config import get_db
# from app.database.models import User, BlacklistedToken

# # Load environment variables
# load_dotenv("env/.env")

# # Load JWT settings
# SECRET_KEY = os.getenv("SECRET_KEY")
# ALGORITHM = os.getenv("ALGORITHM", "HS256")
# ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

# # Check for missing environment variables
# if not SECRET_KEY:
#     raise ValueError("SECRET_KEY environment variable is not set")

# # Password hashing configuration
# pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# # Token creation
# def create_access_token(data: dict, expires_delta: timedelta = None):
#     to_encode = data.copy()
#     if expires_delta:
#         expire = datetime.utcnow() + expires_delta
#     else:
#         expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
#     return encoded_jwt


# # Password hashing and verification
# def get_password_hash(password: str) -> str:
#     return pwd_context.hash(password)

# def verify_password(plain_password: str, hashed_password: str) -> bool:
#     return pwd_context.verify(plain_password, hashed_password)


# # Fetch user from token
# def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> User:
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         user_email: str = payload.get("sub")  # Extract email or ID
#         if user_email is None:
#             raise credentials_exception
        
#         # Fetch the user from the database
#         user = db.query(User).filter(User.email == user_email).first()
#         if user is None:
#             raise credentials_exception
#     except JWTError:
#         raise credentials_exception
    
#     return user


# # Token validation and blacklist checking
# def validate_token(authorization: str = Header(None), db: Session = Depends(get_db)):
#     if not authorization:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    
#     token = authorization.split(" ")[1]  # Extract token from 'Bearer <token>'
    
#     if not token:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token format")

#     # Check if the token is blacklisted
#     if is_token_blacklisted(token, db):
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has been invalidated")

#     try:
#         # Decode the JWT token
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         user_email: str = payload.get("sub")  # Extract user's email or ID
#         if not user_email:
#             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
#         return user_email  # Return user email for querying the user
#     except JWTError:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token or expired")


# # Check if token is blacklisted
# def is_token_blacklisted(token: str, db: Session) -> bool:
#     return db.query(BlacklistedToken).filter(BlacklistedToken.token == token).first() is not None
