from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.models import User
from app.schemas.auth import RegisterRequest, RegisterResponse, LoginRequest, LoginResponse, UserResponse
from app.database.database import get_db
from app.api.auth.admin.controllers import register_user, login_user

router = APIRouter()

@router.get("/users", response_model=List[UserResponse])
def get_all_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users

@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/register", response_model=RegisterResponse)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    return register_user(request, db)

@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    return login_user(request, db)
