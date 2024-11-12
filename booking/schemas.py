from pydantic import BaseModel
from typing import Optional
from datetime import date

# مدل User برای ایجاد کاربر جدید
class UserCreate(BaseModel):
    name: str
    lastname: str
    email: str
    password: str
    phone_number: Optional[str] = None

# مدل User برای به‌روزرسانی اطلاعات کاربر
class UserUpdate(BaseModel):
    name: Optional[str] = None
    lastname: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    phone_number: Optional[str] = None

# مدل User برای نمایش خروجی
class UserResponse(BaseModel):
    id: int
    name: str
    lastname: str
    email: str
    phone_number: Optional[str] = None

    class Config:
        orm_mode = True

# مدل Hotel برای ایجاد هتل جدید
class HotelCreate(BaseModel):
    name: str
    location: str
    description: Optional[str] = None
    has_wifi: Optional[bool] = True
    price_per_night: float

# مدل Hotel برای به‌روزرسانی هتل
class HotelUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    has_wifi: Optional[bool] = True
    price_per_night: Optional[float] = None

# مدل Hotel برای نمایش خروجی
class HotelResponse(BaseModel):
    id: int
    name: str
    location: str
    description: Optional[str] = None
    has_wifi: bool
    price_per_night: float

    class Config:
        orm_mode = True

# مدل Booking برای ایجاد بوکینگ جدید
class BookingCreate(BaseModel):
    hotel_id: int
    check_in_date: date
    check_out_date: date

# مدل Booking برای به‌روزرسانی بوکینگ
class BookingUpdate(BaseModel):
    check_in_date: Optional[date] = None
    check_out_date: Optional[date] = None
    status: Optional[str] = None

# مدل Booking برای نمایش خروجی
class BookingResponse(BaseModel):
    id: int
    user_id: int
    hotel_id: int
    check_in_date: date
    check_out_date: date
    status: str

    class Config:
        orm_mode = True