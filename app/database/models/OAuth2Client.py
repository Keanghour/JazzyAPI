from sqlalchemy import Column, Integer, String
from app.database.config import Base

class OAuth2Client(Base):
    __tablename__ = 'oauth2_clients'

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(String, unique=True, nullable=False)
    client_secret = Column(String, nullable=False)
    redirect_uris = Column(String, nullable=True)   # Stored as a comma-separated string
