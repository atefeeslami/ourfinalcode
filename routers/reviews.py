from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from booking.database import get_db
from booking.models import Review, User
from booking.auth import get_current_user
from pydantic import BaseModel, Field
from typing import List, Optional

router = APIRouter(
    prefix="/reviews",
    tags=["reviews"]
)

class ReviewCreate(BaseModel):
    hotel_id: int
    rating: int
    comment: Optional[str] = None

class ReviewResponse(BaseModel):
    id: int
    hotel_id: int
    user_id: int
    rating: int
    comment: Optional[str] = None

    class Config:
        from_attributes = True  # تنظیم برای تبدیل از ORM

# API برای افزودن نظر جدید
@router.post("/", response_model=ReviewResponse)
def create_review(review: ReviewCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_review = Review(
        user_id=current_user.id,
        hotel_id=review.hotel_id,
        rating=review.rating,
        comment=review.comment
    )
    db.add(new_review)
    db.commit()
    db.refresh(new_review)
    return new_review

# API برای دریافت نظرات یک هتل
@router.get("/{hotel_id}", response_model=List[ReviewResponse])
def get_reviews(hotel_id: int, db: Session = Depends(get_db)):
    reviews = db.query(Review).filter(Review.hotel_id == hotel_id).all()
    if not reviews:
        raise HTTPException(status_code=404, detail="No reviews found for this hotel")
    return reviews

# API برای حذف نظر
@router.delete("/{review_id}")
def delete_review(review_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    review = db.query(Review).filter(Review.id == review_id, Review.user_id == current_user.id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found or you don't have permission to delete it")
    db.delete(review)
    db.commit()
    return {"message": "Review deleted successfully"}