# app/database/models/blacklisted_token.py

from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.database.config import Base

class BlacklistedToken(Base):
    __tablename__ = "blacklisted_tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, nullable=False)
    added_at = Column(DateTime, default=datetime.utcnow)
