from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date, datetime
from booking.database import get_db
from booking.models import Booking, Hotel, User, Wallet
from booking.auth import get_current_user
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(
    prefix="/bookings",
    tags=["bookings"]
)

# مدل رزرو جدید
class BookingCreate(BaseModel):
    hotel_id: int
    check_in_date: date
    check_out_date: date


class BookingResponse(BaseModel):
    id: int
    user_id: int
    hotel_id: int
    check_in_date: date
    check_out_date: date
    status: str

    class Config:
        from_attributes = True
# مدل به‌روزرسانی رزرو
class BookingUpdate(BaseModel):
    check_in_date: Optional[date] = None
    check_out_date: Optional[date] = None
    status: Optional[str] = None  # امکان تغییر وضعیت رزرو

@router.post("/", response_model=BookingResponse)
def create_booking(booking: BookingCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # بررسی اینکه تاریخ چک این از تاریخ چک اوت کوچکتر باشد
    if booking.check_in_date >= booking.check_out_date:
        raise HTTPException(status_code=400, detail="Check-in date must be earlier than check-out date")

    hotel = db.query(Hotel).filter(Hotel.id == booking.hotel_id).first()
    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")

    # بررسی رزرو هم‌پوشان
    overlap_booking = db.query(Booking).filter(
        Booking.hotel_id == booking.hotel_id,
        Booking.check_in_date < booking.check_out_date,
        Booking.check_out_date > booking.check_in_date
    ).first()
    if overlap_booking:
        raise HTTPException(status_code=400, detail="Booking dates overlap with an existing booking")

    new_booking = Booking(
        user_id=current_user.id,
        hotel_id=booking.hotel_id,
        check_in_date=booking.check_in_date,
        check_out_date=booking.check_out_date,
        status="Pending"
    )
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)

    # اضافه کردن موجودی پس از ایجاد رزرو
    wallet = db.query(Wallet).filter(Wallet.user_id == current_user.id).first()
    if wallet:
        wallet.points += 10
        wallet.last_updated = datetime.utcnow()
    else:
        wallet = Wallet(user_id=current_user.id, points=10)
        db.add(wallet)
    db.commit()
    db.refresh(wallet)

    return new_booking
# API برای مشاهده رزروهای کاربر
@router.get("/", response_model=List[dict])
def get_user_bookings(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # ادمین تمام رزروها را می‌بیند
    if current_user.role == "admin":
        bookings = db.query(Booking).all()
    # هتل منیجر فقط رزروهای مربوط به هتل‌های خود را می‌بیند
    elif current_user.role == "hotel_manager":
        bookings = db.query(Booking).join(Hotel).filter(Hotel.user_id == current_user.id).all()
    # کاربر معمولی فقط رزروهای خود را می‌بیند
    else:
        bookings = db.query(Booking).filter(Booking.user_id == current_user.id).all()

    return [{"id": booking.id, "hotel_id": booking.hotel_id, "check_in_date": booking.check_in_date, "check_out_date": booking.check_out_date, "status": booking.status} for booking in bookings]

# API برای به‌روزرسانی رزرو
@router.put("/{booking_id}", response_model=dict)
def update_booking(booking_id: int, booking: BookingUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not db_booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    # محدودیت دسترسی‌ها بر اساس نقش کاربر
    if current_user.role == "user" and db_booking.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    elif current_user.role == "hotel_manager":
        hotel = db.query(Hotel).filter(Hotel.id == db_booking.hotel_id, Hotel.user_id == current_user.id).first()
        if not hotel:
            raise HTTPException(status_code=403, detail="Access denied")
    # ادمین نیازی به بررسی دسترسی خاص ندارد

    # به‌روزرسانی اطلاعات رزرو
    if booking.check_in_date:
        db_booking.check_in_date = booking.check_in_date
    if booking.check_out_date:
        db_booking.check_out_date = booking.check_out_date
    if booking.status and current_user.role in ["admin", "hotel_manager"]:
        db_booking.status = booking.status  # تغییر وضعیت رزرو توسط ادمین یا هتل منیجر

    db.commit()
    db.refresh(db_booking)
    return {"message": "Booking updated successfully"}

# API برای لغو رزرو
@router.delete("/{booking_id}", response_model=dict)
def cancel_booking(booking_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not db_booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    # محدودیت دسترسی‌ها بر اساس نقش کاربر
    if current_user.role == "user" and db_booking.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    elif current_user.role == "hotel_manager":
        hotel = db.query(Hotel).filter(Hotel.id == db_booking.hotel_id, Hotel.user_id == current_user.id).first()
        if not hotel:
            raise HTTPException(status_code=403, detail="Access denied")
    # ادمین نیازی به بررسی دسترسی خاص ندارد

    db_booking.status = "Cancelled"
    db.commit()
    return {"message": "Booking cancelled successfully"}