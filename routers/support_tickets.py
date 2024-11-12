from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from booking.database import get_db
from booking.models import SupportTicket, User
from booking.auth import get_current_user
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime  # افزودن این خط برای ایمپورت datetime

router = APIRouter(
    prefix="/support_tickets",
    tags=["support_tickets"]
)

class TicketCreate(BaseModel):
    subject: str
    description: str

class TicketResponse(BaseModel):
    id: int
    subject: str
    description: str
    status: str
    created_at: datetime
    updated_at: datetime

# API برای ایجاد تیکت جدید
@router.post("/", response_model=TicketResponse)
def create_ticket(ticket: TicketCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_ticket = SupportTicket(
        user_id=current_user.id,
        subject=ticket.subject,
        description=ticket.description
    )
    db.add(new_ticket)
    db.commit()
    db.refresh(new_ticket)
    return new_ticket

# API برای مشاهده تیکت‌های کاربر
@router.get("/", response_model=List[TicketResponse])
def get_user_tickets(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    tickets = db.query(SupportTicket).filter(SupportTicket.user_id == current_user.id).all()
    return tickets

# API برای به‌روزرسانی وضعیت تیکت (فقط توسط ادمین‌ها)
@router.put("/{ticket_id}", response_model=TicketResponse)
def update_ticket_status(ticket_id: int, status: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ticket = db.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    # چک کنید که کاربر ادمین باشد (در صورت نیاز)
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to update ticket status")

    ticket.status = status
    db.commit()
    db.refresh(ticket)
    return ticket