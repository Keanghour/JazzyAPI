from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="admin", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)

    # Relationship to logs
    logs = relationship("UserLog", back_populates="user")


class UserLog(Base):
    __tablename__ = "user_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    event = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationship back to User
    user = relationship("User", back_populates="logs")
