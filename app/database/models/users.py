# app/database/models/user.py

from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship
from app.database.config import Base

# class User(Base):
#     __tablename__ = "users"

#     id = Column(Integer, primary_key=True, index=True)
#     full_name = Column(String, nullable=False)
#     email = Column(String, unique=True, index=True, nullable=False)
#     hashed_password = Column(String, nullable=False)
#     role = Column(String, default="admin", nullable=False)
#     is_active = Column(Boolean, default=False, nullable=False)
#     is_verified = Column(Boolean, default=False, nullable=False)

#     # Relationship to logs
#     logs = relationship("UserLog", back_populates="user")

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=False)
    role = Column(String)
    refresh_token = Column(String, nullable=True)
    
    # Relationship to logs
    logs = relationship("UserLog", back_populates="user")
