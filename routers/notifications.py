from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from booking.database import get_db
from booking.models import Notification, User, Booking
from booking.auth import get_current_user
from pydantic import BaseModel
from typing import List

router = APIRouter(
    prefix="/notifications",
    tags=["notifications"]
)

# مدل ایجاد اعلان جدید
class NotificationCreate(BaseModel):
    booking_id: int
    type: str
    message: str

# مدل پاسخ برای اعلان
class NotificationResponse(BaseModel):
    id: int
    booking_id: int
    type: str
    message: str
    read_status: bool

# API برای ایجاد اعلان جدید
@router.post("/", response_model=dict)
def create_notification(notification: NotificationCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    booking = db.query(Booking).filter(Booking.id == notification.booking_id, Booking.user_id == current_user.id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found or not authorized")

    new_notification = Notification(
        user_id=current_user.id,
        booking_id=notification.booking_id,
        type=notification.type,
        message=notification.message,
        read_status=False
    )
    db.add(new_notification)
    db.commit()
    db.refresh(new_notification)
    return {"message": "Notification created successfully"}

# API برای مشاهده اعلان‌های کاربر
@router.get("/", response_model=List[NotificationResponse])
def get_user_notifications(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    notifications = db.query(Notification).filter(Notification.user_id == current_user.id).all()
    return notifications

# API برای علامت‌گذاری اعلان به عنوان خوانده شده
@router.put("/{notification_id}", response_model=dict)
def mark_notification_as_read(notification_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    notification = db.query(Notification).filter(Notification.id == notification_id, Notification.user_id == current_user.id).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    notification.read_status = True
    db.commit()
    return {"message": "Notification marked as read"}

# API برای حذف اعلان
@router.delete("/{notification_id}", response_model=dict)
def delete_notification(notification_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    notification = db.query(Notification).filter(Notification.id == notification_id, Notification.user_id == current_user.id).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    db.delete(notification)
    db.commit()
    return {"message": "Notification deleted successfully"}