# app/database/models/otp.py

from sqlalchemy import Boolean, Column, Integer, String, DateTime
from datetime import datetime
from app.database.config import Base

class OTP(Base):
    __tablename__ = "otp"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, nullable=False)
    otp_code = Column(Integer, nullable=False)
    request_time = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    active = Column(Boolean, default=True)
