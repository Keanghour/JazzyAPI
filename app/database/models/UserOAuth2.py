from sqlalchemy import Column, Integer, String
from app.database.config import Base

class UserOAuth2(Base):
    __tablename__ = 'users_oauth2'
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)