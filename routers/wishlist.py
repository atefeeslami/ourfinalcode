from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from booking.database import get_db
from booking.models import Wishlist, Hotel, User
from booking.auth import get_current_user
from pydantic import BaseModel
from typing import List
from datetime import datetime

router = APIRouter(
    prefix="/wishlist",
    tags=["wishlist"]
)

# مدل پاسخ Wishlist
class WishlistResponse(BaseModel):
    id: int
    hotel_id: int
    added_at: datetime

# API برای افزودن هتل به لیست علاقه‌مندی‌ها
@router.post("/", response_model=dict)
def add_to_wishlist(hotel_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # بررسی وجود هتل
    hotel = db.query(Hotel).filter(Hotel.id == hotel_id).first()
    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")

    # بررسی وجود هتل در لیست علاقه‌مندی‌ها
    wishlist_item = db.query(Wishlist).filter(Wishlist.user_id == current_user.id, Wishlist.hotel_id == hotel_id).first()
    if wishlist_item:
        raise HTTPException(status_code=400, detail="Hotel already in wishlist")

    new_wishlist_item = Wishlist(user_id=current_user.id, hotel_id=hotel_id)
    db.add(new_wishlist_item)
    db.commit()
    db.refresh(new_wishlist_item)
    return {"message": "Hotel added to wishlist"}

# API برای مشاهده لیست علاقه‌مندی‌های کاربر
@router.get("/", response_model=List[WishlistResponse])
def get_wishlist(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    wishlist = db.query(Wishlist).filter(Wishlist.user_id == current_user.id).all()
    return [{"id": item.id, "hotel_id": item.hotel_id, "added_at": item.added_at} for item in wishlist]

# API برای حذف هتل از لیست علاقه‌مندی‌ها
@router.delete("/{hotel_id}", response_model=dict)
def remove_from_wishlist(hotel_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    wishlist_item = db.query(Wishlist).filter(Wishlist.user_id == current_user.id, Wishlist.hotel_id == hotel_id).first()
    if not wishlist_item:
        raise HTTPException(status_code=404, detail="Hotel not found in wishlist")
    
    db.delete(wishlist_item)
    db.commit()
    return {"message": "Hotel removed from wishlist"}