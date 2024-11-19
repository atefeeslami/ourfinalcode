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
    type: str  # "Urgent", "Reminder", etc.
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
    # فقط ادمین یا هتل منیجر مجاز به ایجاد نوتیفیکیشن هستند
    if current_user.role not in ["admin", "hotel_manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins or hotel managers can create notifications"
        )

    # بررسی اینکه آیا بوکینگ وجود دارد
    booking = db.query(Booking).filter(Booking.id == notification.booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    # هتل منیجر فقط می‌تواند برای بوکینگ‌های مربوط به هتل‌های خودش نوتیفیکیشن ایجاد کند
    if current_user.role == "hotel_manager" and booking.hotel.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to create notifications for this booking"
        )

    new_notification = Notification(
        user_id=booking.user_id,  # اعلان برای کاربری که بوکینگ را انجام داده
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