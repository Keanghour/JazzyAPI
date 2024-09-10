from datetime import datetime, timedelta
import os
from jose import JWTError, jwt
from typing import Dict, Union

from requests import Session

from app.database.models import OAuth2Client

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token_oauth2(data: Dict[str, str], expires_delta: timedelta = None) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = data.copy()
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_client_credentials(client_id: str, client_secret: str, db: Session) -> bool:
    client = db.query(OAuth2Client).filter(
        OAuth2Client.client_id == client_id,
        OAuth2Client.client_secret == client_secret
    ).first()
    return client is not None
