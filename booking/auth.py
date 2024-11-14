import jwt
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from booking.models import User
from booking.database import get_db
from sqlalchemy.orm import Session
import secrets  # برای تولید کلید تصادفی

# تنظیمات اصلی برای توکن
SECRET_KEY = secrets.token_hex(32)  # استفاده از یک کلید تصادفی و پیچیده
ALGORITHM = "HS256"  # الگوریتم رمزنگاری برای JWT
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # مدت زمان اعتبار توکن در دقیقه

# تنظیم رمزگذاری پسورد
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/tokens")

# توابع کمکی برای هش و تایید پسورد
def get_password_hash(password: str) -> str:
    """هش پسورد را برمی‌گرداند."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """تایید می‌کند که پسورد ورودی با پسورد هش شده برابر است."""
    return pwd_context.verify(plain_password, hashed_password)

# ایجاد توکن JWT
def create_access_token(data: dict) -> str:
    """یک توکن JWT با داده‌های کاربر و زمان انقضا می‌سازد."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})  # اضافه کردن زمان انقضا به توکن
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# وابستگی برای دریافت کاربر فعلی براساس توکن
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """
    کاربر فعلی را براساس توکن دریافتی بازیابی می‌کند.
    اگر توکن معتبر نباشد یا کاربر وجود نداشته باشد، خطا ایجاد می‌کند.
    """
    try:
        # توکن را دیکد می‌کند و اطلاعات آن را دریافت می‌کند
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")  # شناسه کاربر را از توکن دریافت می‌کند
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )