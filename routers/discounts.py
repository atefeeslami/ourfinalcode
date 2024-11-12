from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from booking.database import get_db
from booking.models import User, Booking, Discount, BookingDiscount
from booking.auth import get_current_user
from pydantic import BaseModel
from datetime import date
from typing import List, Optional

router = APIRouter(
    prefix="/discounts",
    tags=["discounts"]
)

class DiscountCreate(BaseModel):
    code: str
    description: Optional[str] = None
    discount_percentage: float
    valid_from: date
    valid_until: date

class DiscountResponse(BaseModel):
    id: int
    code: str
    description: Optional[str] = None
    discount_percentage: float
    valid_from: date
    valid_until: date

# API برای ایجاد تخفیف جدید
@router.post("/", response_model=DiscountResponse)
def create_discount(discount: DiscountCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can create discounts")
    
    new_discount = Discount(
        code=discount.code,
        description=discount.description,
        discount_percentage=discount.discount_percentage,
        valid_from=discount.valid_from,
        valid_until=discount.valid_until
    )
    db.add(new_discount)
    db.commit()
    db.refresh(new_discount)
    return new_discount

# API برای مشاهده تمام تخفیف‌ها
@router.get("/", response_model=List[DiscountResponse])
def get_discounts(db: Session = Depends(get_db)):
    discounts = db.query(Discount).all()
    return discounts

# API برای اعمال تخفیف به رزرو
@router.post("/apply/{booking_id}")
def apply_discount(booking_id: int, discount_code: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    booking = db.query(Booking).filter(Booking.id == booking_id, Booking.user_id == current_user.id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found or you don't have permission")
    
    discount = db.query(Discount).filter(Discount.code == discount_code).first()
    if not discount:
        raise HTTPException(status_code=404, detail="Discount code not found")
    
    # چک کردن تاریخ اعتبار تخفیف
    if discount.valid_from > date.today() or discount.valid_until < date.today():
        raise HTTPException(status_code=400, detail="Discount code is expired or not yet valid")
    
    booking_discount = BookingDiscount(
        booking_id=booking.id,
        discount_id=discount.id
    )
    db.add(booking_discount)
    db.commit()
    return {"message": "Discount applied successfully"}