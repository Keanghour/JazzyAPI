# app/scripts/setup_oauth_clients.py

from sqlalchemy.orm import Session
from app.core.security import get_password_hash
from app.database.config import SessionLocal
from app.database.models import OAuth2Client


def create_oauth_client(db: Session):
    client_id = "my-client-id"
    client_secret = get_password_hash("my-client-secret")  # Hash the secret if needed
    redirect_uris = '["http://localhost/callback"]'  # JSON string format

    new_client = OAuth2Client(client_id=client_id, client_secret=client_secret, redirect_uris=redirect_uris)
    db.add(new_client)
    db.commit()
    print("OAuth2 Client created successfully")

if __name__ == "__main__":
    db = SessionLocal()
    create_oauth_client(db)
