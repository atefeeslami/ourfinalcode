from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from booking.database import SessionLocal
from booking.models import User
from pydantic import BaseModel
from typing import Optional
from booking.auth import get_current_user

router = APIRouter()



# مدل جدید برای به‌روزرسانی اطلاعات کاربر
class UserUpdate(BaseModel):
    name: Optional[str] = None
    lastname: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    phone_number: Optional[str] = None

# Dependency برای ایجاد session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# مدل Pydantic برای ورودی کاربر
class UserCreate(BaseModel):
    name: str
    lastname: str
    email: str
    password: str
    phone_number: Optional[str] = None

# API برای ایجاد کاربر جدید
@router.post("/users/")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = User(
        name=user.name,
        lastname=user.lastname,
        email=user.email,
        password=user.password,
        phone_number=user.phone_number
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# API برای به‌روزرسانی پروفایل کاربر
@router.put("/users/{user_id}")
def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # به‌روزرسانی فقط فیلدهایی که مقدار دارن
    if user.name is not None:
        db_user.name = user.name
    if user.lastname is not None:
        db_user.lastname = user.lastname
    if user.email is not None:
        db_user.email = user.email
    if user.password is not None:
        db_user.password = user.password
    if user.phone_number is not None:
        db_user.phone_number = user.phone_number

    db.commit()
    db.refresh(db_user)
    return db_user


#مشاهده اطلاعات کاربر
@router.get("/users/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

#حذف اطلاعات کاربر

@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(db_user)
    db.commit()
    return {"message": "User deleted successfully"}