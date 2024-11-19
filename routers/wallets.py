from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from booking.database import get_db
from booking.models import Wallet, User
from booking.auth import get_current_user
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

router = APIRouter(
    prefix="/wallet",
    tags=["wallet"]
)

class WalletResponse(BaseModel):
    points: float  # تغییر نام balance به points
    last_updated: datetime

# API برای مشاهده کیف پول کاربر
@router.get("/", response_model=WalletResponse)
def get_wallet(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    wallet = db.query(Wallet).filter(Wallet.user_id == current_user.id).first()
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    return wallet

# API برای افزایش امتیاز
class AddPointsRequest(BaseModel):
    amount: float

@router.post("/add_points")
def add_points(request: AddPointsRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    wallet = db.query(Wallet).filter(Wallet.user_id == current_user.id).first()
    if not wallet:
        wallet = Wallet(user_id=current_user.id, points=request.amount)  # تغییر balance به points
        db.add(wallet)
    else:
        wallet.points += request.amount  # تغییر balance به points
    wallet.last_updated = datetime.utcnow()
    db.commit()
    db.refresh(wallet)
    return {"message": "Points added successfully", "points": wallet.points}  # تغییر balance به points

# API برای استفاده از امتیاز
class RedeemPointsRequest(BaseModel):
    amount: float

@router.post("/redeem_points")
def redeem_points(request: RedeemPointsRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    wallet = db.query(Wallet).filter(Wallet.user_id == current_user.id).first()
    if not wallet or wallet.points < request.amount:  # تغییر balance به points
        raise HTTPException(status_code=400, detail="Insufficient points")  # تغییر balance به points
    wallet.points -= request.amount  # تغییر balance به points
    wallet.last_updated = datetime.utcnow()
    db.commit()
    db.refresh(wallet)
    return {"message": "Points redeemed successfully", "remaining_points": wallet.points}  # تغییر balance به points