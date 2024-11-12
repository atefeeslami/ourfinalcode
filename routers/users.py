from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from booking.database import get_db
from booking.models import User
from booking.auth import create_access_token, get_password_hash, verify_password, get_current_user
from pydantic import BaseModel
from typing import Optional

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

# Pydantic model for user registration and login
class UserRegister(BaseModel):
    name: str
    lastname: str
    email: str
    password: str
    phone_number: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

# User registration route
@router.post("/register")
def register_user(user: UserRegister, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = get_password_hash(user.password)
    new_user = User(
        name=user.name,
        lastname=user.lastname,
        email=user.email,
        password=hashed_password,
        phone_number=user.phone_number
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    access_token = create_access_token(data={"sub": new_user.id})
    return {"message": "User registered successfully", "access_token": access_token, "token_type": "bearer"}

# User login route
@router.post("/login")
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    access_token = create_access_token(data={"sub": db_user.id})
    return {"access_token": access_token, "token_type": "bearer"}

# CRUD operations for user profile, requiring authentication
@router.get("/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}")
def update_user(user_id: int, user: UserRegister, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db_user.name = user.name or db_user.name
    db_user.lastname = user.lastname or db_user.lastname
    db_user.email = user.email or db_user.email
    if user.password:
        db_user.password = get_password_hash(user.password)
    db_user.phone_number = user.phone_number or db_user.phone_number
    db.commit()
    db.refresh(db_user)
    return db_user

@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(db_user)
    db.commit()
    return {"message": "User deleted successfully"}
