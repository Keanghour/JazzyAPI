from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Retrieve database URL from .env
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./jazzyapi.db")

# Create engine and session
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Session local for each request
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base model class for all database models
Base = declarative_base()

# Dependency to get DB session for routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize database and create tables
def init_db():
    Base.metadata.create_all(bind=engine)
