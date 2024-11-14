from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from booking.auth import create_access_token, verify_password
from booking.models import User
from booking.database import get_db
from sqlalchemy.orm import Session
from pydantic import BaseModel

# تعریف مدل برای داده‌های ورودی توکن
class TokenData(BaseModel):
    username: str
    password: str

# ایجاد روتر
router = APIRouter()

@router.post("/tokens")
def login_for_access_token(request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.username).first()
    if not user or not verify_password(request.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user.id})
    return {"access_token": access_token, "token_type": "bearer"}

