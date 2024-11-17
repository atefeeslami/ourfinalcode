from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from booking.database import get_db
from booking.models import Hotel, User
from booking.schemas import HotelCreate, HotelUpdate, HotelResponse
from booking.auth import get_current_user

router = APIRouter(
    prefix="/hotels",
    tags=["hotels"]
)

# عملیات ایجاد هتل (فقط برای نقش‌های admin و hotel_manager)
@router.post("/", response_model=HotelResponse)
def create_hotel(
    hotel: HotelCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["admin", "hotel_manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    new_hotel = Hotel(
        name=hotel.name,
        location=hotel.location,
        description=hotel.description,
        has_wifi=hotel.has_wifi,
        price_per_night=hotel.price_per_night,
        user_id=current_user.id
    )
    db.add(new_hotel)
    db.commit()
    db.refresh(new_hotel)
    return new_hotel

# مشاهده هتل‌ها
@router.get("/", response_model=List[HotelResponse])
def get_hotels(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role == "admin":
        hotels = db.query(Hotel).all()
    elif current_user.role == "hotel_manager":
        hotels = db.query(Hotel).filter(Hotel.user_id == current_user.id).all()
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    return hotels

# عملیات مشاهده جزئیات یک هتل خاص
@router.get("/{hotel_id}", response_model=HotelResponse)
def get_hotel(hotel_id: int, db: Session = Depends(get_db)):
    hotel = db.query(Hotel).filter(Hotel.id == hotel_id).first()
    if not hotel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hotel not found")
    return hotel

# عملیات به‌روزرسانی اطلاعات هتل (فقط برای نقش‌های admin و hotel_manager)
@router.put("/{hotel_id}", response_model=HotelResponse)
def update_hotel(
    hotel_id: int,
    hotel: HotelUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_hotel = db.query(Hotel).filter(Hotel.id == hotel_id).first()
    if not db_hotel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hotel not found")
    if current_user.role == "admin":
        pass
    elif current_user.role == "hotel_manager" and db_hotel.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to update this hotel"
        )

    db_hotel.name = hotel.name or db_hotel.name
    db_hotel.location = hotel.location or db_hotel.location
    db_hotel.description = hotel.description or db_hotel.description
    db_hotel.has_wifi = hotel.has_wifi if hotel.has_wifi is not None else db_hotel.has_wifi
    db_hotel.price_per_night = hotel.price_per_night or db_hotel.price_per_night

    db.commit()
    db.refresh(db_hotel)
    return db_hotel

# عملیات حذف هتل (فقط برای نقش‌های admin)
@router.delete("/{hotel_id}")
def delete_hotel(
    hotel_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_hotel = db.query(Hotel).filter(Hotel.id == hotel_id).first()
    if not db_hotel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hotel not found")
    if current_user.role == "admin":
        db.delete(db_hotel)
        db.commit()
        return {"message": "Hotel deleted successfully"}
    elif current_user.role == "hotel_manager" and db_hotel.user_id == current_user.id:
        db.delete(db_hotel)
        db.commit()
        return {"message": "Hotel deleted successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and the hotel manager who created the hotel can delete it"
        )
    