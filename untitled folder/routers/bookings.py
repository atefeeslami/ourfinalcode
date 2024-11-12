from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from booking.database import SessionLocal
from booking.models import Booking
from pydantic import BaseModel
from datetime import date
from booking.auth import get_current_user

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class BookingCreate(BaseModel):
    user_id: int
    hotel_id: int
    check_in_date: date
    check_out_date: date

@router.post("/bookings/")
def create_booking(booking: BookingCreate, db: Session = Depends(get_db)):
    new_booking = Booking(
        user_id=booking.user_id,
        hotel_id=booking.hotel_id,
        check_in_date=booking.check_in_date,
        check_out_date=booking.check_out_date,
    )
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)
    return new_booking