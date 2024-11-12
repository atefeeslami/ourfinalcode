from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from booking.database import SessionLocal
from booking.models import Hotel
from pydantic import BaseModel
from typing import Optional
from booking.auth import get_current_user

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()




class HotelCreate(BaseModel):
    name: str
    location: str
    description: Optional[str] = None
    has_wifi: Optional[bool] = True
    price_per_night: float

@router.post("/hotels/")
def create_hotel(hotel: HotelCreate, db: Session = Depends(get_db), user_id: int = Depends(get_current_user)):
    new_hotel = Hotel(
        name=hotel.name,
        location=hotel.location,
        description=hotel.description,
        has_wifi=hotel.has_wifi,
        price_per_night=hotel.price_per_night,
        user_id=user_id  # متصل کردن هتل به مدیر
    )
    db.add(new_hotel)
    db.commit()
    db.refresh(new_hotel)
    return new_hotel

@router.put("/hotels/{hotel_id}")
def update_hotel(hotel_id: int, hotel: HotelCreate, db: Session = Depends(get_db)):
    db_hotel = db.query(Hotel).filter(Hotel.id == hotel_id).first()
    if not db_hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")
    db_hotel.name = hotel.name
    db_hotel.location = hotel.location
    db_hotel.description = hotel.description
    db_hotel.has_wifi = hotel.has_wifi
    db_hotel.price_per_night = hotel.price_per_night
    db.commit()
    db.refresh(db_hotel)
    return db_hotel

#مشاهده اطلاعات هتل

@router.get("/hotels/{hotel_id}")
def get_hotel(hotel_id: int, db: Session = Depends(get_db)):
    db_hotel = db.query(Hotel).filter(Hotel.id == hotel_id).first()
    if not db_hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")
    return db_hotel

#حذف اطلاعات هتل
@router.delete("/hotels/{hotel_id}")
def delete_hotel(hotel_id: int, db: Session = Depends(get_db)):
    db_hotel = db.query(Hotel).filter(Hotel.id == hotel_id).first()
    if not db_hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")
    db.delete(db_hotel)
    db.commit()
    return {"message": "Hotel deleted successfully"}

@router.get("/hotels/my_hotels")
def get_my_hotels(db: Session = Depends(get_db), user_id: int = Depends(get_current_user)):
    hotels = db.query(Hotel).filter(Hotel.user_id == user_id).all()
    return hotels